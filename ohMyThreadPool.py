import time
import threading

plock = threading.Lock()
pprint = print


def print(*args, **kwargs):
    plock.acquire()
    pprint(*args, **kwargs)
    plock.release()


class ohMyThreadPool(object):
    def _pool_inner_worker(self, tid):
        while True:
            # always looping, waiting for task
            task = self._tasks.get()

            # do real world work here
            func = task['func']
            args = task['args']
            print(f"_pool_inner_worker No.{tid} is working on task {args}...")
            res = func(*args)

            self._lock.acquire()
            self._results.append(res)
            self._lock.release()

            self._tasks.task_done()

    def __init__(self, max_workers=5):
        import queue
        self._max_workers = max_workers
        self._lock = threading.Lock()
        self._tasks = queue.Queue()
        self._thrs = list()
        self._results = list()

    def submit(self, func, *args):
        self._tasks.put(dict(
            func=func,
            args=args,
        ))

        # lazy creation
        if len(self._thrs) < self._max_workers:
            tid = len(self._thrs)
            t = threading.Thread(target=self._pool_inner_worker, args=(tid,))
            t.daemon = True
            self._thrs.append(t)
            t.start()

    def result(self):
        self._tasks.join()
        return self._results

    def clean(self):
        self._lock.acquire()
        self._results = list()
        self._lock.release()


def real_world_worker(idx, *args, **kwargs):
    time.sleep(0.1)
    return idx

def main():
    omtp = ohMyThreadPool(max_workers=5)

    for i, _ in enumerate(range(20), 1):
        omtp.submit(real_world_worker, i, 'real')
    result = omtp.result()
    print(result)

    omtp.clean()
    for i, _ in enumerate(range(20), 1):
        omtp.submit(real_world_worker, i, 'world')
    result = omtp.result()
    print(result)

if __name__ == '__main__':
    main()

# from concurrent.futures import ThreadPoolExecutor
# pool = ThreadPoolExecutor(max_workers=5)
