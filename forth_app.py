import asyncio

import json
from fastapi import FastAPI
import async_timeout
import redis.asyncio as redis
from redis.client import PubSub

SUBSCRIBE_CHANNELS = ('first_app:channel', 'service:file')

app = FastAPI()
client = redis.from_url('redis://localhost')


@app.on_event('startup')
async def on_startup() -> None:
    asyncio.create_task(listen(SUBSCRIBE_CHANNELS))


@app.on_event('shutdown')
async def on_shutdown() -> None:
    await client.close()


@app.get('/')
async def root_get() -> dict:
    return dict(ping=await client.ping())


async def get_pubsub(channels):
    subscriber = client.pubsub()
    for channel in channels:
        await subscriber.psubscribe(channel)
    return subscriber


async def message_manager(message: dict | None):
    if message:
        channel: str = message.get('channel').decode('utf-8')
        message: dict = json.loads(message.get('data'))
        match channel:
            case 'first_app:channel':
                print({'channel': 'first_app:channel', 'data': message})
            case 'test_app:channel':
                print({'channel': 'Тестовый канал', 'data': message})
            case 'service:file':
                print({'channel': channel, 'data': message})
        


async def listen(*channels):
    subscriber: PubSub = await get_pubsub(*channels)
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await subscriber.get_message(ignore_subscribe_messages=True)
                await message_manager(message)
                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass
