from sanic import Blueprint, response
from sanic.exceptions import abort
import pymongo.errors
import imghdr

from validation import *
from util import *
from database import *
from auth import *
from ratelimits import *
from cache import *


bp = Blueprint("api_files", url_prefix="/images")
scope_cache = Cache(minutes=1, params=True)


@bp.get("/<file_id>")
@resolve_user(required=True)
@rate_limit(burst=10, seconds=5)
@use_cache(scope_cache)
async def _get_file(req, file_id, user):
    doc = await req.app.db.links.find_one({"_id": file_id, "type": LinkType.URL, "user_id": user["id"]})
    if doc is None:
        return response.json({"error": "Unknown URL"}, status=404)

    if doc["type"] != LinkType.FILE:
        return response.json({"error": "Unknown File"}, status="404")

    del doc["user_id"]
    doc["id"] = doc.pop("_id")
    return CacheValue(doc)


@bp.post("/")
@resolve_user(required=True)
@validate_json(CREATE_FILE_SCHEMA)
@rate_limit(burst=5, seconds=5)
async def _create_file(req, user, data):
    if data["type"] == "custom":
        name = data["name"]
    else:
        name = URL_TYPES[data["type"]]()

    file = req.files.get("file")
    if file is None:
        return abort(400, "A file is required")

    img_type = imghdr.what(None, h=file.body)
    if img_type is None:
        return abort(400, "Invalid image type")

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
        data["id"], data["target"] = await req.app.links.create_file(
            data["scope"], name, img_type, file.body, user_id=user_id
        )
    except pymongo.errors.DuplicateKeyError:
        return abort(400, "There is already an URL with that name")

    data["url"] = f"https://{data['scope']}/{name}"
    return response.json(data)
