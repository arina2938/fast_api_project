from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_session
from app.models.models import Instrument
from app.schemas import instrument as schemas
from app.core.database import get_session
from app.models.models import  User
from ..auth.auth import get_current_user

router = APIRouter(prefix="/instruments", tags=["Инструменты"])

@router.post("/", response_model=schemas.InstrumentRead, status_code=status.HTTP_201_CREATED,
             summary = 'Добавить новый инструмент в список')
def create_instrument(
    instrument_data: schemas.InstrumentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    existing_instrument = db.query(Instrument).filter(Instrument.name == instrument_data.name).first()
    if existing_instrument:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Инструмент с таким именем уже существует"
        )
    db_instrument = Instrument(name=instrument_data.name)
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument

@router.get("/", response_model=List[schemas.InstrumentRead],
             summary = 'Получить список всех инструментов')
def read_instruments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    instruments = db.query(Instrument).offset(skip).limit(limit).all()
    return instruments

@router.get("/{instrument_id}", response_model=schemas.InstrumentRead,
             summary = 'Получить инструмент по id')
def read_instrument(instrument_id: int, db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)):
    instrument = db.get(Instrument, instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    return instrument