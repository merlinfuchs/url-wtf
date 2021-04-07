from sanic import Blueprint

from . import api, resolve, links


bp = Blueprint.group([api.bp, resolve.bp, links.bp])
