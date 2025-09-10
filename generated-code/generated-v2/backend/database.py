from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_DETAILS = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.get_default_database() 

async def fetch_all_users():
    users = []
    cursor = db.users.find()
    async for document in cursor:
        users.append(document)
    return users

async def fetch_user_by_id(user_id: str):
    return await db.users.find_one({"_id": ObjectId(user_id)})

# Note: Additional database operations (create, update, delete) can be added here.