from sanic import Sanic, response
from sanic.exceptions import SanicException, MethodNotSupported
from aiohttp import ClientSession
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
import json

import routes
from database import LinkDatabase


DEBUG = True
CORS_HEADERS = {
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*"
}


class App(Sanic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.redis = None
        self.db = None
        self.links = None
        self.session = None

        self.blueprint(routes.bp)
        self.error_handler.add(SanicException, self.on_http_error)
        self.register_middleware(self.cors_middleware, "response")
        self.register_listener(self.setup, "before_server_start")
        self.register_listener(self.teardown, "after_server_stop")

    async def setup(self, _, loop):
        self.redis = await aioredis.create_redis_pool(
            getattr(self.config, "REDIS_URL", "redis://127.0.0.1"),
            minsize=3,
            loop=loop
        )
        self.db = AsyncIOMotorClient(getattr(self.config, "MONGO_URL", "mongodb://127.0.0.1")).url_wtf
        self.links = LinkDatabase(self)
        await self.links.create_indexes()
        self.session = ClientSession(loop=loop)

        caddy_url = getattr(self.config, "CADDY_URL", None)
        if caddy_url is not None:
            with open("caddy.json", "r") as f:
                caddy_config = json.load(f)

            async with self.session.post(f"{caddy_url}/load", json=caddy_config) as resp:
                resp.raise_for_status()

    async def teardown(self, _, loop):
        self.redis.close()
        await self.redis.wait_closed()
        await self.session.close()

    async def on_http_error(self, request, e):
        if isinstance(e, MethodNotSupported) and request.method == "OPTIONS":
            return response.HTTPResponse(headers=CORS_HEADERS)

        return response.json({"text ": str(e)}, status=getattr(e, "status_code", 500))

    async def cors_middleware(self, _, resp):
        resp.headers.update(CORS_HEADERS)


if __name__ == "__main__":
    app = App(name="url.wtf", load_env="APP_", strict_slashes=False)
    if not DEBUG:
        app.config.PROXIES_COUNT = 2
    else:
        app.config.FILE_LOCATION = "./files"

    app.run(host="127.0.0.1", port=8000, access_log=True, debug=DEBUG, auto_reload=DEBUG)
