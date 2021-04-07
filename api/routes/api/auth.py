from sanic import Blueprint, response
import pymongo

from auth import *
from validation import *
from ratelimits import *

bp = Blueprint("api_auth", url_prefix="/auth")


@bp.listener("after_server_start")
async def init(app, _):
    await app.db.users.create_index([("email", pymongo.ASCENDING)], unique=True)


@bp.get("/user")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=5, bucket=RouteBucket.TOKEN)
async def _get_user(req, user):
    return response.json(user)


@bp.delete("/user")
@resolve_user(required=True)
@rate_limit(burst=2, seconds=60, bucket=RouteBucket.TOKEN)
async def _delete_user(req, user):
    return response.json(user)


@bp.delete("/user/token")
@resolve_user(required=True)
@rate_limit(burst=2, seconds=10, bucket=RouteBucket.IP)
async def _reset_token(req, user):
    new_token = await reset_token(req.app, user["id"])
    return response.json({"token": new_token})


@bp.post("/discord")
@validate_json(AUTH_DISCORD_SCHEMA)
@rate_limit(burst=3, seconds=5, bucket=RouteBucket.IP)
async def _auth_with_discord(req, data):
    token = await login_user(req.app, "login@merlin.gg", "Merlin")
    return response.json({"token": token})
