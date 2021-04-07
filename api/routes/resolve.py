from sanic import Blueprint, response

from database import LinkType
from ratelimits import *


bp = Blueprint("resolve")


bp.static("/f", "./files")


@bp.get("/<name>")
@rate_limit(burst=10, seconds=5, bucket=RouteBucket.IP)
async def _resolve(req, name):
    scope = req.host.split(":")[0]
    _type, target = await req.app.links.resolve_link(scope, name)
    if _type == LinkType.URL:
        return response.redirect(target, status=302)
    elif _type == LinkType.FILE:
        return response.redirect(f"https://{req.app.config.DEFAULT_SCOPE}/f/{target}", status=302)
    else:
        return response.json({"error": "Unknown link"}, status=404)
