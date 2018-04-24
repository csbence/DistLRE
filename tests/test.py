
def test():
    distlre = DistLRE()

    task = Task()
    future = distlre.submit(task)
    future.result()