from sanic import response
from enum import IntEnum
from datetime import timedelta, datetime


__all__ = (
    "RouteBucket",
    "make_bucket_key",
    "rate_limit"
)


class RouteBucket(IntEnum):
    GLOBAL = 0
    USER = 1


def make_bucket_key(req, bucket, params=False, query=False):
    if params:
        key = req.path
    else:
        key = req.uri_template

    if bucket == RouteBucket.USER:
        if req.user is not None:
            key += f":{req.user['id']}"
        else:
            key += f":{req.ip}"

    if query:
        key += req.query_string

    return key


def rate_limit(burst=5, bucket=RouteBucket.USER, params=False, query=False, **per):
    seconds = timedelta(**per).total_seconds()

    def _predicate(handler):
        async def _wrapper(req, *args, **kwargs):
            user = kwargs.get("user")
            user_burst = burst
            if user is not None:
                user_burst = (user.get("premium_level", 0) + 1) * burst

            pre_key = make_bucket_key(req, bucket, params=params, query=query)
            key = f"rate_limit:{pre_key}"
            current = await req.app.redis.get(key)
            if current is None:
                await req.app.redis.setex(key, seconds, 1)

            elif int(current) >= user_burst:
                retry_after = await req.app.redis.pttl(key)
                retry_at = datetime.utcnow() + timedelta(milliseconds=retry_after)
                return response.json({
                    "retry_after": max(0, retry_after / 1000),
                    "retry_at": retry_at.timestamp(),
                    "text": "Too many requests, please try again later"
                }, status=429)

            else:
                await req.app.redis.incr(key)

            return await handler(req, *args, **kwargs)

        return _wrapper

    return _predicate
