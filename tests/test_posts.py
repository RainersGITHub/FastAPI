from typing import List
from app import schemas


def test_get_all_posts(authorized_client, test_posts):
    result = authorized_client.get("/posts/")

    def validate(post):
        return schemas.PostJoin(**post)

    posts_map = map(validate, result.json())
    posts_list = list(posts_map)

    assert len(result.json()) == len(test_posts)
    assert result.status_code == 200
    # assert posts_list[0].Post.id == test_posts[0].id


def test_unauthorized_user_get_all_posts(client, test_posts):
    result = client.get("/posts/")
    assert result.status_code == 401


def test_unauthorized_user_get_one_post(client, test_posts):
    result = client.get(f"/posts/{test_posts[0].id}")
    assert result.status_code == 401
