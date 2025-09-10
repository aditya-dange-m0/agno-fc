from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator
from core.config import settings
import aioredis

client: AsyncIOMotorClient | None = None
redis: aioredis.Redis | None = None
db = None

async def connect_to_mongo_and_redis():
    global client, db, redis
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        # verify connection
        await client.admin.command('ping')
        db = client[settings.DATABASE_NAME]
        # connect to redis
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.ping()
        print("Connected to MongoDB and Redis")
    except Exception as e:
        print("DB/Redis connection error:", e)
        raise

async def close_connections():
    global client, redis
    if client:
        client.close()
    if redis:
        await redis.close()