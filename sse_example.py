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


@app.get("/sse/demo")
async def get():
    return HTMLResponse(html)


@app.get("/sse/publish")
async def get_publish(channel: str = "example_channel", message: str = "Hello world!", redis: Redis = Depends(depends_redis)):
    await redis.publish(channel=channel, message=message)
    return ""


@app.get("/sse/stream")
async def stream(channel: str = "example:channel", redis: Redis = Depends(depends_redis)):
    pub_sub_reader = redis.pubsub()
    return EventSourceResponse(subscribe(channel, pub_sub_reader))


async def subscribe(channel: str, pub_sub: PubSub):
    async with pub_sub as p:
        await p.subscribe(channel)
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await p.get_message(ignore_subscribe_messages=True)
                    if message:
                        if message.get('data') == STOPWORD:
                            break
                        print(message.get('data'))
                        yield {"event": "message", "data": message.get('data')}
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass
