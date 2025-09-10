from database import db
from bson import ObjectId
from datetime import datetime

COLL = "comments"

async def create_comment(doc: dict) -> dict:
    doc["created_at"] = datetime.utcnow()
    res = await db[COLL].insert_one(doc)
    created = await db[COLL].find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created

async def list_comments(resource_type: str, resource_id: str, limit: int = 50, skip: int = 0) -> list:
    cursor = db[COLL].find({"resource_type": resource_type, "resource_id": resource_id}).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items