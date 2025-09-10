from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from core.config import settings
from database import redis
import uuid

class TokenService:
    @staticmethod
    def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode = {"exp": expire, "sub": subject}
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except Exception:
            return None

    @staticmethod
    async def create_refresh_token(user_id: str) -> str:
        # rotation: create new token id and store mapping in redis with TTL
        token_id = str(uuid.uuid4())
        token = jwt.encode({"jti": token_id, "sub": user_id}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        # store token_id -> user_id
        await redis.set(f"refresh:{token_id}", user_id, ex=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
        return token

    @staticmethod
    async def rotate_refresh_token(old_token: str) -> Optional[str]:
        try:
            payload = jwt.decode(old_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            token_id = payload.get("jti")
            user_id = payload.get("sub")
            if not token_id or not user_id:
                return None
        except Exception:
            return None
        # revoke old token atomically: use GETDEL if available, else get+del
        stored = await redis.get(f"refresh:{token_id}")
        if not stored:
            # token already revoked
            return None
        # consume old
        await redis.delete(f"refresh:{token_id}")
        # create new
        return await TokenService.create_refresh_token(user_id)

    @staticmethod
    async def revoke_refresh_token(token: str) -> None:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            token_id = payload.get("jti")
            if token_id:
                await redis.delete(f"refresh:{token_id}")
        except Exception:
            pass