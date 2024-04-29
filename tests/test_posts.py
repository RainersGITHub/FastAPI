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


def test_create_post_default_published_true(authorized_client, create_test_user, test_posts):
    testtitle = "Test Title"
    testcontent = "Test content"
    result = authorized_client.post("/posts/", json={"title": testtitle, "content": testcontent})

    created_post = schemas.PostCreate(**result.json())

    assert result.status_code == 201
    assert created_post.title == testtitle
    assert created_post.content == testcontent
    assert created_post.published == True


def test_unauthorized_user_create_post(client, create_test_user, test_posts):
    testtitle = "Test Title"
    testcontent = "Test content"
    result = client.post("/posts/", json={"title": testtitle, "content": testcontent})
    assert result.status_code == 401


def test_unauthorized_user_delete_post(client, create_test_user, test_posts):
    result = client.delete(f"/posts/{test_posts[0].id}")
    assert result.status_code == 401


def test_delete_post(authorized_client, create_test_user, test_posts):
    result = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert result.status_code == 204


def test_delete_noexisting_post(authorized_client, create_test_user, test_posts):
    result = authorized_client.delete("/posts/89898989")
    assert result.status_code == 404


def test_delete_other_users_post(authorized_client, create_test_user, test_posts):
    result = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert result.status_code == 403


def test_update_post(authorized_client, create_test_user, test_posts):
    data = {
        "title": "updated Title",
        "content": "updated content",
        "id": test_posts[0].id
    }

    result = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.PostUpdate(**result.json())

    assert result.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


def test_update_other_users_post(authorized_client, create_test_user, test_posts, create_another_test_user):
    data = {
        "title": "updated Title2",
        "content": "updated content2",
        "id": test_posts[3].id
    }

    result = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)

    assert result.status_code == 403


def test_unauthorized_user_update_post(client, create_test_user, test_posts):
    result = client.put(f"/posts/{test_posts[0].id}")
    assert result.status_code == 401


def test_update_noexisting_post(authorized_client, create_test_user, test_posts):
    data = {
        "title": "updated Title3",
        "content": "updated content3",
        "id": test_posts[0].id
    }

    result = authorized_client.put("/posts/8989898976", json=data)
    assert result.status_code == 404
