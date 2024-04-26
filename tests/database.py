from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db, Base
from app.main import app
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


@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
