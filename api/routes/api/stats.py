from sanic import Blueprint, response
from datetime import datetime

from auth import *
from ratelimits import *
from cache import *


bp = Blueprint("api_stats", url_prefix="/stats")


@bp.get("/<link_id>/<period>")
@resolve_user(required=True)
@rate_limit(burst=5, seconds=10)
@cache(params=True, minutes=1)
async def _get_stats(req, link_id, period, user):
    if period not in {"24h", "7d", "30d"}:
        period = "24h"

    raw_browsers = await req.app.influx.query(
        f"SELECT count(value) "
        f"FROM url_wtf.autogen.links_resolved "
        f"WHERE time > now() - {period} AND id='{link_id}' "
        f"GROUP BY ua_browser"
    )
    browsers = {
        item["tags"]["ua_browser"]: item["values"][0][1]
        for item in raw_browsers["results"][0].get("series", [])
    }

    raw_systems = await req.app.influx.query(
        f"SELECT count(value) "
        f"FROM url_wtf.autogen.links_resolved "
        f"WHERE time > now() - {period} AND id='{link_id}' "
        f"GROUP BY ua_os"
    )
    systems = {
        item["tags"]["ua_os"]: item["values"][0][1]
        for item in raw_systems["results"][0].get("series", [])
    }

    raw_clicks = await req.app.influx.query(
        f"SELECT sum(value) "
        f"FROM url_wtf.autogen.links_resolved "
        f"WHERE time > now() - {period} AND id='{link_id}'"
        f"GROUP BY time(1h) FILL(0)",
        epoch="s"
    )
    try:
        clicks = {
            datetime.fromtimestamp(value[0]).strftime("%H:%M"): value[1]
            for value in raw_clicks["results"][0]["series"][0]["values"]
        }
    except (KeyError, IndexError):
        clicks = {}

    return response.json({
        "browser": browsers,
        "os": systems,
        "clicks": clicks
    })

