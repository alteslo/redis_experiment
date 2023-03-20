import asyncio

import async_timeout
from aioredis import Redis
from aioredis.client import PubSub
from fastapi import FastAPI, BackgroundTasks, status, Response
from fastapi.params import Depends
from fastapi_plugins import depends_redis, redis_plugin
from sse_starlette.sse import EventSourceResponse
# from starlette.responses import HTMLResponse


STOPWORD = "STOP"

app = FastAPI()


@app.get("/")
async def root_get(cache: Redis = Depends(depends_redis)) -> dict:
    return dict(ping=await cache.ping())


@app.get("/console_writer")
async def console_writer(message: str, channel: str):
    print(f'Write massage "{message}" from channel "{channel}"')
    return {}
