from database import db
from datetime import datetime

COLL = "audit_logs"

async def create_audit_log(doc: dict) -> dict:
    doc["created_at"] = datetime.utcnow()
    res = await db[COLL].insert_one(doc)
    created = await db[COLL].find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created