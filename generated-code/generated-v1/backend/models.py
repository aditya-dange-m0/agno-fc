from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class TodoIn(BaseModel):
    title: str
    description: Optional[str] = None
    completed: Optional[bool] = False

class TodoOut(TodoIn):
    id: str

    class Config:
        json_encoders = {
            ObjectId: str,
        }