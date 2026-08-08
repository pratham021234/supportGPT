from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None

class RoleResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: UUID
    is_verified: bool
    is_active: bool
    roles: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
