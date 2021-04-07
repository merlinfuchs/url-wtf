import cerberus
from sanic import response
from sanic.exceptions import abort
from sanic.exceptions import InvalidUsage
import re
import json

__all__ = (
    "Validator",
    "validate_json",
    "CREATE_URL_SCHEMA",
    "CREATE_FILE_SCHEMA",
    "AUTH_DISCORD_SCHEMA",
    "CREATE_SCOPE_SCHEMA",
    "CREATE_PASTE_SCHEMA"
)


class Validator(cerberus.Validator):
    def _validate_type_url(self, value):
        if not re.match(r"^http(s)://.+\..+$", str(value).strip()):
            return False
        return True


def validate_json(schema):
    def _predicate(handler):
        async def _validate(req, *args, **kwargs):
            to_validate = None
            try:
                to_validate = req.json
            except InvalidUsage:
                print(req.form)
                raw = req.form.get("json")
                if raw is not None:
                    try:
                        to_validate = json.loads(raw)
                    except json.JSONDecodeError:
                        pass

            if to_validate is None:
                return abort(400, "Missing JSON body")

            validator = Validator(schema, purge_unknown=True)
            valid = validator.validate(to_validate)
            if not valid:
                return response.json(validator.errors, status=400)

            normalized = validator.normalized(to_validate)
            return await handler(req, *args, **kwargs, data=normalized)

        return _validate

    return _predicate


CREATE_URL_SCHEMA = {
    "target": {"type": "url", "required": True, "empty": False},
    "type": {
        "type": "string",
        "allowed": ["default", "invisible", "custom"],
        "default": "default",
        "empty": False
    },
    "name": {"type": "string", "empty": False},
    "scope": {"type": "string", "default": "url.wtf", "empty": False},
}

CREATE_FILE_SCHEMA = {
    "type": {
        "type": "string",
        "allowed": ["default", "invisible", "custom"],
        "default": "default",
        "empty": False
    },
    "name": {"type": "string", "empty": False},
    "scope": {"type": "string", "default": "url.wtf", "empty": False},
}

CREATE_PASTE_SCHEMA = {
    "type": {
        "type": "string",
        "allowed": ["default", "invisible", "custom"],
        "default": "default",
        "empty": False
    },
    "name": {"type": "string", "empty": False},
    "scope": {"type": "string", "default": "url.wtf", "empty": False},
    "text": {"type": "string", "empty": False, "required": True},
    "file_type": {"type": "string", "empty": False}
}

AUTH_DISCORD_SCHEMA = {
    "code": {"type": "string", "empty": False, "required": True}
}

CREATE_SCOPE_SCHEMA = {
    "name": {"type": "string", "empty": False, "regex": r"[a-zA-Z0-9\._-]+", "required": True}
}
