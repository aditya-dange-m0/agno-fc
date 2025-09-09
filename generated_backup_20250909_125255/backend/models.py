from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    hashed_password: str
    is_active: bool = True

# Update the existing imports and classes in app.py if needed