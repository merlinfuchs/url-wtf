from ratelimits import *
from datetime import timedelta
import json
from sanic import response
from uuid import uuid4


__all__ = (
    "Cache",
    "RouteBucket",
    "use_cache",
    "cache",
    "CacheValue"
)


class Cache:
    def __init__(self, bucket=RouteBucket.USER, params=False, query=False, **td):
        self.name = uuid4().hex
        self.bucket = bucket
        self.params = params
        self.query = query
        self.ttl = timedelta(**td).total_seconds()

    def make_bucket_key(self, req):
        if self.params:
            key = f"{self.name}:{json.dumps(req.match_info)}"
        else:
            key = self.name

        if self.bucket == RouteBucket.USER:
            if req.user is not None:
                key += f":{req.user['id']}"
            else:
                key += f":{req.ip}"

        if self.query:
            key += req.query_string

        return f"cache:{key}"

    async def add(self, req, value):
        key = self.make_bucket_key(req)
        await req.app.redis.setex(key, self.ttl, value.to_json())

    async def get(self, req):
        key = self.make_bucket_key(req)

        cached = await req.app.redis.get(key)
        if cached is not None:
            return CacheValue.from_json(cached)

        return None

    async def delete(self, req):
        key = self.make_bucket_key(req)
        await req.app.redis.delete(key)


class CacheValue:
    def __init__(self, data):
        self.data = data

    def to_json(self):
        return json.dumps(self.data)

    @classmethod
    def from_json(cls, data_string):
        return cls(json.loads(data_string))


def use_cache(cache):
    def _predicate(handler):
        async def _wrapper(req, *args, **kwargs):
            cached = await cache.get(req)
            if cached is not None:
                return response.json(cached.data, status=200)

            resp = await handler(req, *args, **kwargs)
            if isinstance(resp, CacheValue):
                await cache.add(req, resp)
                return response.json(resp.data, status=200)
            else:
                return resp

        return _wrapper

    return _predicate


def cache(bucket=RouteBucket.USER, params=False, query=False, **td):
    cache = Cache(bucket=bucket, params=params, query=query, **td)
    return use_cache(cache)
