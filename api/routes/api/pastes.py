from sanic import Blueprint, response

from validation import *
from auth import *


bp = Blueprint("api_pastes", url_prefix="/pastes")


@bp.post("/")
@resolve_user()
@validate_json(CREATE_PASTE_SCHEMA)
async def _create_paste(req, data, user):
    pass
