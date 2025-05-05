import pytest
from faker import Faker
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime, timedelta, timezone
from typing import List

from app.main import app
from app.models.models import (
    Concert, ConcertStatus, User, UserRole,
    Composer, Instrument, ConcertComposer, ConcertInstrument
)
from app.database import Base, get_session
from app.auth.auth import get_password_hash, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

fake = Faker()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        org_user = User(
            full_name="org_user",
            email="org@example.com",
            role=UserRole.ORG,
            user_password=get_password_hash("orgpass"),
            phone_number=1234567890,
            verified=False
        )
        db.add(org_user)
        db.flush()

        composer1 = Composer(name="Tchaikovsky")
        composer2 = Composer(name="Mozart")
        instrument1 = Instrument(name="Piano")
        instrument2 = Instrument(name="Violin")
        db.add_all([composer1, composer2, instrument1, instrument2])
        db.flush()

        concert1 = Concert(
            title="Test Concert 1",
            date=datetime.now(timezone.utc) + timedelta(weeks=2),
            description="Test description 1",
            price_type="fixed",
            price_amount=1000,
            location="Test Location 1",
            current_status=ConcertStatus.UPCOMING,
            organization_id=org_user.id
        )

        concert2 = Concert(
            title="Test Concert 2",
            date=datetime.now(timezone.utc) + timedelta(weeks=3),
            description="Test description 2",
            price_type="free",
            price_amount=0,
            location="Test Location 2",
            current_status=ConcertStatus.UPCOMING,
            organization_id=org_user.id
        )

        concert3 = Concert(
            title="Past Concert",
            date=datetime.now(timezone.utc) - timedelta(weeks=1),
            description="Completed concert",
            price_type="fixed",
            price_amount=500,
            location="Old Location",
            current_status=ConcertStatus.COMPLETED,
            organization_id=org_user.id
        )

        db.add_all([concert1, concert2, concert3])
        db.flush()

        db.add_all([
            ConcertComposer(concert_id=concert1.id, composer_id=composer1.id),
            ConcertInstrument(concert_id=concert1.id, instrument_id=instrument1.id),
            ConcertInstrument(concert_id=concert2.id, instrument_id=instrument2.id)
        ])

        db.commit()
        yield db

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(client, db_session):
    db_session.rollback()

    test_user = User(
        full_name="testuser",
        email="test@example.com",
        user_password=get_password_hash("testpass"),
        role=UserRole.ORG,
        phone_number=9876543210,
        verified=False
    )

    try:
        db_session.add(test_user)
        db_session.commit()

        access_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(minutes=30)
        )

        client.headers.update({"Authorization": f"Bearer {access_token}"})
        yield client

    finally:
        db_session.rollback()
        db_session.query(User).filter(User.full_name == "testuser").delete()
        db_session.commit()


def test_get_concerts_without_filter(client):
    response = client.get("/concerts")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 3


def test_get_concerts_with_status_filter(client):
    response = client.get("/concerts?status_of_concert=completed")
    assert response.status_code == status.HTTP_200_OK
    concerts = response.json()
    assert len(concerts) >= 1
    assert all(c["current_status"] == "completed" for c in concerts)


