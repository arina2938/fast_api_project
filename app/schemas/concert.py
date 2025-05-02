from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.models import ConcertStatus


class ConcertBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str] = None
    price_type: str
    price_amount: Optional[int] = None
    location: str

class ConcertCreate(ConcertBase):
    pass

class ConcertRead(ConcertBase):
    id: int
    organization_id: int
    current_status: ConcertStatus

class ConcertUpdateInfo(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    price_type: Optional[str] = None
    price_amount: Optional[int] = None
    location: Optional[str] = None

