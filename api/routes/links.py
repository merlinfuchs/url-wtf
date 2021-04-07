from sanic import response, Blueprint


bp = Blueprint("links")


@bp.get("/")
async def _index(req):
    return response.redirect("/app", status=301)


@bp.get("/discord")
async def _index(req):
    return response.redirect("https://discord.gg", status=302)
