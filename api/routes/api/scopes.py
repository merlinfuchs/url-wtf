from sanic import Blueprint, response
from sanic.exceptions import abort
import async_dns.resolver
from async_dns.core import types as dnc_types
import asyncio
import traceback
import pymongo
import pymongo.errors

from auth import *
from validation import *
from database import *
from ratelimits import *


bp = Blueprint("/scopes", url_prefix="/scopes")


@bp.listener("after_server_start")
async def verify_loop(app, _):
    await app.db.scopes.create_index([("name", pymongo.ASCENDING)], unique=True)

    while app.is_running:
        await asyncio.sleep(60)
        resolver = async_dns.resolver.Resolver()
        async for scope in app.db.scopes.find({"verified": False}):
            try:
                result = await resolver.query_safe(scope["name"], dnc_types.TXT)
                if result is None:
                    continue

                for record in filter(lambda r: r.qtype == dnc_types.TXT, result.an):
                    text = record.data.decode().strip()
                    parts = text.split("=")
                    if parts[0] != "url.wtf" or len(parts) != 2:
                        continue

                    if parts[1] == scope["owner_id"]:
                        # TODO: call certbot
                        await app.db.scopes.update_one({"_id": scope["_id"]}, {"$set": {"verified": True}})
                        break
            except:
                traceback.print_exc()


@bp.post("/")
@resolve_user(required=True)
@validate_json(CREATE_SCOPE_SCHEMA)
@rate_limit(burst=5, seconds=5, bucket=RouteBucket.TOKEN)
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

    return abort(200)


@bp.get("/")
@resolve_user()
@rate_limit(burst=3, seconds=5, bucket=RouteBucket.IP)
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

    return response.json(scopes)


@bp.get("/<name>")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=5, bucket=RouteBucket.TOKEN)
async def _get_custom_scope(req, name, user):
    doc = await req.app.db.scopes.find_one({"name": name, "user_ids": user["id"]})
    if doc is None:
        return abort(404, "Unknown scope")

    del doc["_id"]
    return response.json(doc)


@bp.delete("/<name>")
@resolve_user(required=True)
@rate_limit(burst=3, seconds=5, bucket=RouteBucket.TOKEN)
async def _delete_custom_scope(req, name, user):
    result = await req.app.db.scopes.delete_one({"name": name, "owner_id": user["id"]})
    if result.deleted_count == 0:
        return abort(404, "Unknown scope")

    return abort(200)


@bp.get("/check")
@rate_limit(burst=20, seconds=5, bucket=RouteBucket.IP)
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