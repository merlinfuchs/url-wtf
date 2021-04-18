from sanic import Blueprint, response
import asyncio
from datetime import datetime
from sanic.exceptions import abort
from urllib.parse import urlparse
from ua_parser import user_agent_parser

from database import LinkType
from ratelimits import *


bp = Blueprint("resolve")
bp.static("/f", "./files")
metrics_points = []

with open("./paste.html") as f:
    paste_template = f.read()


@bp.listener("after_server_start")
async def _on_server_start(app, loop):
    app.add_task(_write_points_loop(app))


async def _write_points_loop(app):
    global metrics_points

    while app.is_running:
        await asyncio.sleep(10)
        points = list(metrics_points)
        metrics_points = []
        await app.influx.write(points)


@bp.get("/<name>")
@rate_limit(burst=10, seconds=5, bucket=RouteBucket.USER)
async def _resolve(req, name):
    scope = req.headers.get("HOST")
    doc = await req.app.db.links.find_one({"scope": scope, "name": name})
    if doc is None:
        return abort(404, "Unknown link")

    if doc["user_id"] is not None:
        user_agent = req.headers.get("User-Agent")
        ua_os = "other"
        ua_browser = "other"
        if user_agent is not None:
            parsed_ua = user_agent_parser.Parse(user_agent)
            ua_os = parsed_ua["os"]["family"]
            ua_browser = parsed_ua["user_agent"]["family"]

        referer = req.headers.get("Referer")
        if referer is not None:
            referer_url = urlparse(referer)
            referer = referer_url.hostname
        else:
            referer = "direct"

        metrics_points.append({
            "time": datetime.utcnow(),
            "measurement": "links_resolved",
            "tags": {
                "id": doc["_id"],
                "scope": doc["scope"],
                "referer": referer,
                "ua_os": ua_os,
                "ua_browser": ua_browser
            },
            "fields": {"value": 1}
        })

    _type, target = await req.app.links.resolve_link(scope, name)
    if _type == LinkType.URL:
        return response.redirect(target, status=302)
    elif _type == LinkType.FILE:
        return response.redirect(f"https://{req.app.config.DEFAULT_SCOPE}/f/{target}", status=302)
    elif _type == LinkType.PASTE:
        return response.html(paste_template.replace("{{text}}", target))
    else:
        return response.json({"error": "Unknown link"}, status=404)
