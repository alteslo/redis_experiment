import asyncio

import json
from fastapi import FastAPI
import async_timeout
import redis.asyncio as redis
from redis.client import PubSub

STOPWORD = "STOP"

app = FastAPI()
client = redis.from_url('redis: // localhost')


@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(consumer("first_app:channel"))


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await client.close()


@app.get("/")
async def root_get() -> dict:
    return dict(ping=await client.ping())


async def get_pubsub(channel: str):
    subscriber = client.pubsub()
    await subscriber.psubscribe(channel)
    return subscriber


async def consumer(channel: str):
    pub_sub: PubSub = await get_pubsub(channel)
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await pub_sub.get_message(ignore_subscribe_messages=True)
                if message:
                    message = json.loads(message.get('data'))
                    print({"event": "message", "data": message})
                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass
