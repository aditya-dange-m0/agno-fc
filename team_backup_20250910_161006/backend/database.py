from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

client: AsyncIOMotorClient | None = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        # Optionally verify connection with server_info
        await client.admin.command('ping')
        db = client[settings.DATABASE_NAME]
        print("Connected to MongoDB")
    except Exception as e:
        print("MongoDB connection error:", e)
        raise

async def close_mongo_connection():
    global client
    if client:
        client.close()