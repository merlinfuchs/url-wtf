from sanic import Blueprint, response
from sanic.exceptions import abort
import pymongo.errors

from validation import *
from util import *
from database import *
from auth import *
from ratelimits import *


bp = Blueprint("api_urls", url_prefix="/urls")


@bp.get("/<scope>/<name>")
@rate_limit(burst=10, seconds=5, bucket=RouteBucket.IP)
async def _get_url(req, scope, name):
    doc = await req.app.db.links.find_one({"scope": scope, "name": name, "type": LinkType.URL})
    if doc is None:
        return response.json({"error": "Unknown URL"}, status=404)

    if doc["type"] != LinkType.URL:
        return response.json({"error": "Unknown URL"}, status="404")

    del doc["user_id"]
    doc["id"] = doc.pop("_id")
    return response.json(doc)


@bp.post("/")
@resolve_user()
@validate_json(CREATE_URL_SCHEMA)
@rate_limit(burst=10, seconds=5, bucket=RouteBucket.IP)
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
    return response.json(data)
