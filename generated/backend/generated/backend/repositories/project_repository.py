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

async def list_projects(limit: int = 20, skip: int = 0) -> list:
    cursor = db[COLL].find().sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items

async def add_team_member(project_id: str, user_id: str, role: str) -> dict | None:
    # adds to project.members array and optionally update user.projects mapping should be done by user repo
    await db[COLL].update_one({"_id": ObjectId(project_id)}, {"$addToSet": {"members": {"user_id": user_id, "role": role}}})
    return await get_project(project_id)

async def update_team_member(project_id: str, user_id: str, role: str) -> dict | None:
    await db[COLL].update_one({"_id": ObjectId(project_id), "members.user_id": user_id}, {"$set": {"members.$.role": role}})
    return await get_project(project_id)

async def get_wbs(project_id: str) -> list:
    # Build nested tasks tree using aggregation. For simplicity return tasks list grouped by parent
    tasks = db["tasks"].find({"project_id": project_id}).sort("start_date", 1)
    items = []
    async for t in tasks:
        t["id"] = str(t["_id"])
        t.pop("_id", None)
        items.append(t)
    # naive nesting
    tree = {}
    for t in items:
        tree.setdefault(t.get("parent_id"), []).append(t)
    def build(parent_id=None):
        nodes = []
        for n in tree.get(parent_id, []):
            n["children"] = build(n.get("id"))
            nodes.append(n)
        return nodes
    return build(None)