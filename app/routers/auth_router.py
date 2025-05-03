"""Роутер для аутентификации и регистрации пользователей."""

# Стандартные библиотеки
from datetime import timedelta

# Сторонние библиотеки
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

# Локальные модули
from app.config import settings
from app.database import get_session
from app.models.models import User, UserRole
from app.schemas import user as schema_user
from ..auth import auth

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Войти в систему",
    response_model=dict
)
def user_login(
        login_attempt_data: OAuth2PasswordRequestForm = Depends(),
        db_session: Session = Depends(get_session)
) -> dict:
    """Аутентификация пользователя и выдача JWT токена.

    Args:
        login_attempt_data: Данные для входа (username/password)
        db_session: Сессия базы данных

    Returns:
        dict: Токен доступа и его тип

    Raises:
        HTTPException: Если пользователь не найден или неверный пароль
    """
    statement = select(User).where(User.email == login_attempt_data.username)
    existing_user = db_session.execute(statement).scalar_one_or_none()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {login_attempt_data.username} not found"
        )

    if auth.verify_password(
            login_attempt_data.password,
            existing_user.user_password):
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth.create_access_token(
            data={"sub": login_attempt_data.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password for user {login_attempt_data.username}"
        )


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=schema_user.UserRead,
    summary="Регистрация пользователя"
)
def create_user(user: schema_user.UserCreate, session: Session = Depends(get_session)):
    """Регистрация нового пользователя в системе.

    Args:
        user: Данные нового пользователя
        session: Сессия базы данных

    Returns:
        User: Созданный пользователь

    Raises:
        HTTPException: Если пользователь уже существует или неверная роль
         if user.role not in UserRole.__members__.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Поле 'role' может принимать только значения: {[role.value for role in UserRole]}"
        )
    """
    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Пользователь с email {user.email} уже существует.")

    if user.role not in UserRole.__members__.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Поле 'role' может принимать только значения: {[role.value for role in UserRole]}"
        )

    # Hash the password before storing it
    hashed_password = auth.get_password_hash(user.user_password)

    new_user = User(
        email=str(user.email),
        phone_number=user.phone_number,
        full_name=user.full_name,
        user_password=hashed_password,  # Store the hashed version
        role=user.role,
        verified=False
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)


    return new_user
