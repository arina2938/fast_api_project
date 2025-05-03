"""Модуль моделей базы данных SQLAlchemy."""

# Стандартные библиотеки
from enum import Enum
from datetime import datetime, timedelta

# Сторонние библиотеки
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

# Локальные модули
from app.database import Base

class UserRole(str, Enum):
    """Роли пользователей."""

    LISTENER = "listener"
    ORG = "organization"

class User(Base):
    """Модель пользователя системы.

    Attributes:
        id (int): Уникальный идентификатор
        full_name (str): Полное имя пользователя
        email (str): Email (уникальный)
        phone_number (int): Номер телефона
        user_password (str): Хэш пароля
        role (str): Роль (listener/organization)
        verified (bool): Подтвержден ли аккаунт (для организаций)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(Integer, unique=False, nullable=True)
    user_password = Column(String, unique=False, nullable=False)
    role = Column(String, nullable=False)  # "listener" или "organization"
    verified = Column(Boolean, nullable=False)


class ConcertStatus(str, Enum):
    """Статусы концерта."""

    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Concert(Base):
    """Модель концерта.

    Attributes:
        id (int): Уникальный идентификатор
        title (str): Название концерта
        date (DateTime): Дата и время проведения
        description (Text): Описание
        price_type (str): Тип цены (free/fixed/hat)
        price_amount (int): Сумма (если fixed)
        location (str): Место проведения
        current_status (ConcertStatus): Текущий статус
        organization_id (int): ID организатора
    """

    __tablename__ = "concerts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now() + timedelta(weeks=1))
    description = Column(Text)
    price_type = Column(String, nullable=True)
    price_amount = Column(Integer, nullable=True)
    location = Column(String, nullable=False)
    current_status = Column(String, default=ConcertStatus.UPCOMING)
    organization_id = Column(Integer, ForeignKey("users.id"))

    organization = relationship("User")
    concert_composers = relationship("ConcertComposer", back_populates="concert")
    concert_instruments = relationship("ConcertInstrument", back_populates="concert")


class Composer(Base):
    """Модель композитора.

    Attributes:
        id (int): Уникальный идентификатор
        name (str): Имя композитора (уникальное)
        birth_year (int): Год рождения
        death_year (int): Год смерти
    """

    __tablename__ = "composers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    birth_year = Column(Integer, nullable=True)
    death_year = Column(Integer, nullable=True)

    concert_composers = relationship("ConcertComposer", back_populates="composer")


class Instrument(Base):
    """Модель музыкального инструмента.

    Attributes:
        id (int): Уникальный идентификатор
        name (str): Название инструмента (уникальное)
    """

    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    concert_instruments = relationship("ConcertInstrument", back_populates="instrument")


class ConcertComposer(Base):
    """Ассоциативная таблица концерт-композитор."""

    __tablename__ = 'concert_composers'

    concert_id = Column(Integer, ForeignKey('concerts.id'), primary_key=True)
    composer_id = Column(Integer, ForeignKey('composers.id'), primary_key=True)

    concert = relationship("Concert", back_populates="concert_composers")
    composer = relationship("Composer", back_populates="concert_composers")


class ConcertInstrument(Base):
    """Ассоциативная таблица концерт-инструмент."""

    __tablename__ = 'concert_instruments'

    concert_id = Column(Integer, ForeignKey('concerts.id'), primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), primary_key=True)

    concert = relationship("Concert", back_populates="concert_instruments")
    instrument = relationship("Instrument", back_populates="concert_instruments")
