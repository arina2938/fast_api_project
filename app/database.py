"""Модуль для работы с базой данных."""

# Стандартные библиотеки
from contextlib import contextmanager

# Сторонние библиотеки
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_session():
    """Генератор сессий базы данных.

    Yields:
        Session: Сессия базы данных

    Пример использования:
        with get_session() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Инициализирует базу данных, создавая все таблицы."""
    Base.metadata.create_all(bind=engine)
