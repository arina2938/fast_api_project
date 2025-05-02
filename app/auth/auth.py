"""Модуль для аутентификации и работы с JWT токенами."""

# Стандартные библиотеки
from datetime import datetime, timedelta, timezone
from typing import Annotated

# Сторонние библиотеки
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

# Локальные модули
from app.config import settings
from app.database import get_session
from app.models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)


def get_password_hash(password: str) -> str:
    """Генерирует хеш пароля.

    Args:
        password (str): Пароль в чистом виде

    Returns:
        str: Хеш пароля
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и его хеша.

    Args:
        plain_password (str): Пароль в чистом виде
        hashed_password (str): Захешированный пароль

    Returns:
        bool: True если пароли совпадают
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
) -> str:
    """Создает JWT токен доступа.

    Args:
        data (dict): Данные для кодирования в токен
        expires_delta (timedelta | None): Время жизни токена

    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algo
    )
    return encoded_jwt


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db_session: Session = Depends(get_session)
) -> User:
    """Получает текущего пользователя по JWT токену.

    Args:
        token (str): JWT токен
        db_session (Session): Сессия базы данных

    Returns:
        User: Объект пользователя

    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algo]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    statement = select(User).where(User.email == username)
    user = db_session.scalars(statement).first()

    if user is None:
        raise credentials_exception
    return user
