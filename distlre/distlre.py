from concurrent.futures import Future
from queue import Queue
from multiprocessing import Lock


class Task:
    def __init__(self, command, meta, time_limit, memory_limit):
        self.meta = meta
        self.command = command
        self.input = None
        self.output = None
        self.error = None
        self.time_limit = time_limit
        self.memory_limit = memory_limit


class InternalTask:
    def __init__(self, task):
        self.task = task
        self.future = Future()


class RemoteHost:
    def __init__(self, hostname, port=22, username=None, password=None, key_file_path=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_file_path = key_file_path


class DistLRE:
    def __init__(self, local_threads=0, remote_hosts=None):
        if remote_hosts is None:
            remote_hosts = []
        self.local_threads = local_threads
        self.remote_hosts = remote_hosts
        self.task_queue = Queue()
        self.local_executor = None
        self.remote_executor = None

        if local_threads != 0:
            from distlre.localexecutor import LocalExecutor
            self.local_executor = LocalExecutor(self.task_queue, local_threads)

        if remote_hosts:
            from distlre.remoteexecutor import RemoteExecutor
            self.remote_executor = RemoteExecutor(self.task_queue, remote_hosts)

    def submit(self, task):
        internal_task = InternalTask(task)

        self.task_queue.put(internal_task)

        return internal_task.future

    def execute_tasks(self):
        if self.local_executor:
            self.local_executor.start()

        if self.remote_executor is not None:
            self.remote_executor.start()

    def wait(self):
        if self.local_executor is not None:
            self.local_executor.wait()

        if self.remote_executor is not None:
            self.remote_executor.wait()
