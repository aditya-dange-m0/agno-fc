from database import db
from bson import ObjectId
from datetime import datetime

COLL = "issues"

async def create_issue(doc: dict) -> dict:
    doc.setdefault("status", "open")
    doc["created_at"] = datetime.utcnow()
    res = await db[COLL].insert_one(doc)
    created = await db[COLL].find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created

async def get_issue(issue_id: str) -> dict | None:
    if not ObjectId.is_valid(issue_id):
        return None
    doc = await db[COLL].find_one({"_id": ObjectId(issue_id)})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc