from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db, Base
from app.main import app
from app.oauth2 import create_access_token
from app import ormmodels
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


@pytest.fixture()
def create_test_user(client):
    user_data = {"email": "rainer.rode@web.de", "password": "password123"}
    result = client.post("/users/", json=user_data)
    assert result.status_code == 201
    new_user = result.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture()
def create_another_test_user(client):
    user_data = {"email": "rainer.rode@gmx.com", "password": "password123"}
    result = client.post("/users/", json=user_data)
    assert result.status_code == 201
    new_user = result.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture()
def token(create_test_user):
    return create_access_token({"user_id": create_test_user['id']})


@pytest.fixture()
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture()
def test_posts(create_test_user, session, create_another_test_user):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": create_test_user['id']},

        {
            "title": "second title",
            "content": "second content",
            "owner_id": create_test_user['id']},
        {
            "title": "third title",
            "content": "third content",
            "owner_id": create_test_user['id']},
        {
            "title": "fourth title",
            "content": "fourth content",
            "owner_id": create_another_test_user['id']
        }]

    def create_post_model(post):
        return ormmodels.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()

    posts = session.query(ormmodels.Post).all()
    return posts
