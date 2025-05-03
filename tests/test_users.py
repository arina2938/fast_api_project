import pytest
from fastapi.testclient import TestClient
from fastapi import status
from faker import Faker
from app.main import app
from app.models.models import UserRole
from app.database import Base, get_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

fake = Faker()
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user_data():
    return {
        "email": fake.email(),
        "phone_number": 89999999999,
        "full_name": fake.name(),
        "user_password": fake.password(length=12),
        "role": UserRole.LISTENER.value
    }

def test_signup_success(client, test_user_data):
    response = client.post("/auth/signup", json=test_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert "id" in response_data
    assert response_data["email"] == test_user_data["email"]


def test_login_success(client, test_user_data):
    # Сначала регистрируем пользователя
    client.post("/auth/signup", json=test_user_data)

    # Пытаемся войти
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["user_password"]
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


