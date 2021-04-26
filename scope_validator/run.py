import asyncio
from os import environ as env
from motor.motor_asyncio import AsyncIOMotorClient
import async_dns.resolver
from async_dns.core import types as dnc_types
import subprocess
from concurrent.futures import ThreadPoolExecutor

loop = asyncio.get_event_loop()
loop.set_default_executor(ThreadPoolExecutor(max_workers=10))
db = AsyncIOMotorClient(env.get("MONGO_URL", "mongodb://127.0.0.1")).url_wtf


async def validate_scope(resolver, scope):
    result = await resolver.query_safe(scope["name"], dnc_types.TXT)
    if result is None:
        return

    for record in filter(lambda r: r.qtype == dnc_types.TXT, result.an):
        text = record.data.decode().strip()
        parts = text.split("=")
        if parts[0] != "url.wtf" or len(parts) != 2:
            continue

        if parts[1] == scope["owner_id"]:
            result = await loop.run_in_executor(None, subprocess.run, [
                "certbot", "certonly", "--webroot", "-w", "/var/www/html/certs", "-d", scope["name"],
                "--non-interactive"
            ])
            if result.returncode == 0:
                await db.scopes.update_one({"_id": scope["_id"]}, {"$set": {"verified": True}})

            return


async def main():
    while True:
        await asyncio.sleep(60)

        resolver = async_dns.resolver.Resolver()
        tasks = []
        async for scope in db.scopes.find({"verified": False}):
            tasks.append(loop.create_task(validate_scope(resolver, scope)))

        if tasks:
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)


loop.run_until_complete(main())
