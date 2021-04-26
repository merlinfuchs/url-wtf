from sanic import Blueprint

from . import api, resolve


bp = Blueprint.group([api.bp, resolve.bp])
