import pytest

from app import ormmodels


@pytest.fixture()
def create_test_vote(test_posts, session, create_test_user):
    new_vote = ormmodels.Vote(post_id=test_posts[3].id, user_id=create_test_user['id'])
    session.add(new_vote)
    session.commit()


def test_vote_on_post(authorized_client, test_posts):
    result = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "direction": 1})

    assert result.status_code == 201


def test_vote_twice_on_post(authorized_client, test_posts, create_test_vote):
    result = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "direction": 1})

    assert result.status_code == 409


def test_delete_vote(authorized_client, test_posts, create_test_vote):
    result = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "direction": 0})

    assert result.status_code == 201


def test_delete_not_existing_vote(authorized_client, test_posts):
    result = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "direction": 0})

    assert result.status_code == 404


def test_vote_on_not_existing_vote(authorized_client, test_posts):
    result = authorized_client.post("/vote/", json={"post_id": 898989733, "direction": 1})

    assert result.status_code == 404


def test_vote_on_with_unauthorized_user(client, test_posts):
    result = client.post("/vote/", json={"post_id": test_posts[3].id, "direction": 1})

    assert result.status_code == 401