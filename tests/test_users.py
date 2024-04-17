from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db, Base
from app.main import app
from app import schemas, ormmodels
import pytest

DATABASE_TYPE = settings.DATABASE_TYPE
USERNAME = settings.USERNAME
PASSWORD = settings.PASSWORD
HOST = settings.HOST
PORT = settings.PORT
DATABASE_NAME = settings.DATABASE_NAME
ENCODING = settings.ENCODING
SQLALCHEMY_DATABASE_URL = f"{DATABASE_TYPE}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}_test"

engine = create_engine(f"{SQLALCHEMY_DATABASE_URL}", client_encoding=f"{ENCODING}")

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)


def test_root(client):
    result = client.get("/")
    assert result.status_code == 200
    assert result.json().get('message') == 'The URL is not complete / not defined'


def test_create_user(client):
    result = client.post("/users/", json={"email": "rainer.rode@web.de", "password": "password123"})

    print(result)
    new_user = schemas.UserOut(**result.json())
    assert result.status_code == 201
    assert new_user.email == "rainer.rode@web.de"
