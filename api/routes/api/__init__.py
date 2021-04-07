from sanic import Blueprint

from . import files, urls, auth, scopes, pastes


bp = Blueprint.group([files.bp, urls.bp, auth.bp, scopes.bp, pastes.bp], url_prefix="/api")
