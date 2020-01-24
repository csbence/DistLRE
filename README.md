# DistLRE (dist-el-ar-ee)

[![Downloads](https://pepy.tech/badge/distlre)](https://pepy.tech/project/distlre)

A lightweight Python package to distribute commands on remote hosts via SSH and to execute them locally in parallel.

Runs a parallel process for each task to monitor system resources effectively.

Supports running a local commands, time limit is expressed in seconds and memory limit is in GB:

```python
from distlre.distlre import DistLRE, Task, RemoteHost
executor = DistLRE(local_threads=1)

task = Task(command='ls ~', meta='META', time_limit=10, memory_limit=10)
future = executor.submit(task)
executor.execute_tasks()
executor.wait()
print(future.result().output)
```

Or runs command on a remote host, done over ssh and requires a user-specified method of reporting memory usage.

A simple memory reporter can be made using the `psutil` package and adding the script to your `/usr/bin` in order for it to be executed.

For example if we created a file called `getpsutil` (make sure to have `psutil` installed to your default Python env or specify the correct one for your usage at the top:

```python
#! /usr/bin/env python

import psutil

if __name__ == '__main__':
    print(psutil.virtual_memory().used)
```

Now we can use this simple script when accessing your remote machine (make sure you have added the host to remote hosts and you have key log-in over ssh enabled) to report its memory usage, and track it during task execution:

```python
executor = DistLRE(remote_hosts=[RemoteHost('localhost', 
                                            mem_check='source ~/.bashrc && getpsutil',
                                            port=22)])

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
