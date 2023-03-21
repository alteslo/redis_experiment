import asyncio

import json
from aioredis import Redis
from aioredis.client import PubSub
from fastapi import FastAPI, BackgroundTasks
from fastapi.params import Depends
from fastapi_plugins import depends_redis, redis_plugin
from sse_starlette.sse import EventSourceResponse
from fastapi_utils.tasks import repeat_every
import async_timeout
# from starlette.responses import HTMLResponse


STOPWORD = "STOP"

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    await redis_plugin.init_app(app)
    await redis_plugin.init()
    subscriber = redis_plugin.redis.pubsub()
    # loop = asyncio.get_event_loop()
    asyncio.create_task(consumer("first_app:channel", subscriber))
    # await loop.run_forever()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


@app.get("/")
async def root_get(cache: Redis = Depends(depends_redis)) -> dict:
    return dict(ping=await cache.ping())


# async def consumer(channel: str, pub_sub: PubSub):
#     async with pub_sub as p:
#         await p.subscribe(channel)
#         while True:
#             try:
#                 async with async_timeout.timeout(1):
#                     message = await p.get_message(ignore_subscribe_messages=True)
#                     if message:
#                         # if message.get('data') == STOPWORD:
#                         #     break
#                         print({"event": "message", "data": message.get('data')})
#                         # yield {"event": "message", "data": message.get('data')}
#                     await asyncio.sleep(0.01)
#             except asyncio.TimeoutError:
#                 pass


async def consumer(channel: str, pub_sub: PubSub):
    async with pub_sub as p:
        await p.subscribe(channel)
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await p.get_message(ignore_subscribe_messages=True)
                    if message:
                        message = json.loads(message.get('data'))
                        print({"event": "message", "data": message})
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass


# @repeat_every(seconds=0.01)
# async def consumer_th(channel: str, pub_sub: PubSub):
#     async with pub_sub as p:
#         await p.subscribe(channel)
#         try:
#             async with async_timeout.timeout(1):
#                 message = await p.get_message(ignore_subscribe_messages=True)
#                 if message:
#                     print({"event": "message", "data": message.get('data')})
#                     # yield {"event": "message", "data": message.get('data')}
#         except asyncio.TimeoutError:
#             pass
