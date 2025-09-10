from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from auth.deps import get_current_user, permission_for_project, require_roles
from repositories import project_repository
from repositories.auditlog_repository import create_audit_log
from database import redis

router = APIRouter()

@router.post("/", dependencies=[Depends(require_roles(["project_manager", "admin"]))])
async def create_project(payload: dict, user: dict = Depends(get_current_user)):
    payload.setdefault("owner_id", user.get("id"))
    created = await project_repository.create_project(payload)
    # invalidate cache
    await redis.delete("projects:summary")
    await create_audit_log({"resource_type": "project", "resource_id": created.get("id"), "action": "created", "user_id": user.get("id")})
    return created

@router.get("/", tags=["projects"])
async def list_projects(limit: int = Query(20, le=100), offset: int = 0):
    # Simple caching for project summaries
    cached = None
    try:
        cached = await redis.get("projects:summary")
    except Exception:
        cached = None
    if cached:
        import json
        return json.loads(cached)[offset:offset+limit]
    items = await project_repository.list_projects(limit=limit, skip=offset)
    try:
        import json
        await redis.set("projects:summary", json.dumps(items), ex=60)
    except Exception:
        pass
    return items

@router.post("/{project_id}/team")
async def add_team_member(project_id: str, member: dict, user: dict = Depends(permission_for_project(project_id, ["project_manager", "admin"]))):
    # member: {user_id: str, role: str}
    member_user_id = member.get("user_id")
    role = member.get("role")
    if not member_user_id or not role:
        raise HTTPException(status_code=400, detail="user_id and role required")
    updated = await project_repository.add_team_member(project_id, member_user_id, role)
    await create_audit_log({"resource_type": "project", "resource_id": project_id, "action": "team_add", "user_id": user.get("id"), "details": {"member_id": member_user_id, "role": role}})
    await redis.delete("projects:summary")
    return updated

@router.patch("/{project_id}/team")
async def update_team_member(project_id: str, member: dict, user: dict = Depends(permission_for_project(project_id, ["project_manager", "admin"]))):
    member_user_id = member.get("user_id")
    role = member.get("role")
    if not member_user_id or not role:
        raise HTTPException(status_code=400, detail="user_id and role required")
    updated = await project_repository.update_team_member(project_id, member_user_id, role)
    await create_audit_log({"resource_type": "project", "resource_id": project_id, "action": "team_update", "user_id": user.get("id"), "details": {"member_id": member_user_id, "role": role}})
    await redis.delete("projects:summary")
    return updated

@router.get("/{project_id}/wbs")
async def get_wbs(project_id: str):
    # returns nested tree of tasks
    wbs = await project_repository.get_wbs(project_id)
    return wbs