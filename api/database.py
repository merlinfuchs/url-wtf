from enum import IntEnum
import hashlib
import pymongo
import aiofiles
from datetime import datetime

__all__ = (
    "get_snowflake",
    "LinkType",
    "LinkDatabase"
)

SNOWFLAKE_EPOCH = 1609459200
_generated_snowflakes = 0


def get_snowflake() -> str:
    global _generated_snowflakes

    genid_b = "{0:012b}".format(_generated_snowflakes % 4096)
    procid_b = "{0:05b}".format(1)
    workid_b = "{0:05b}".format(1)

    timestamp = int(datetime.utcnow().timestamp() * 1000) - SNOWFLAKE_EPOCH
    epoch_b = "{0:042b}".format(timestamp)

    snowflake_b = f"{epoch_b}{workid_b}{procid_b}{genid_b}"
    _generated_snowflakes += 1

    return str(int(snowflake_b, 2))


class LinkType(IntEnum):
    URL = 0
    FILE = 1
    PASTE = 2


class LinkDatabase:
    def __init__(self, app):
        self.app = app
        self.redis = app.redis
        self.db = app.db

    async def create_indexes(self):
        await self.db.links.create_index([("name", pymongo.ASCENDING), ("scope", pymongo.ASCENDING)], unique=True)
        await self.db.links.create_index([("user_id", pymongo.ASCENDING)])
        await self.db.links.create_index([("target", pymongo.ASCENDING)])

    async def create_url(self, scope, name, url, user_id=None):
        result = await self.db.links.insert_one({
            "_id": get_snowflake(),
            "user_id": user_id,
            "type": LinkType.URL,
            "name": name,
            "scope": scope,
            "target": url
        })
        await self.redis.setex(f"links:{scope}:{name}", 24 * 60 * 60, f"{LinkType.URL}:{url}")
        return str(result.inserted_id)

    async def create_file(self, scope, name, file_extension, file_blob, user_id=None):
        file_hash = hashlib.md5(file_blob).hexdigest()
        file_name = f"{file_hash}.{file_extension}"

        async with aiofiles.open(f"{self.app.config.FILE_LOCATION}/{file_name}", "wb") as f:
            await f.write(file_blob)

        result = await self.db.links.insert_one({
            "_id": get_snowflake(),
            "user_id": user_id,
            "type": LinkType.FILE,
            "name": name,
            "scope": scope,
            "target": file_name
        })
        # await self.redis.setex(f"links:{scope}:{name}", 24 * 60 * 60, f"{LinkType.FILE}:{file_name}")
        return str(result.inserted_id), file_name

    async def resolve_link(self, scope, name):
        cached = await self.redis.get(f"links:{scope}:{name}")
        if cached is not None:
            _type, target = cached.decode("utf-8").split(":", 1)
            return int(_type), target

        doc = await self.db.links.find_one({"scope": scope, "name": name})
        if doc is None:
            return None, None

        # await self.redis.setex(f"links:{scope}:{name}", 24 * 60 * 60, f"{doc['type']}:{doc['target']}")
        return doc["type"], doc["target"]
