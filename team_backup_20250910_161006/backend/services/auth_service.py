from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import uuid
from core.config import settings
from repositories import user_repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    to_encode = {"sub": subject, "type": "access"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def create_refresh_token(subject: str, jti: str | None = None, expires_delta: timedelta | None = None) -> str:
    jti = jti or str(uuid.uuid4())
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": subject, "jti": jti, "type": "refresh", "exp": expire}
    token = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti

# Simple refresh token storage using Redis is recommended. For the scaffold we store jti in Mongo refresh_tokens collection
from database import db

REFRESH_COLL = "refresh_tokens"

async def store_refresh_token(user_id: str, jti: str, expires_at: datetime):
    await db[REFRESH_COLL].insert_one({"user_id": user_id, "jti": jti, "expires_at": expires_at})

async def revoke_refresh_token(jti: str):
    await db[REFRESH_COLL].update_one({"jti": jti}, {"$set": {"revoked": True}})

async def is_refresh_token_revoked(jti: str) -> bool:
    doc = await db[REFRESH_COLL].find_one({"jti": jti})
    if not doc:
        return True
    return doc.get("revoked", False)

async def register_user(email: str, password: str, full_name: str | None = None) -> dict:
    existing = await user_repository.find_user_by_email(email)
    if existing:
        raise ValueError("User already exists")
    hashed = hash_password(password)
    user_doc = {"email": email, "password_hash": hashed, "full_name": full_name, "roles": ["team_member"], "is_active": True}
    created = await user_repository.create_user(user_doc)
    return created

async def authenticate_user(email: str, password: str) -> dict | None:
    user = await user_repository.find_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.get("password_hash")):
        return None
    return user