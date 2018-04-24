from distlre.distlre import DistLRE, Task, RemoteHost
import unittest
import getpass


class TestLocalExecutor(unittest.TestCase):
    def test_local(self):
        executor = DistLRE(local_threads=1)

        task = Task(command='ls ~', meta='META', time_limit=10, memory_limit=10)
        future = executor.submit(task)
        executor.execute_tasks()
        executor.wait()
        print(future.result().output)


class TestRemoteExecutor(unittest.TestCase):
    def test_remote(self):
        password = getpass.getpass("Password to connect to [localhost]:")
        executor = DistLRE(remote_hosts=[RemoteHost('localhost', port=31415, password=password)])

        task = Task(command='ls ~', meta='META', time_limit=10, memory_limit=10)
        future = executor.submit(task)
        executor.execute_tasks()
        executor.wait()
        print(future.result().output)


if __name__ == '__main__':
    unittest.main()
