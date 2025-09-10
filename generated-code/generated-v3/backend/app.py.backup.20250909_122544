from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List

app = FastAPI()
client = AsyncIOMotorClient('mongodb://localhost:27017')  # Update with your MongoDB connection string
db = client.task_management

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    description: str = None
    completed: bool = False

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    task_dict = task.dict(exclude_unset=True)
    result = await db.tasks.insert_one(task_dict)
    task.id = str(result.inserted_id)
    return task

@app.get("/tasks/", response_model=List[Task])
async def list_tasks():
    tasks = await db.tasks.find().to_list(100)
    return tasks

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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)