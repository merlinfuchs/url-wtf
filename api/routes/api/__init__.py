from sanic import Blueprint

from . import files, urls, auth, scopes, pastes, stats


bp = Blueprint.group([files.bp, urls.bp, auth.bp, scopes.bp, pastes.bp, stats.bp], url_prefix="/api")
