from sanic import Blueprint, response
from sanic.exceptions import abort
import pymongo.errors

from validation import *
from util import *
from database import *
from auth import *
from ratelimits import *


bp = Blueprint("api_files", url_prefix="/files")


@bp.get("/<scope>/<name>")
@rate_limit(burst=10, seconds=5, bucket=RouteBucket.TOKEN)
async def _get_file(req, scope, name):
    doc = await req.app.db.links.find_one({"scope": scope, "name": name, "type": LinkType.URL})
    if doc is None:
        return response.json({"error": "Unknown URL"}, status=404)

    if doc["type"] != LinkType.FILE:
        return response.json({"error": "Unknown File"}, status="404")

    del doc["user_id"]
    doc["id"] = doc.pop("_id")
    return response.json(doc)


@bp.post("/")
@resolve_user(required=True)
@validate_json(CREATE_FILE_SCHEMA)
@rate_limit(burst=5, seconds=5, bucket=RouteBucket.TOKEN)
async def _create_file(req, user, data):
    if data["type"] == "custom":
        name = data["name"]
    else:
        name = URL_TYPES[data["type"]]()

    file = req.files.get("file")
    if file is None:
        return response.json({"error": "A file is required"}, status=400)

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

    file_extension = file.name.rsplit(".")[-1]
    try:
        data["id"], data["target"] = await req.app.links.create_file(
            data["scope"], name, file_extension, file.body, user_id=user_id
        )
    except pymongo.errors.DuplicateKeyError:
        return abort(400, "There is already an URL with that name")

    data["url"] = f"https://{data['scope']}/{name}"
    return response.json(data)
