from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional

app = FastAPI()

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "budget_tracker"

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

class Expense(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    description: str
    amount: float
    category: str
    date: str

class Income(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    source: str
    amount: float
    date: str

@app.post("/expenses/", response_model=Expense)
async def create_expense(expense: Expense):
    expense_data = expense.dict(exclude_unset=True)
    result = await db.expenses.insert_one(expense_data)
    expense.id = str(result.inserted_id)
    return expense

@app.get("/expenses/", response_model=List[Expense])
async def get_expenses():
    expenses = await db.expenses.find().to_list(100)
    return expenses

@app.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(expense_id: str, expense: Expense):
    await db.expenses.update_one({"_id": ObjectId(expense_id)}, {"$set": expense.dict(exclude_unset=True)})
    expense.id = expense_id
    return expense

@app.delete("/expenses/{expense_id}", response_model=dict)
async def delete_expense(expense_id: str):
    result = await db.expenses.delete_one({"_id": ObjectId(expense_id)})
    if result.deleted_count == 1:
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Expense not found")

@app.post("/income/", response_model=Income)
async def create_income(income: Income):
    income_data = income.dict(exclude_unset=True)
    result = await db.income.insert_one(income_data)
    income.id = str(result.inserted_id)
    return income

@app.get("/income/", response_model=List[Income])
async def get_income():
    income = await db.income.find().to_list(100)
    return income

@app.put("/income/{income_id}", response_model=Income)
async def update_income(income_id: str, income: Income):
    await db.income.update_one({"_id": ObjectId(income_id)}, {"$set": income.dict(exclude_unset=True)})
    income.id = income_id
    return income

@app.delete("/income/{income_id}", response_model=dict)
async def delete_income(income_id: str):
    result = await db.income.delete_one({"_id": ObjectId(income_id)})
    if result.deleted_count == 1:
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Income not found")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}