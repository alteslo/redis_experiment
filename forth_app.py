import asyncio

import async_timeout
from aioredis import Redis
from aioredis.client import PubSub
from fastapi import FastAPI, BackgroundTasks
from fastapi.params import Depends
from fastapi_plugins import depends_redis, redis_plugin
from sse_starlette.sse import EventSourceResponse
from contextlib import asynccontextmanager
# from starlette.responses import HTMLResponse


STOPWORD = "STOP"

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    await redis_plugin.init_app(app)
    await redis_plugin.init()
    subscriber = redis_plugin.redis.pubsub()
    await consumer("first_app:channel", subscriber)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


@app.get("/")
async def root_get(cache: Redis = Depends(depends_redis)) -> dict:
    return dict(ping=await cache.ping())


async def consumer(channel: str, pub_sub: PubSub):
    async with pub_sub as p:
        await p.subscribe(channel)
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await p.get_message(ignore_subscribe_messages=True)
                    if message:
                        if message.get('data') == STOPWORD:
                            break
                        print({"event": "message", "data": message.get('data')})
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass
