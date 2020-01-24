from distlre.distlre import DistLRE, Task, RemoteHost
import unittest


class TestLocalExecutor(unittest.TestCase):
    def test_local(self):
        executor = DistLRE(local_threads=1)

        task = Task(command='~/CLionProjects/search/cmake-build-release/search wastar unit_tiles 1.2 1',
                    meta='META', time_limit=10, memory_limit=10)
        future = executor.submit(task)
        executor.execute_tasks()
        executor.wait()
        print(future.result().output)


class TestRemoteExecutor(unittest.TestCase):
    def test_remote(self):
        executor = DistLRE(remote_hosts=[RemoteHost('localhost', port=31415, password=None)])

        task = Task(command='ls ~', meta='META', time_limit=10, memory_limit=10)
        future = executor.submit(task)
        executor.execute_tasks()
        executor.wait()
        print(future.result().output)


if __name__ == '__main__':
    unittest.main()
