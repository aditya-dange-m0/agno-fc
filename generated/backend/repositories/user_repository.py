from database import db
from typing import Optional
from bson import ObjectId
from datetime import datetime

USERS_COLL = "users"

async def create_user(user_doc: dict) -> dict:
    user_doc["created_at"] = datetime.utcnow()
    res = await db[USERS_COLL].insert_one(user_doc)
    user_doc["_id"] = res.inserted_id
    return {"id": str(res.inserted_id), "email": user_doc.get("email")}

async def find_user_by_email(email: str) -> Optional[dict]:
    doc = await db[USERS_COLL].find_one({"email": email})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

async def find_user_by_id(user_id: str) -> Optional[dict]:
    if not ObjectId.is_valid(user_id):
        return None
    doc = await db[USERS_COLL].find_one({"_id": ObjectId(user_id)})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc