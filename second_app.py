import asyncio

import async_timeout
from aioredis import Redis
from aioredis.client import PubSub
from fastapi import FastAPI, BackgroundTasks
from fastapi.params import Depends
from fastapi_plugins import depends_redis, redis_plugin
from sse_starlette.sse import EventSourceResponse
# from starlette.responses import HTMLResponse


STOPWORD = "STOP"

app = FastAPI()


@app.on_event("startup")
async def on_startup(redis: Redis = Depends(depends_redis)) -> None:
    await redis_plugin.init_app(app)
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


@app.get("/")
async def root_get(cache: Redis = Depends(depends_redis)) -> dict:
    return dict(ping=await cache.ping())


@app.get("/listener")
async def stream(background_tasks: BackgroundTasks, channel: str = "example:channel", redis: Redis = Depends(depends_redis)):
    pub_sub_reader = redis.pubsub()
    # background_tasks.add_task(listener(channel, pub_sub_reader))
    return EventSourceResponse(listener(channel, pub_sub_reader))


async def listener(channel: str, pub_sub: PubSub):
    async with pub_sub as p:
        await p.subscribe(channel)
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await p.get_message(ignore_subscribe_messages=True)
                    if message:
                        if message.get('data') == STOPWORD:
                            break
                        yield {"event": "message", "data": message.get('data')}
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass
