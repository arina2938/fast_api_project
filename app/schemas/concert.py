"""Pydantic-схемы для работы с концертами"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.models import ConcertStatus
from app.schemas.instrument import InstrumentRead
from app.schemas.composer import ComposerRead

class ConcertBase(BaseModel):
    """Базовая схема для концерта."""
    title: str = Field(description="Название концерта")
    date: datetime = Field(description="Дата и время проведения концерта")
    description: Optional[str] = Field(
        default=None,
        description="Описание концерта"
    )
    price_type: str = Field(description="Тип цены: бесплатно или платно")
    price_amount: Optional[int] = Field(
        default=None,
        description="Стоимость билета в рублях, если цена указана"
    )
    location: str = Field(description="Место проведения концерта")
    composers: Optional[List[int]] = Field(
        default_factory=list,
        description="Список id композиторов, чьи произведения прозвучат"
    )
    instruments: Optional[List[int]] = Field(
        default_factory=list,
        description="Список id инструментов, задействованных в концерте"
    )


class ConcertCreate(ConcertBase):
    """Схема для создания нового концерта."""
    pass


class ConcertRead(ConcertBase):
    """Схема для чтения данных о концерте."""
    id: int
    organization_id: int
    current_status: ConcertStatus
    composers: List[ComposerRead] = Field(default_factory=list)
    instruments: List[InstrumentRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConcertUpdateInfo(BaseModel):
    """Схема для обновления информации о концерте."""
    title: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    price_type: Optional[str] = None
    price_amount: Optional[int] = None
    location: Optional[str] = None
    composers: Optional[List[int]] = None
    instruments: Optional[List[int]] = None
