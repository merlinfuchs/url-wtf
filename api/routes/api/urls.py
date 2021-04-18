from sanic import Blueprint, response
from sanic.exceptions import abort
import pymongo.errors

from validation import *
from util import *
from database import *
from auth import *
from ratelimits import *
from cache import *


bp = Blueprint("api_urls", url_prefix="/urls")
urls_cache = Cache(minutes=1)


@bp.get("/<url_id>")
@resolve_user(required=True)
@rate_limit(burst=10, seconds=5)
@cache(minutes=1, params=True)
async def _get_url(req, url_id, user):
    doc = await req.app.db.links.find_one({"_id": url_id, "type": LinkType.URL, "user_id": user["id"]})
    if doc is None:
        return abort(404, "Unknown URL")

    if doc["type"] != LinkType.URL:
        return abort(404, "Unknown URL")

    del doc["user_id"]
    doc["id"] = doc.pop("_id")
    return CacheValue(doc)


@bp.delete("/<url_id>")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=5)
async def _delete_url(req, url_id, user):
    result = await req.app.db.links.delete_one({"_id": url_id, "type": LinkType.URL, "user_id": user["id"]})
    if result.deleted_count == 0:
        return abort(404, "Unknown URL")

    await urls_cache.delete(req)
    return abort(200)


@bp.get("/")
@resolve_user(required=True)
@rate_limit(burst=3, seconds=5)
@use_cache(urls_cache)
async def _get_urls(req, user):
    urls = []
    async for doc in req.app.db.links.find({"user_id": user["id"], "type": LinkType.URL}):
        doc["id"] = doc.pop("_id")
        urls.append(doc)

    return CacheValue(urls)


@bp.post("/")
@resolve_user()
@validate_json(CREATE_URL_SCHEMA)
@rate_limit(burst=10, seconds=5)
async def _create_url(req, user, data):
    if data["type"] == "custom":
        name = data["name"]
    else:
        name = URL_TYPES[data["type"]]()

    user_id = None
    if user is not None:
        user_id = user["id"]

    if data["scope"] != req.app.config.DEFAULT_SCOPE:
        doc = await req.app.db.scopes.find_one({"name": data["scope"]}, projection=("public", "user_ids", "verified"))
        if doc is None:
            return abort(400, "Unknown scope")

        if not doc["verified"]:
            return abort(400, "Scope isn't verified")

        if not doc["public"]:
            if user is None or user["id"] not in doc["user_ids"]:
                return abort(403, "Missing access to scope")

    try:
        data["id"] = await req.app.links.create_url(data["scope"], name, data["target"], user_id=user_id)
    except pymongo.errors.DuplicateKeyError:
        return abort(400, "There is already an URL with that name")

    data["url"] = f"https://{data['scope']}/{name}"
    data["name"] = name
    return response.json(data)