def test_get_concert_by_id(client, db_session):
    concert = db_session.query(Concert).first()
    response = client.get(f"/concerts/{concert.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == concert.id


def test_get_nonexistent_concert(client):
    response = client.get("/concerts/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_concert_success(auth_client):
    concert_data = {
        "title": "New Concert",
        "date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
        "description": "Test description",
        "price_type": "fixed",
        "price_amount": 1000,
        "location": "Test Location",
        "composers": [1],
        "instruments": [1]
    }

    response = auth_client.post("/concerts/", json=concert_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "New Concert"


def test_create_concert_without_location(auth_client):
    concert_data = {
        "title": "No Location Concert",
        "date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
        "description": "No location test",
        "price_type": "free"
    }

    response = auth_client.post("/concerts/", json=concert_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "location" in response.json()["detail"][0]["loc"]


def test_create_concert_with_past_date(auth_client):
    concert_data = {
        "title": "Past Concert",
        "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "description": "Test description",
        "price_type": "fixed",
        "price_amount": 1000,
        "location": "Test Location"
    }

    response = auth_client.post("/concerts/", json=concert_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "прошедшей датой" in response.json()["detail"]


def test_update_concert_success(auth_client, db_session):
    concert_data = {
        "title": "Concert to Update",
        "date": (datetime.now(timezone.utc) + timedelta(days=20)).isoformat(),
        "description": "Initial description",
        "price_type": "fixed",
        "price_amount": 1500,
        "location": "Initial Location"
    }
    create_response = auth_client.post("/concerts/", json=concert_data)
    concert_id = create_response.json()["id"]

    update_data = {
        "title": "Updated Concert",
        "description": "Updated description"
    }

    response = auth_client.patch(f"/concerts/{concert_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Concert"


def test_update_concert_with_past_date(auth_client, db_session):
    concert_data = {
        "title": "Date Test Concert",
        "date": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
        "description": "Date test",
        "price_type": "fixed",
        "price_amount": 1000,
        "location": "Test Location"
    }
    create_response = auth_client.post("/concerts/", json=concert_data)
    concert_id = create_response.json()["id"]

    update_data = {
        "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    }

    response = auth_client.patch(f"/concerts/{concert_id}", json=update_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "раньше сегодняшней" in response.json()["detail"]


def test_cancel_concert_success(auth_client, db_session):
    concert_data = {
        "title": "Concert to Cancel",
        "date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "description": "Will be cancelled",
        "price_type": "fixed",
        "price_amount": 2000,
        "location": "Cancel Location"
    }
    create_response = auth_client.post("/concerts/", json=concert_data)
    concert_id = create_response.json()["id"]

    response = auth_client.patch(f"/concerts/{concert_id}/cancel")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["current_status"] == "cancelled"


def test_cancel_already_cancelled_concert(auth_client, db_session):
    concert_data = {
        "title": "Already Cancelled",
        "date": (datetime.now(timezone.utc) + timedelta(days=25)).isoformat(),
        "description": "Test",
        "price_type": "fixed",
        "price_amount": 1000,
        "location": "Test"
    }
    create_response = auth_client.post("/concerts/", json=concert_data)
    concert_id = create_response.json()["id"]
    auth_client.patch(f"/concerts/{concert_id}/cancel")

    response = auth_client.patch(f"/concerts/{concert_id}/cancel")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "уже отменен" in response.json()["detail"]


def test_delete_concert_success(auth_client, db_session):
    concert_data = {
        "title": "Concert to Delete",
        "date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "description": "Will be deleted",
        "price_type": "fixed",
        "price_amount": 1000,
        "location": "Delete Location"
    }
    create_response = auth_client.post("/concerts/", json=concert_data)
    assert create_response.status_code == 201
    concert_id = create_response.json()["id"]

    concert = db_session.query(Concert).get(concert_id)
    db_session.commit()
    concert = db_session.query(Concert).get(concert_id)
    delete_response = auth_client.delete(f"/concerts/{concert_id}")
    assert delete_response.status_code == 200


def test_filter_concerts_by_date(client, db_session):
    concert = db_session.query(Concert).first()
    date_str = concert.date.isoformat()

    response = client.get(f"/concerts/filter/?date={date_str}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_filter_concerts_by_composer(client):
    response = client.get("/concerts/filter/?composer_names=Tchaikovsky")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_filter_concerts_by_instrument(client):
    response = client.get("/concerts/filter/?instrument_names=Violin")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_filter_concerts_multiple_filters(client):
    response = client.get(
        "/concerts/filter/",
        params={
            "composer_names": ["Tchaikovsky"],
            "instrument_names": ["Piano"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1