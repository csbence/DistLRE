![distlre PyPI Downloads](https://pypistats.com/badge/distlre.png)

# DistLRE (dist-el-ar-ee)

A lightweight Python package to distribute commands on remote hosts via SSH and to execute them locally in parallel.

Supports running a local commands:

```python
from distlre.distlre import DistLRE, Task, RemoteHost
executor = DistLRE(local_threads=1)

task = Task(command='ls ~', meta='META', time_limit=10, memory_limit=10)
future = executor.submit(task)
executor.execute_tasks()
executor.wait()
print(future.result().output)
```

Or runs command on a remote host:

```python
import getpass
password = getpass.getpass("Password to connect to [localhost]:")
executor = DistLRE(remote_hosts=[RemoteHost('localhost', port=31415, password=password)])

task = Task(command='ls ~', meta='META', time_limit=10, memory_limit=10)
other_task = Task(command='cd ~', meta='META', time_limit=10, memory_limit=10)
future = executor.submit(task)
other_future = executor.submit(other_task)
executor.execute_tasks()
executor.wait()
print(future.result().output)
```

# Install

`pip3 install DistLRE`
