import jwt
import pymongo
from sanic.exceptions import abort
from datetime import datetime

from database import *


__all__ = (
    "resolve_user",
    "make_auth_token",
    "reset_token",
    "login_user"
)


def resolve_user(required=False):
    def _predicate(handler):
        async def _check_auth(req, *args, **kwargs):
            user = None
            raw_token = req.headers.get("Authorization")
            if raw_token is not None:
                try:
                    token_data = jwt.decode(raw_token, key=req.app.config.JWT_KEY)
                except jwt.DecodeError:
                    pass
                else:
                    user_id = token_data["u"]
                    timestamp = datetime.fromtimestamp(token_data["t"])

                    user = await req.app.db.users.find_one({"_id": user_id})
                    if user is not None:
                        user["id"] = user.pop("_id")
                        if timestamp < user["token_reset"]:
                            user = None

            if user is None and required:
                return abort(401, "Token required")

            req.user = user
            return await handler(req, *args, **kwargs, user=user)
        return _check_auth
    return _predicate


def make_auth_token(app, user_id):
    return jwt.encode({"u": user_id, "t": int(datetime.utcnow().timestamp()) + 30}, key=app.config.JWT_KEY)


async def reset_token(app, user_id):
    await app.db.users.update_one({"_id": user_id}, {"$set": {"token_reset": datetime.utcnow()}})
    return make_auth_token(app, str(user_id))


async def login_user(app, email, name):
    doc = await app.db.users.find_one_and_update(
        {"email": email},
        {
            "$set": {"name": name},
            "$setOnInsert": {
                "_id": get_snowflake(),
                "token_reset": datetime.utcnow(),
                "premium_level": 0
            }
        },
        return_document=pymongo.ReturnDocument.AFTER,
        upsert=True
    )
    return make_auth_token(app, doc["_id"])
