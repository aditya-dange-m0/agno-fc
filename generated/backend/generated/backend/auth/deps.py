from fastapi import Depends, HTTPException, status, Request
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer
from services.token_service import TokenService
from repositories.user_repository import find_user_by_id
from core.config import settings
from database import redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

class PermissionError(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Validate access token and return user document. Raises 401 on invalid token."""
    payload = TokenService.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = await find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return user

async def require_roles(allowed_roles: List[str], user: dict = Depends(get_current_user)) -> dict:
    """Dependency that enforces allowed global roles or project scoped roles on user document."""
    # global roles check
    roles = user.get("roles", [])
    for r in allowed_roles:
        if r in roles:
            return user
    # No global role match — role must be checked at endpoint with project context
    raise PermissionError("User lacks required role")

async def permission_for_project(project_id: str, allowed_project_roles: List[str], user: dict = Depends(get_current_user)) -> dict:
    """Check user's project-scoped role. Expects project membership stored on user or project doc.

    This implementation checks membership on user['projects'] mapping: {project_id: role}
    """
    projects = user.get("projects", {})
    role = projects.get(project_id)
    if role and role in allowed_project_roles:
        return user
    # Allow admins
    if "admin" in user.get("roles", []):
        return user
    raise PermissionError("User lacks required project role")