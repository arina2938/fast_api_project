"""Роутер для работы с композиторами."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.models import Composer
from app.schemas import composer as schemas
from ..auth.auth import get_current_user
from app.database import get_session
from app.models.models import  User

router = APIRouter(prefix="/composers", tags=["Композиторы"])

@router.post("/", response_model=schemas.ComposerRead, status_code=status.HTTP_201_CREATED,
             summary = 'Добавить нового композтора в списко',

)
def create_composer(
    composer_data: schemas.ComposerCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
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
             summary = 'Получить список всех композиторов')
def read_composers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    composers = db.query(Composer).offset(skip).limit(limit).all()
    return composers

@router.get("/{composer_id}", response_model=schemas.ComposerRead,
             summary = 'Получить композитора по id')
def read_composer(composer_id: int, db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)):
    composer = db.get(Composer, composer_id)
    if not composer:
        raise HTTPException(status_code=404, detail="Композитор не найден")
    return composer
