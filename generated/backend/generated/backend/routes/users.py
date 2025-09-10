from fastapi import APIRouter, Depends
from auth.deps import get_current_user

router = APIRouter()

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    # Return sanitized user info
    user_copy = {"id": user.get("id") or user.get("_id"), "email": user.get("email"), "full_name": user.get("full_name"), "roles": user.get("roles", []), "projects": user.get("projects", {})}
    return user_copy