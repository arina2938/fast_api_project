import pytest
from fastapi import status
from faker import Faker
from app.models.models import UserRole
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tests.test_concerts import db_session, client, SQLALCHEMY_DATABASE_URL
fake = Faker()

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    client.post("/auth/signup", json=test_user_data)

    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["user_password"]
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
