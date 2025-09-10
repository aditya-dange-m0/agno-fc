from fastapi import APIRouter, HTTPException
from models.schemas import TaskCreate
from repositories import project_repository
from database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_task(payload: TaskCreate):
    # validate project exists
    proj = await project_repository.get_project(payload.project_id)
    if not proj:
        raise HTTPException(status_code=400, detail="Project does not exist")
    doc = payload.model_dump()
    doc.update({"status": "todo", "created_at": datetime.utcnow()})
    res = await db["tasks"].insert_one(doc)
    return {"task_id": str(res.inserted_id)}

@router.get("/{task_id}")
async def get_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid id")
    doc = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    # include subtasks stub
    doc["subtasks"] = []
    return doc

@router.patch("/{task_id}")
async def patch_task(task_id: str, patch: dict):
    # enforce simple status transitions
    allowed = {
        "todo": ["in_progress"],
        "in_progress": ["blocked", "review", "done"],
        "review": ["done"],
        "done": ["closed"]
    }
    doc = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")
    cur = doc.get("status", "todo")
    if "status" in patch:
        target = patch.get("status")
        if target == cur:
            pass
        elif target not in allowed.get(cur, []):
            raise HTTPException(status_code=400, detail=f"Invalid status transition {cur} -> {target}")
    patch["updated_at"] = datetime.utcnow()
    await db["tasks"].update_one({"_id": ObjectId(task_id)}, {"$set": patch})
    updated = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated