from pydantic import BaseModel, Field

class InstrumentBase(BaseModel):
    name: str  = Field(
        description="Рекомендуется писать инструмент в единственном числе, кроме несклоняемых, "
                    "или Духовой орекстр /Симфонический орекстр, если инструментов много",
        examples=["Скрипка", "Гусли", "Симфонический оркестр"]
    )

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentRead(InstrumentBase):
    id: int

    class Config:
        from_attributes = True