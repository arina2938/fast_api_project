from pydantic import BaseModel, Field
from typing import Optional

class ComposerBase(BaseModel):
    name: str  = Field(
        description="Полное имя композитора в формате Имя Отчество (при наличии) Фамилия",
        examples=["Иоганн Себаастьян Бах", "Людвиг ван Бетховен", "Сергей Васильевич Рахманинов"]
    )
    birth_year: Optional[int] = Field(None, examples=[1685])  # Сделаем необязательным
    death_year: Optional[int] = Field(..., examples=[1750])

class ComposerCreate(ComposerBase):
    pass

class ComposerRead(ComposerBase):
    id: int

    class Config:
        from_attributes = True