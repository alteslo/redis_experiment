import asyncio

import async_timeout
import httpx
from aioredis import Redis
from aioredis.client import PubSub

redis_uri: str = "redis://localhost:6379"
redis = Redis().from_url(redis_uri)
subscriber = redis.pubsub()
STOPWORD = 'STOP'


async def send_to_third_app(channel, message):
    httpx.AsyncClient()
    async with httpx.AsyncClient(base_url='http://localhost:8888/') as client:
        params = {
            'message': message.decode('utf-8'),
            'channel': channel,
        }
        await client.get(url='console_writer', params=params)


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
                        await send_to_third_app(channel, message.get('data'))
                        print({"event": "message", "data": message.get('data')})
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass


if __name__ == '__main__':
    asyncio.run(listener('first_app:channel', subscriber))
