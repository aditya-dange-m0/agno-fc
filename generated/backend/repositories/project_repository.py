from database import db
from bson import ObjectId
from datetime import datetime

COLL = "projects"

async def create_project(doc: dict) -> dict:
    doc.setdefault("status", "ideation")
    doc["created_at"] = datetime.utcnow()
    res = await db[COLL].insert_one(doc)
    created = await db[COLL].find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created

async def get_project(project_id: str) -> dict | None:
    if not ObjectId.is_valid(project_id):
        return None
    doc = await db[COLL].find_one({"_id": ObjectId(project_id)})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

async def update_project(project_id: str, patch: dict) -> dict | None:
    if not ObjectId.is_valid(project_id):
        return None
    patch["updated_at"] = datetime.utcnow()
    await db[COLL].update_one({"_id": ObjectId(project_id)}, {"$set": patch})
    return await get_project(project_id)