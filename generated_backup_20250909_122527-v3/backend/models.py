from pydantic import BaseModel, Field
from bson import ObjectId

class TaskModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    description: str = None
    completed: bool = False