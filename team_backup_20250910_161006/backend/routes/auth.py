from fastapi import APIRouter, HTTPException, Depends
from fastapi import status as http_status
from models.schemas import UserCreate
from services import auth_service
from datetime import datetime, timedelta
from core.config import settings
from pydantic import BaseModel
from jose import jwt

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/register")
async def register(payload: UserCreate):
    try:
        created = await auth_service.register_user(payload.email, payload.password, payload.full_name)
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"user_id": created.get("id"), "email": created.get("email"), "message": "Account created"}

class LoginPayload(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginPayload):
    user = await auth_service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = auth_service.create_access_token(user["id"], expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token, jti = auth_service.create_refresh_token(user["id"])
    # store refresh token
    await auth_service.store_refresh_token(user["id"], jti, datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    return {"access_token": access_token, "refresh_token": refresh_token}

class RefreshPayload(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshPayload):
    try:
        data = jwt.decode(payload.refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if data.get("type") != "refresh":
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    jti = data.get("jti")
    user_id = data.get("sub")
    if await auth_service.is_refresh_token_revoked(jti):
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
    # rotate: revoke old and issue new
    await auth_service.revoke_refresh_token(jti)
    new_refresh_token, new_jti = auth_service.create_refresh_token(user_id)
    await auth_service.store_refresh_token(user_id, new_jti, datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    access_token = auth_service.create_access_token(user_id)
    return {"access_token": access_token, "refresh_token": new_refresh_token}