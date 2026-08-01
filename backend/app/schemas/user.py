from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    full_name: str
    email: str


class UserCreate(UserBase):
    password: str
    role: Optional[str] = "Reporter"


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
