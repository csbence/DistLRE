from queue import Empty
from threading import Thread

import paramiko
from os import path


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
        client = spawn_ssh_client(self.host)
        while True:
            try:
                internal_task = self.task_queue.get(block=False)
            except Empty:
                break

            execute_remote_task(client, internal_task)


def execute_remote_task(client, internal_task):
    task = internal_task.task
    internal_task.future.set_running_or_notify_cancel()

    try:
        stdin, stdout, stderr = client.exec_command(task.command)

        if task.input:
            stdin.write(task.input)
            stdin.flush()

        task.output = ''.join(stdout.readlines())
        task.error = ''.join(stderr.readlines())

        internal_task.future.set_result(task)
    except Exception as e:
        internal_task.future.set_exception(e)


def spawn_ssh_client(host):
    key = None

    if host.key_file_path:
        key = paramiko.RSAKey.from_private_key_file(path.expanduser(host.key_file_path))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname=host.hostname,
                   password=host.password,
                   username=host.username,
                   port=host.port,
                   pkey=key)

    return client
