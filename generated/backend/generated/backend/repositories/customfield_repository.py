from database import db
from datetime import datetime

COLL = "custom_field_definitions"

async def create_custom_field(doc: dict) -> dict:
    doc["created_at"] = datetime.utcnow()
    res = await db[COLL].insert_one(doc)
    created = await db[COLL].find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created

async def list_custom_fields(resource_type: str) -> list:
    cursor = db[COLL].find({"resource_type": resource_type}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items