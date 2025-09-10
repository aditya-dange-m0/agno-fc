from database import db
from bson import ObjectId
from datetime import datetime

COLL = "time_entries"

async def create_time_entry(doc: dict) -> dict:
    doc["created_at"] = datetime.utcnow()
    res = await db[COLL].insert_one(doc)
    created = await db[COLL].find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created

async def list_time_entries(task_id: str, limit: int = 50, skip: int = 0) -> list:
    cursor = db[COLL].find({"task_id": task_id}).sort("start_time", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items