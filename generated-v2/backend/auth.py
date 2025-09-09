from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from models import UserModel
from database import db

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/auth/register")
async def register(user: UserModel):
    # Hash password
    hashed_password = pwd_context.hash(user.password)  
    user.password = hashed_password
    # Save user to database
    await db.users.insert_one(user.dict())
    return {"message": "User registered successfully"}

@router.post("/auth/login")
async def login(user: UserModel):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # Create JWT token
    token = jwt.encode({"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token}