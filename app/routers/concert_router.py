"""Роутер для управления концертами."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select
from app.database import get_session
from app.models.models import (Concert, User, ConcertStatus,
                               Composer, Instrument, ConcertComposer,
                               ConcertInstrument, UserRole)
from app.schemas import concert as schemas
from ..auth.auth import get_current_user


router = APIRouter(prefix="/concerts", tags=["Концерты"])


@router.post("/",
             response_model=schemas.ConcertRead,
             status_code=status.HTTP_201_CREATED,
             summary='Создать концерт')
def create_concert(
        concert_data: schemas.ConcertCreate,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ORG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на создание концерта."
        )
    if not concert_data.location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Требуется ввести место проведения"
        )
    if concert_data.date < datetime.now(timezone.utc):
        raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно создать концерт с прошедшей датой"
        )

    new_concert = Concert(
        title=concert_data.title,
        date=concert_data.date,
        description=concert_data.description,
        price_type=concert_data.price_type,
        price_amount=concert_data.price_amount,
        location=concert_data.location,
        organization_id=current_user.id
    )

    db.add(new_concert)
    db.flush()  # чтобы получить new_concert.id без коммита

    if concert_data.composers:
        for composer_id in concert_data.composers:
            concert_composer = ConcertComposer(
                concert_id=new_concert.id,
                composer_id=composer_id
            )
            db.add(concert_composer)

    if concert_data.instruments:
        for instrument_id in concert_data.instruments:
            concert_instrument = ConcertInstrument(
                concert_id=new_concert.id,
                instrument_id=instrument_id
            )

            db.add(concert_instrument)


    db.commit()
    db.refresh(new_concert)

    return new_concert




@router.get("/",
            response_model=List[schemas.ConcertRead],
            summary='Получить концерты с фильтрацией по статусу',
            description="Возвращает список концертов с возможностью фильтрации по статусу")
def get_concerts(
        status_of_concert: schemas.ConcertStatus | None = Query(
            default=None,
            description="Фильтр по статусу концерта",
            examples=["upcoming", "completed", "cancelled"]
        ),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_session)
):
    query = db.query(Concert).options(
        joinedload(Concert.concert_composers).joinedload(ConcertComposer.composer),
        joinedload(Concert.concert_instruments).joinedload(ConcertInstrument.instrument)
    )

    if status_of_concert:
        query = query.filter(Concert.current_status == status_of_concert.value)

    concerts = query.offset(skip).limit(limit).all()

    result = []
    for concert in concerts:
        concert_dict = {
            "id": concert.id,
            "title": concert.title,
            "date": concert.date,
            "description": concert.description,
            "price_type": concert.price_type,
            "price_amount": concert.price_amount,
            "location": concert.location,
            "current_status": concert.current_status,
            "organization_id": concert.organization_id,
            "composers": [
                {
                    "id": cc.composer.id,
                    "name": cc.composer.name,
                    "birth_year": cc.composer.birth_year,
                    "death_year": cc.composer.death_year
                } for cc in concert.concert_composers
            ],
            "instruments": [
                {
                    "id": ci.instrument.id,
                    "name": ci.instrument.name
                } for ci in concert.concert_instruments
            ]
        }
        result.append(concert_dict)

    return result

@router.get("/{concert_id}",
            response_model=schemas.ConcertRead,
            status_code=status.HTTP_200_OK,
            summary='Получить концерт по concert_id')
def read_concert(
        concert_id: int,
        db: Session = Depends(get_session)
):
    concert = db.query(Concert).options(
        joinedload(Concert.concert_composers).joinedload(ConcertComposer.composer),
        joinedload(Concert.concert_instruments).joinedload(ConcertInstrument.instrument)
    ).filter(Concert.id == concert_id).first()

    if not concert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Концерт не найден"
        )

    # Преобразуем данные в нужный формат
    concert.composers = [schemas.ComposerRead.from_orm(cc.composer) for cc in concert.concert_composers]
    concert.instruments = [schemas.InstrumentRead.from_orm(ci.instrument) for ci in concert.concert_instruments]

    return concert


@router.patch("/{concert_id}",
              response_model=schemas.ConcertUpdateInfo,
              status_code=status.HTTP_200_OK,
              summary='Изменить информацию о концерте')
def update_concert(
        concert_id: int,
        concert_data: schemas.ConcertUpdateInfo,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    concert = db.get(Concert, concert_id)
    if not concert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Концерт не найден"
        )
    #if current_user.role != "admin":
    if concert.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь организатором этого концерта"
        )

    data = concert_data.model_dump(exclude_unset=True)

     #Проверка даты при обновлении
    if "date" in data:
        new_date = data["date"]
        if new_date < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невозможно установить дату концерта раньше сегодняшней"
            )

    for key, value in data.items():
        setattr(concert, key, value)

    db.add(concert)
    db.commit()
    db.refresh(concert)

    return concert


@router.patch(
    "/{concert_id}/cancel",
    response_model=schemas.ConcertRead,
    summary="Отменить концерт",
    description="Меняет статус концерта на 'cancelled' без удаления записи"
)
def cancel_concert(
        concert_id: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    concert = db.query(Concert).get(concert_id)
    if not concert:
        raise HTTPException(404, "Концерт не найден")

    #if current_user.role != "admin":
    if current_user.role != UserRole.ORG:
        raise HTTPException(403, "Нет прав на отмену")

    # Проверка даты концерта
    concert_date = concert.date
    if concert_date.tzinfo is None:
        concert_date = concert_date.replace(tzinfo=timezone.utc)

    if concert_date < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя отменить уже прошедший концерт"
        )

    # Проверка текущего статуса
    if concert.current_status == ConcertStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Концерт уже отменен"
        )

    concert.current_status = ConcertStatus.CANCELLED

    db.commit()
    db.refresh(concert)

    return concert


@router.delete("/{concert_id}",
               status_code=status.HTTP_200_OK,
               summary='Удалить запись о концерте')
def delete_concert(
        concert_id: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    concert = db.get(Concert, concert_id)
    if not concert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Концерт не найден"
        )

    #if current_user.role != "admin":
    if concert.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь организатором этого концерта"
        )
    db.refresh(concert)

    #if concert.current_status not in [ConcertStatus.CANCELLED, ConcertStatus.COMPLETED]:
    #    raise HTTPException(
    #        status_code=status.HTTP_400_BAD_REQUEST,
    #        detail="Можно удалить только отменённый или завершённый концерт"
    #    )
    db.query(ConcertComposer).filter_by(concert_id=concert_id).delete()

    db.query(ConcertInstrument).filter_by(concert_id=concert_id).delete()

    db.delete(concert)
    db.commit()

    return {"message": "Концерт успешно удален"}



@router.get("/filter/", response_model=List[schemas.ConcertRead],
            summary='Найти концерт по дате/инструменту/композитору')
def filter_concerts(
    date: Optional[datetime] = None,
    composer_names: Optional[List[str]] = Query(None),
    instrument_names: Optional[List[str]] = Query(None),
    db: Session = Depends(get_session)
):
    query = db.query(Concert).options(
        joinedload(Concert.concert_composers).joinedload(ConcertComposer.composer),
        joinedload(Concert.concert_instruments).joinedload(ConcertInstrument.instrument)
    ).filter(Concert.current_status == ConcertStatus.UPCOMING)

    if date:
        query = query.filter(Concert.date == date)

    if composer_names:
        query = query.join(Concert.concert_composers).join(ConcertComposer.composer).filter(
            Composer.name.in_(composer_names)
        )

    if instrument_names:
        query = query.join(Concert.concert_instruments).join(ConcertInstrument.instrument).filter(
            Instrument.name.in_(instrument_names)
        )
    concerts = query.all()

    return concerts
