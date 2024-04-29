from typing import List

import pytest

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


def test_unauthorized_user_get_post_by_id(client, test_posts):
    result = client.get(f"/posts/{test_posts[0].id}")
    assert result.status_code == 401


def get_post_by_not_existing_id(authorized_client, test_posts):
    result = authorized_client.get("/posts/88888")
    assert result.status_code == 404


def get_post_by_existing_id(authorized_client, test_posts):
    result = authorized_client.get(f"/posts/{test_posts[0].id}")

    post = schemas.PostJoin(**result.json())

    assert result.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


@pytest.mark.parametrize("title, content, published",
                         [("awesome new title", "awesome new content", True),
                          ("favourite pizza", "I love peperoni", False),
                          ("tallest skyscraper", "wahoo", True),
                          ])
def test_create_post(authorized_client, create_test_user, test_posts, title, content, published):
    result = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})

    created_post = schemas.PostCreate(**result.json())

    assert result.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
