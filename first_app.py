from aioredis import Redis
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi_plugins import depends_redis, redis_plugin
import json


app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    await redis_plugin.init_app(app)
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


@app.get("/")
async def root_get(cache: Redis = Depends(depends_redis)) -> dict:
    return dict(ping=await cache.ping())


@app.post("/publish")
async def get_publish(message: dict[str, str], channel: str = "first_app:channel", redis: Redis = Depends(depends_redis)):
    message = json.dumps(message)
    await redis.publish(channel=channel, message=message)
    return ""
