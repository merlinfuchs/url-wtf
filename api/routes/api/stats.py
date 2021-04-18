from sanic import Blueprint, response
from sanic.exceptions import abort

from auth import *
from ratelimits import *
from cache import *


bp = Blueprint("api_stats", url_prefix="/stats")


@bp.get("/<link_id>/<period>")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=10)
@cache(params=True, minutes=1)
async def _get_stats(req, link_id, period, user):
    return response.json({
        "browser": {
            "Firefox": 30,
            "Chrome": 60,
            "Opera": 10
        },
        "os": {
            "Windows": 70,
            "Mac OS X": 20,
            "Linux": 10
        },
        "clicks": {

        }
    })

    return abort(404, "No stats available")

