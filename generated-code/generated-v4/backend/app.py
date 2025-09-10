from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional
from passlib.context import CryptContext
import jwt
import os

app = FastAPI()

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "budget_tracker"
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

db_client = AsyncIOMotorClient(MONGODB_URL)
db = db_client[DATABASE_NAME]

# User model
class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    hashed_password: str
    is_active: bool = True

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/register/", response_model=User)
async def register_user(user: User):
    user.hashed_password = get_password_hash(user.hashed_password)
    await db.users.insert_one(user.dict(exclude_unset=True))
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Protect existing routes with the dependency
@app.get("/expenses/", response_model=List[Expense])
async def get_expenses(token: str = Depends(oauth2_scheme)):
    expenses = await db.expenses.find().to_list(100)
    return expenses

# Add the same dependency to other protected routes