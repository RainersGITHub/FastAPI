from app import schemas
from app.config import settings
from jose import jwt
import pytest


def test_root(client):
    result = client.get("/")
    assert result.status_code == 200
    assert result.json().get('message') == 'The URL is not complete / not defined'


def test_create_user(client):
    user_data = {"email": "rainer.rode@web.de", "password": "password123"}
    result = client.post("/users/", json=user_data)

    assert result.status_code == 201

    new_user = schemas.UserOut(**result.json())
    assert new_user.email == "rainer.rode@web.de"
    return new_user


def test_login_user(client, create_test_user):
    result = client.post("/login",
                         data={"username": create_test_user['email'], "password": create_test_user['password']})

    login_result = schemas.Token(**result.json())
    payload = jwt.decode(login_result.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    id = payload.get("user_id")
    assert id == create_test_user['id']
    assert login_result.token_type == "bearer"
    assert result.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('rainer.rode@mail.de', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('rainer.rode@mail.de', None, 422)
])
def test_incorrect_login(client, create_test_user, email, password, status_code):
    result = client.post("/login",
                         data={"username": email, "password": password})

    assert result.status_code == status_code
