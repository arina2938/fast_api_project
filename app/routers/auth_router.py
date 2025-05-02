from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from app.core.database import get_session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..auth import auth
from app.core.config import settings
from datetime import timedelta
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.models.models import User
from ..schemas import user as schema_user
from ..models.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Безопасность"]
)
@router.post("/login", status_code=status.HTTP_200_OK,
             summary = 'Войти в систему')
def user_login(login_attempt_data: OAuth2PasswordRequestForm = Depends(),
               db_session = Depends(get_session)):
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



@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=schema_user.UserRead,
             summary = 'Регистрация пользователя')
def create_user(user: schema_user.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Пользователь с email {user.email} уже существует.")

    if user.role not in ["listener", "organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поле 'role' может принимать только значения 'listener','organization'."
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

