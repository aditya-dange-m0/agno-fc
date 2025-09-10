import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, constr
from bson import ObjectId

# Environment variables
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

class Todo(BaseModel):
    title: str
    description: str
    completed: bool = False

@app.post("/todos/", response_model=Todo)
async def create_todo(todo: Todo):
    todo_dict = todo.dict()
    result = await db.todos.insert_one(todo_dict)
    return JSONResponse(status_code=201, content={"_id": str(result.inserted_id), **todo_dict})

@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: str):
    todo = await db.todos.find_one({"_id": ObjectId(todo_id)})
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.delete("/todos/{todo_id}", response_model=dict)
async def delete_todo(todo_id: str):
    result = await db.todos.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"status": "Todo deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}