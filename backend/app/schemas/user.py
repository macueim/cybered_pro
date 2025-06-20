# backend/app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "student"  # Default role is student

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Additional properties stored in DB
class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True

# Properties to return via API
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True