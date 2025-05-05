"""Роутер для работы с композиторами."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.models import User
from app.models.models import Composer
from app.schemas import composer as schemas
from app.database import get_session
from ..auth.auth import get_current_user

router = APIRouter(prefix="/composers", tags=["Композиторы"])

@router.post("/", response_model=schemas.ComposerRead, status_code=status.HTTP_201_CREATED,
             summary='Добавить нового композитора в список')
def create_composer(
    composer_data: schemas.ComposerCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создает нового композитора в базе данных.

    Проверяет, существует ли композитор с таким именем. Если существует,
    возвращает ошибку. В противном случае добавляет нового композитора в базу данных.

    Args:
        composer_data (schemas.ComposerCreate): Данные о композиторе.
        db (Session): Сессия базы данных.
        current_user (User): Текущий авторизованный пользователь.

    Raises:
        HTTPException: Если композитор с таким именем уже существует.

    Returns:
        Composer: Созданный композитор.
    """
    existing_composer = db.query(Composer).filter(Composer.name == composer_data.name).first()
    if existing_composer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Композитор с таким именем уже существует"
        )

    db_composer = Composer(
        name=composer_data.name,
        birth_year=composer_data.birth_year,
        death_year=composer_data.death_year
    )
    db.add(db_composer)
    db.commit()
    db.refresh(db_composer)
    return db_composer

@router.get("/", response_model=List[schemas.ComposerRead],
             summary='Получить список всех композиторов')
def read_composers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    """
    Получает список всех композиторов из базы данных с возможностью
    указания параметров для пропуска и ограничения количества записей.

    Args:
        skip (int): Количество записей для пропуска (по умолчанию 0).
        limit (int): Максимальное количество записей для получения (по умолчанию 100).
        db (Session): Сессия базы данных.

    Returns:
        List[Composer]: Список композиторов.
    """
    composers = db.query(Composer).offset(skip).limit(limit).all()
    return composers

@router.get("/{composer_id}", response_model=schemas.ComposerRead,
             summary='Получить композитора по id')
def read_composer(composer_id: int, db: Session = Depends(get_session),
                  current_user: User = Depends(get_current_user)):
    """
    Получает композитора по его ID.

    Если композитор с указанным ID не найден, возвращает ошибку.

    Args:
        composer_id (int): ID композитора.
        db (Session): Сессия базы данных.
        current_user (User): Текущий авторизованный пользователь.

    Raises:
        HTTPException: Если композитор с таким ID не найден.

    Returns:
        Composer: Композитор с указанным ID.
    """
    composer = db.get(Composer, composer_id)
    if not composer:
        raise HTTPException(status_code=404, detail="Композитор не найден")
    return composer
