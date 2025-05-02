from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.models import ConcertStatus
from typing import List, Optional


class ConcertBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str] = None
    price_type: str
    price_amount: Optional[int] = None
    location: str
    composers: Optional[List[int]] = Field(default_factory=list)
    instruments: Optional[List[int]] = Field(default_factory=list)

class ConcertCreate(ConcertBase):
    pass
class ComposerRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class InstrumentRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
class ConcertRead(ConcertBase):
    id: int
    organization_id: int
    current_status: ConcertStatus
    #composers: List[ComposerRead] = []
    #instruments: List[InstrumentRead] = []

    #class Config:
    #    orm_mode = True

class ConcertUpdateInfo(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    price_type: Optional[str] = None
    price_amount: Optional[int] = None
    location: Optional[str] = None
    composers: Optional[List[int]] = None
    instruments: Optional[List[int]] = None
