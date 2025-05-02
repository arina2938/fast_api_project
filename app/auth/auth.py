from datetime import  timezone
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.core.database import get_session
from app.models.models import User
from app.core.config import settings
from fastapi import status, Depends, HTTPException
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy import select


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict,
                        expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = (datetime.now(timezone.utc) +
                  expires_delta)
    else:
        expire = (datetime.now(timezone.utc) +
                  timedelta(minutes=15))

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode,
                             settings.secret_key,
                             algorithm=settings.algo)
    return encoded_jwt


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algo])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(User.email == username)
    user = db_session.scalars(statement).first()

    if user is None:
        raise credentials_exception
    return user