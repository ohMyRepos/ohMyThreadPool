import time
import threading

plock = threading.Lock()
pprint = print

def print(*args, **kwargs):
    plock.acquire()
    pprint(*args, **kwargs)
    plock.release()


class ThreadPool(object):
    def _pool_inner_worker(self, tid):
        while True:
            # always loop, waiting for task
            while not self._tasks.empty():
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
        for i in range(self._max_workers):
            t = threading.Thread(target=self._pool_inner_worker, args=(i,))
            t.daemon = True
            self._thrs.append(t)

        # start to roll
        [t.start() for t in self._thrs]

    def submit(self, func, *args):
        self._tasks.put(dict(
            func=func,
            args=args,
        ))

    def result(self):
        self._tasks.join()
        return self._results

    def clean(self):
        self._lock.acquire()
        self._results = list()
        self._lock.release()


def real_world_worker(idx, *args, **kwargs):
    time.sleep(1)
    return idx

def main():
    tp = ThreadPool(max_workers=5)

    for i, _ in enumerate(range(20), 1):
        tp.submit(real_world_worker, i, 'real')
    result = tp.result()
    print(result)

    tp.clean()
    for i, _ in enumerate(range(20), 1):
        tp.submit(real_world_worker, i, 'world')
    result = tp.result()
    print(result)

if __name__ == '__main__':
    main()