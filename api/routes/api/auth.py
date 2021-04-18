from sanic import Blueprint, response
from sanic.exceptions import abort
import pymongo
from urllib.parse import quote as urlquote

from auth import *
from validation import *
from ratelimits import *
from cache import *

bp = Blueprint("api_auth", url_prefix="/auth")


@bp.listener("after_server_start")
async def init(app, _):
    await app.db.users.create_index([("email", pymongo.ASCENDING)], unique=True)


@bp.get("/user")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=5)
@cache(minutes=1)
async def _get_user(req, user):
    user["token_reset"] = user["token_reset"].timestamp()
    return CacheValue(user)


@bp.delete("/user")
@resolve_user(required=True)
@rate_limit(burst=2, seconds=60)
async def _delete_user(req, user):
    return response.json(user)


@bp.delete("/user/token")
@resolve_user(required=True)
@rate_limit(burst=2, seconds=10)
async def _reset_token(req, user):
    new_token = await reset_token(req.app, user["id"])
    return response.json({"token": new_token})


@bp.get("/discord")
async def _redirect_to_discord(req):
    config = req.app.config
    return response.redirect(f"https://discord.com/api/oauth2/authorize?client_id={config.DISCORD_OAUTH_ID}&"
                             f"redirect_uri={urlquote(config.DISCORD_OAUTH_REDIRECT)}&"
                             f"response_type=code&scope=identify%20email&prompt=none")


@bp.post("/discord")
@validate_json(AUTH_DISCORD_SCHEMA)
@rate_limit(burst=3, seconds=5)
async def _auth_with_discord(req, data):
    code = data["code"]

    config = req.app.config
    async with req.app.session.post(
            "https://discord.com/api/v8/oauth2/token",
            data={
                "client_id": config.DISCORD_OAUTH_ID,
                "client_secret": config.DISCORD_OAUTH_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config.DISCORD_OAUTH_REDIRECT,
                "scope": "identify, email"
            }
    ) as resp:
        if resp.status >= 300:
            return abort(resp.status, await resp.text())

        token_data = await resp.json()

    async with req.app.session.get(
            "https://discord.com/api/v8/users/@me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
    ) as resp:
        if resp.status >= 300:
            return abort(resp.status, await resp.text())

        user_data = await resp.json()

    token = await login_user(req.app, user_data["email"], user_data["username"])
    return response.json({"token": token})


@bp.get("/github")
async def _redirect_to_github(req):
    config = req.app.config
    return response.redirect(f"https://github.com/login/oauth/authorize?client_id={config.GITHUB_OAUTH_ID}&"
                             f"redirect_uri={urlquote(config.GITHUB_OAUTH_REDIRECT)}&"
                             f"response_type=code&scope=read:user%20user:email")


@bp.post("/github")
@validate_json(AUTH_GITHUB_SCHEMA)
@rate_limit(burst=3, seconds=5)
async def _auth_with_github(req, data):
    code = data["code"]

    config = req.app.config
    async with req.app.session.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": config.GITHUB_OAUTH_ID,
                "client_secret": config.GITHUB_OAUTH_SECRET,
                "code": code,
                "redirect_uri": config.GITHUB_OAUTH_REDIRECT,
                "scope": "identify, email"
            },
            headers={"Accept": "application/json"}
    ) as resp:
        if resp.status >= 300:
            return abort(resp.status, await resp.text())

        token_data = await resp.json()

    async with req.app.session.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token_data['access_token']}"}
    ) as resp:
        if resp.status >= 300:
            return abort(resp.status, await resp.text())

        user_data = await resp.json()

    token = await login_user(req.app, user_data["email"], user_data["name"])
    return response.json({"token": token})
