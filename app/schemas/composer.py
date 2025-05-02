"""Схемы Pydantic для работы с данными о композиторах."""

from typing import Optional

from pydantic import BaseModel, Field


class ComposerBase(BaseModel):
    """Базовая схема для композитора."""
    name: str = Field(
        description="Полное имя композитора в формате 'Имя Отчество Фамилия' (при наличии отчества)",
        examples=["Иоганн Себастьян Бах", "Людвиг ван Бетховен", "Сергей Васильевич Рахманинов"]
    )
    birth_year: Optional[int] = Field(
        default=None,
        description="Год рождения композитора",
        examples=[1685]
    )
    death_year: Optional[int] = Field(
        default=None,
        description="Год смерти композитора",
        examples=[1750]
    )


class ComposerCreate(ComposerBase):
    """Схема для создания нового композитора."""
    pass


class ComposerRead(ComposerBase):
    """Схема для чтения данных о композиторе (с id)."""
    id: int

    class Config:
        from_attributes = True  # Позволяет Pydantic работать с ORM-моделями (SQLAlchemy)
