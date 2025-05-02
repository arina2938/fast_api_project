from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    phone_number: int =  Field(
        description="Номер телефона в формате 8xxxxxxxxxx",
        examples=["89001234567"]
    )
    full_name: str
    user_password: str = Field(..., min_length=6)
    role: Literal["listener", "organization", "admin"] = Field(
        description="Тип учетной записи: listener, organization, admin",
        examples=["listener", "organization", "admin"]
    )
    #verified : bool = Field(
    #    description="Верификация организации администратором", )
    class Config:
        orm_mode = True

class UserRead(UserCreate):
    id: int
    full_name: str
    email: EmailStr
    phone_number: int
    role: str
    verified: bool

    class Config:
        orm_mode = True