from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ProjectCreate
from repositories import project_repository
from bson import ObjectId
from typing import Any

router = APIRouter()

@router.post("/")
async def create_project(payload: ProjectCreate):
    doc = payload.model_dump()
    created = await project_repository.create_project(doc)
    return {"project_id": created.get("id"), "key": created.get("key")}

@router.get("/{project_id}")
async def get_project(project_id: str):
    proj = await project_repository.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    # include simple aggregated counts - stub
    proj["aggregates"] = {"tasks": 0, "open_issues": 0, "spent_hours": 0}
    return proj

@router.patch("/{project_id}")
async def patch_project(project_id: str, patch: dict):
    # simple lifecycle validation example
    allowed_transitions = {
        "ideation": ["proposal"],
        "proposal": ["planning"],
        "planning": ["active"],
        "active": ["on_hold", "completed"],
    }
    if "status" in patch:
        current = (await project_repository.get_project(project_id))
        if not current:
            raise HTTPException(status_code=404, detail="Project not found")
        cur_status = current.get("status")
        desired = patch.get("status")
        if cur_status == desired:
            pass
        elif desired not in allowed_transitions.get(cur_status, []):
            raise HTTPException(status_code=400, detail=f"Invalid status transition {cur_status} -> {desired}")
    updated = await project_repository.update_project(project_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project_id": updated.get("id"), "status": updated.get("status")}