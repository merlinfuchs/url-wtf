from sanic import Blueprint
from sanic.exceptions import abort
import pymongo
import pymongo.errors

from auth import *
from validation import *
from database import *
from ratelimits import *
from cache import *


bp = Blueprint("/scopes", url_prefix="/scopes")
scopes_cache = Cache(minutes=1)
scope_cache = Cache(minutes=1, params=True)


@bp.post("/")
@resolve_user(required=True)
@validate_json(CREATE_SCOPE_SCHEMA)
@rate_limit(burst=5, seconds=5)
async def _create_custom_scope(req, user, data):
    try:
        await req.app.db.scopes.insert_one({
            "_id": get_snowflake(),
            "name": data["name"],
            "verified": False,
            "owner_id": user["id"],
            "public": False,
            "user_ids": [user["id"]]
        })
    except pymongo.errors.DuplicateKeyError:
        return abort(400, "A scope with that name already exists")

    await scopes_cache.delete(req)
    return abort(200)


@bp.get("/")
@resolve_user()
@rate_limit(burst=3, seconds=5)
@use_cache(scopes_cache)
async def _get_custom_scopes(req, user):
    scopes = [
        {
            "name": req.app.config.DEFAULT_SCOPE,
            "default": True
        }
    ]
    if user is not None:
        async for scope in req.app.db.scopes.find({"user_ids": user["id"]}):
            del scope["_id"]
            scopes.append(scope)

    return CacheValue(scopes)


@bp.get("/<name>")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=5)
@use_cache(scope_cache)
async def _get_custom_scope(req, name, user):
    doc = await req.app.db.scopes.find_one({"name": name, "user_ids": user["id"]})
    if doc is None:
        return abort(404, "Unknown scope")

    del doc["_id"]
    return CacheValue(doc)


@bp.delete("/<name>")
@resolve_user(required=True)
@rate_limit(burst=3, seconds=5)
async def _delete_custom_scope(req, name, user):
    result = await req.app.db.scopes.delete_one({"name": name, "owner_id": user["id"]})
    if result.deleted_count == 0:
        return abort(404, "Unknown scope")

    await scopes_cache.delete(req)
    await scope_cache.delete(req)
    return abort(200)


@bp.get("/check")
@rate_limit(burst=20, seconds=5)
async def _caddy_ask(req):
    scope = req.args.get("domain")
    if not scope:
        return abort(400, "No domain provided")

    if scope == req.app.config.DEFAULT_SCOPE:
        return abort(200)

    doc = await req.app.db.scopes.find_one({"name": scope.strip()}, projection=("verified",))
    if doc is None:
        return abort(404, "Unknown scope")
    elif not doc["verified"]:
        return abort(403, "Scope is not verified")
    else:
        return abort(200)
