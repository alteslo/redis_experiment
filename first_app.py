from aioredis import Redis
from aioredis.client import PubSub
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi_plugins import depends_redis, redis_plugin
from sse_starlette.sse import EventSourceResponse
from starlette.responses import HTMLResponse
import async_timeout
import asyncio


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>SSE</title>
    </head>
    <body>
        <script>
            const evtSource = new EventSource("http://127.0.0.1:8888/sse/stream");
            evtSource.addEventListener("message", function(event) {
                // Logic to handle status updates
                console.log(event.data)
            });
        </script>
    </body>
</html>
"""

STOPWORD = "STOP"

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


@app.get("/publish")
async def get_publish(channel: str = "first_app:channel", message: str = "Hello world!", redis: Redis = Depends(depends_redis)):
    await redis.publish(channel=channel, message=message)
    return ""
