from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Environment variables for security
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.task_management

# Password hashing context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# User model
class User(BaseModel):
    username: str
    password: str

class UserInDB(User):
    hashed_password: str

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    description: str = None
    completed: bool = False

@app.post('/register', response_model=User)
async def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    await db.users.insert_one(user_in_db.dict())
    return user

@app.post('/login')
async def login(user: User):
    db_user = await db.users.find_one({'username': user.username})
    if not db_user or not pwd_context.verify(user.password, db_user['hashed_password']):
        raise HTTPException(status_code=400, detail='Invalid credentials')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get("/tasks/", response_model=List[Task])
async def list_tasks():
    tasks = await db.tasks.find().to_list(100)
    return tasks

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    task_dict = task.dict(exclude_unset=True)
    result = await db.tasks.insert_one(task_dict)
    task.id = str(result.inserted_id)
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task: Task):
    await db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': task.dict(exclude_unset=True)})
    return task

@app.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({'_id': ObjectId(task_id)})
    if result.deleted_count == 1:
        return {'status': 'success'}
    raise HTTPException(status_code=404, detail='Task not found')

@app.get('/health')
async def health_check():
    return {'status': 'ok'}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)