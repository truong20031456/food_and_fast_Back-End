from fastapi import Depends
from cachetools import TTLCache


class CacheService:
    def __init__(self, cache: TTLCache):
        self.cache = cache

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]


_cache = TTLCache(maxsize=1000, ttl=300)


def get_cache_service():
    return CacheService(cache=_cache)
