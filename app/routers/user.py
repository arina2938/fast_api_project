from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.models.models import User
from ..schemas import user as schema_user
router = APIRouter(
    prefix="/registration",
    tags=["Регистрация пользователя"]
)

@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema_user.UserRead,
             summary = 'Регистрация пользователя')
def create_user(user: schema_user.UserCreate, session: Session = Depends(get_session)):

    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Пользователь с email {user.email}  уже существует.")

    if user.role not in ["listener", "organization"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поле 'role' может принимать только значения 'listener' или 'organization'."
        )

    new_user = User(
        email=str(user.email),
        phone_number=user.phone_number,
        full_name=user.full_name,
        hashed_password=user.hashed_password,
        role=user.role,
        verified=False
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user
