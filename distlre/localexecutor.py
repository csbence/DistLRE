from queue import Empty
from subprocess import run, PIPE
from threading import Thread
from resource import setrlimit, RLIMIT_AS, getrlimit


class LocalExecutor:
    def __init__(self, task_queue, thread_count):
        self.task_queue = task_queue
        self.thread_count = thread_count
        self.workers = None
        self.initialize_workers()

    def initialize_workers(self):
        self.workers = [LocalWorker(self.task_queue) for _ in range(self.thread_count)]

    def start(self):
        for worker in self.workers:
            worker.start()

    def wait(self):
        for worker in self.workers:
            worker.join()


class LocalWorker(Thread):
    def __init__(self, task_queue):
        super(LocalWorker, self).__init__()
        self.task_queue = task_queue

    def run(self):
        while True:
            try:
                internal_task = self.task_queue.get(block=False)
                execute_task(internal_task)
            except Empty:
                break


def execute_task(internal_task):
    task = internal_task.task
    internal_task.future.set_running_or_notify_cancel()
    task_memory_limit = 7 * 1024 * 1024 * 1024  # 7 GB
    if task.memory_limit is not None:
        task_memory_limit = task.memory_limit * 1024 * 1024 * 1024

    try:
        setrlimit(RLIMIT_AS, (task_memory_limit, task_memory_limit))
        print(getrlimit(RLIMIT_AS))
        completed_process = run([task.command], input=task.input, stdout=PIPE, stderr=PIPE,
                                timeout=task.time_limit, shell=True)
        task.output = completed_process.stdout.decode('utf-8')
        task.error = completed_process.stderr.decode('utf-8')

        internal_task.future.set_result(task)
    except Exception as e:
        internal_task.future.set_exception(e)
