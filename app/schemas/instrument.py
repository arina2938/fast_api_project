"""Pydantic-схемы для работы с инструментами"""

from pydantic import BaseModel, Field

class InstrumentBase(BaseModel):
    name: str = Field(
        description=(
            "Название инструмента в единственном числе (например: 'Скрипка', 'Гусли'). "
            "Если указывается оркестр, напишите, например ('Симфонический оркестр', 'Духовой оркестр')."
        ),
        examples=["Скрипка", "Гусли", "Симфонический оркестр"]
    )

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentRead(InstrumentBase):
    id: int

    class Config:
        from_attributes = True
