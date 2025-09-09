from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class ExpenseModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    description: str
    amount: float
    category: str
    date: str

class IncomeModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    source: str
    amount: float
    date: str