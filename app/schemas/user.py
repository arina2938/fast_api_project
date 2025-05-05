"""Pydantic-схемы для работы с пользователями"""

from pydantic import BaseModel, EmailStr, Field
from app.models.models import UserRole
from typing import List, Optional
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    phone_number: int = Field(
        description="Номер телефона в формате 8xxxxxxxxxx",
        examples=["89001234567"]
    )
    full_name: str
    user_password: str = Field(..., min_length=6)

    role: UserRole = Field(
        description="Тип учетной записи: listener, organization, admin",
        examples=["listener", "organization"]
    )

    class Config:
        orm_mode = True

class UserRead(UserCreate):
    id: int
    verified: bool

    class Config:
        orm_mode = True


class PreferenceCreate(BaseModel):
    instrument_id: Optional[int] = None
    composer_id: Optional[int] = None


class PreferenceResponse(PreferenceCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    limit: int = 10
    include_upcoming: bool = True
    include_completed: bool = False
