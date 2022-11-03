from collections import deque
from concurrent.futures import ThreadPoolExecutor
from random import random
from threading import Thread, Lock
from time import time, sleep


class TradeSource:

    def __init__(self, initial=0, maxdepth=60*60, name='default'):
        self.name = name

        self._mutex = Lock()
        self._tick = 0
        self._price = initial
        self._history = deque([(self._tick, self._price)], maxlen=maxdepth)

    def get_price(self):
        with self._mutex:
            return self._price

    def get_point(self):
        with self._mutex:
            return (self._tick, self._price)

    def get_history(self):
        with self._mutex:
            return list(self._history)

    def update(self):
        with self._mutex:
            change = -1 if random() < 0.5 else 1
            self._tick += 1
            self._price += change
            self._history.append((self._tick, self._price))


class TradeSourceService:

    def __init__(self, total=100, interval=1):
        self.total = total
        self.interval = interval
        self.shutdown = False

        width = 0
        while total > 0:
            total //= 10
            width += 1

        self.sources = {
            idx: TradeSource(name=f'ticker_{idx:0{width}}')
            for idx in range(self.total)
        }

        self._thread = None

    def get_indices(self):
        return list(self.sources.keys())

    def get_names(self):
        return [t.name for t in self.sources.values()]

    def get_index(self, name):
        [index] = [idx for idx, ts in self.sources.items() if ts.name == name]
        return index

    def get_name(self, index):
        return self.sources[index].name

    def get_price(self, index):
        return self.sources[index].get_price()

    def get_point(self, index):
        return self.sources[index].get_point()

    def get_history(self, index):
        return self.sources[index].get_history()

    def start(self):
        if self._thread is not None:
            return

        def _run():
            last = time()
            while True:
                if self.shutdown:
                    return

                current = time()
                if current - last < self.interval:
                    sleep(self.interval / self.total)
                    continue

                with ThreadPoolExecutor(max_workers=self.total) as executor:
                    executor.map(lambda x: x.update(), self.sources.values())
                last = current

        self.shutdown = False
        self._thread = Thread(target=_run)
        self._thread.start()

    def stop(self):
        self.shutdown = True
        sleep(self.interval)

        self._thread.join()
        self._thread = None
