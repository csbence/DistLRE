from queue import Empty
from threading import Thread
from subprocess import Popen, PIPE, run

import time


class RemoteExecutor:
    def __init__(self, task_queue, hosts):
        self.task_queue = task_queue
        self.hosts = hosts
        self.workers = None
        self.initialize_workers()

    def initialize_workers(self):
        self.workers = [SshWorker(host, self.task_queue) for host in self.hosts]

    def start(self):
        for worker in self.workers:
            worker.start()

    def wait(self):
        for worker in self.workers:
            worker.join()


class SshWorker(Thread):
    def __init__(self, host, task_queue):
        super(SshWorker, self).__init__()
        self.task_queue = task_queue
        self.host = host

    def run(self):
        while True:
            try:
                internal_task = self.task_queue.get(block=False)
            except Empty:
                break

            execute_remote_task(self.host, internal_task)


def execute_remote_task(host, internal_task):
    task = internal_task.task
    internal_task.future.set_running_or_notify_cancel()

    task_memory_limit = 7 * 1024 * 1024 * 1024  # 7 GB
    if task.memory_limit is not None:
        task_memory_limit = task.memory_limit * 1024 * 1024 * 1024

    try:
        start = time.time()

        auth = host.username + "@" + host.hostname + " -p " + host.port

        process = Popen("exec ssh " + auth + " " + task.command,
                        stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

        if task.input is not None:
            process.stdin.write(task.input)

        while process.poll() is None:
            mem_proc = Popen("exec ssh " + auth + " python ./getpsutil.py",
                             stdout=PIPE, shell=True)
            mem_proc.wait()

            mem_used = int(mem_proc.stdout.readline())
            mem_proc.stdout.close()
            if mem_used >= task_memory_limit:
                internal_task.task.output = "OutOfMemory exceeded max_bytes: " + str(mem_used)
                process.terminate()
                process.kill()
            if (time.time() - start) > task.time_limit:
                internal_task.task.output = "OutOfTime exceeded time_limit: " + str(task.time_limit)
                process.terminate()
                process.kill()

        process.wait()

        if process.returncode == 0:
            task.output = b''.join(process.stdout.readlines())

        task.error = b''.join(process.stderr.readlines())

        internal_task.future.set_result(task)

        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
    except Exception as e:
        internal_task.future.set_exception(e)
