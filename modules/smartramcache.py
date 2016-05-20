import heapq
import time


class SmartRamCache(object):
    times = []
    storage = {}

    def __init__(self, cache_size=1000):
        self.cache_size = cache_size

    def clear(self):
        self.times[:] = []
        self.storage.clear()

    def get(self, key, func=lambda: None, force=False):
        if not force and key in self.storage:
            value = self.storage[key]
        else:
            value = func()
            self.storage[key] = value
            self.times.append((time.time(), key))
            self.times.sort(reverse=True)
            if len(self.times) > self.cache_size:
                (t, oldkey) = self.times.pop()
                if key != oldkey:
                    del self.storage[oldkey]
        return value


def checkit():
    import random
    cache = SmartRamCache(3)
    for k in range(20):
        key = random.choice(['a', 'b', 'c', 'd', 'e'])
        print k, key, cache.get(key, lambda: random.randint(100, 200)), len(cache.times)
