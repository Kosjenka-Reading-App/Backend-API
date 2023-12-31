import pytest

from conftest import client, auth_header, good_request


@pytest.mark.parametrize("category_name", ["Dogs", "Cats"])
def test_create_category(category_name, admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    category_count = len(categories)
    created_category = client.post(
        f"http://localhost:8000/categories/{category_name}",
        headers=auth_header(admin_token),
    ).json()
    assert created_category["category"] == category_name
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    assert len(categories) == category_count + 1


def test_get_categories(regular_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(regular_token)
    ).json()["items"]
    assert type(categories) == list
    assert type(categories[0]) == dict
    assert "category" in categories[0]


def test_update_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    original_category = categories[0]["category"]
    body = {"category": "Mice"}
    updated_category = client.patch(
        f"http://localhost:8000/categories/{original_category}",
        json=body,
        headers=auth_header(admin_token),
    ).json()
    print(updated_category)
    assert updated_category["category"] == "Mice"
    assert (
        original_category
        not in client.get(
            "http://localhost:8000/categories", headers=auth_header(admin_token)
        ).json()["items"]
    )


def test_delete_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    assert len(categories) > 0
    while categories:
        category = categories.pop()
        client.delete(
            f"http://localhost:8000/categories/{category['category']}",
            headers=auth_header(admin_token),
        ).json()
        remaining_categories = client.get(
            "http://localhost:8000/categories", headers=auth_header(admin_token)
        ).json()["items"]
        assert len(remaining_categories) == len(categories)
        assert category not in remaining_categories


def test_create_exercise_with_category(admin_token):
    client.post(
        "http://localhost:8000/categories/cats", headers=auth_header(admin_token)
    )
    categories = client.get(
        "http://localhost:8000/categories/", headers=auth_header(admin_token)
    ).json()["items"]
    assert {"category": "cats"} in categories
    assert {"category": "dogs"} not in categories
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()["items"]
    exercise_count = len(exercises)
    new_exercise = {
        "title": "Title of exercise about cats",
        "text": "Text of exercise about cats",
        "category": ["cats", "dogs"],
    }
    created_exercise = client.post(
        "http://localhost:8000/exercises",
        json=new_exercise,
        headers=auth_header(admin_token),
    ).json()
    for key in new_exercise:
        if key == "category":
            assert created_exercise[key] == [{"category": "cats"}, {"category": "dogs"}]
            continue
        assert created_exercise[key] == new_exercise[key]
    assert created_exercise["complexity"] == None
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()["items"]
    assert len(exercises) == exercise_count + 1
    categories = client.get(
        "http://localhost:8000/categories/", headers=auth_header(admin_token)
    ).json()["items"]
    assert set(c["category"] for c in categories) == {"cats", "dogs"}


def test_update_exercise_with_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    assert set(c["category"] for c in categories) == {"cats", "dogs"}
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()["items"]
    exercise_id = exercises[0]["id"]
    original_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}",
        headers=auth_header(admin_token),
    ).json()
    body = {"category": ["cats", "mice"]}
    client.patch(
        f"http://localhost:8000/exercises/{exercise_id}",
        json=body,
        headers=auth_header(admin_token),
    ).json()
    updated_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}",
        headers=auth_header(admin_token),
    ).json()
    for key in updated_exercise:
        if key == "category":
            assert {cat["category"] for cat in updated_exercise[key]} == {
                "cats",
                "mice",
            }
            continue
        assert updated_exercise[key] == original_exercise[key]
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    assert set(c["category"] for c in categories) == {"cats", "dogs", "mice"}


def test_rename_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories/", headers=auth_header(admin_token)
    ).json()["items"]
    assert set(c["category"] for c in categories) == {"cats", "dogs", "mice"}
    body = {"category": "one mouse"}
    updated_category = client.patch(
        "http://localhost:8000/categories/mice?",
        json=body,
        headers=auth_header(admin_token),
    ).json()
    assert updated_category["category"] == "one mouse"
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()["items"]
    assert set(c["category"] for c in categories) == {"cats", "dogs", "one mouse"}


def test_sort_categories(regular_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(regular_token)
    ).json()["items"]
    assert len(categories) > 0
    assert [
        c["category"]
        for c in client.get(
            "http://localhost:8000/categories?order=asc",
            headers=auth_header(regular_token),
        ).json()["items"]
    ] == sorted([c["category"] for c in categories])
    assert [
        c["category"]
        for c in client.get(
            "http://localhost:8000/categories?order=desc",
            headers=auth_header(regular_token),
        ).json()["items"]
    ] == sorted([c["category"] for c in categories])[::-1]


def test_search_categories(regular_token):
    categories = client.get(
        "http://localhost:8000/categories?name_like=use",
        headers=auth_header(regular_token),
    ).json()["items"]
    assert len(categories) > 0
    assert categories[0] == {"category": "one mouse"}


def test_delete_nonexistent_category(admin_token):
    # Assume nonexistent_category doesn't exist
    non_existent_category = "nonexistent_category"
    resp = client.delete(
        f"http://localhost:8000/categories/{non_existent_category}",
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "category not found"


def test_patch_nonexistent_category(admin_token):
    # Assume nonexistent_category doesn't exist
    non_existent_category = {"category": "non_existent_category"}
    body = {"category": "cats"}
    resp = client.patch(
        f"http://localhost:8000/categories/{non_existent_category}",
        json=body,
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "category not found"


def test_patch_category_updates_linked_exercises(create_exercise, admin_token):
    ex_wood_id = create_exercise(categories=["wood"])["id"]
    patch_category = {"category": "stone"}
    good_request(
        client.patch,
        "http://localhost:8000/categories/wood",
        headers=auth_header(admin_token),
        json=patch_category,
    )
    ex = good_request(client.get, f"http://localhost:8000/exercises/{ex_wood_id}")
    assert ex["category"][0]["category"] == "stone"
    good_request(
        client.delete,
        "http://localhost:8000/categories/stone",
        headers=auth_header(admin_token),
    )


def test_patch_category_to_existing_category(create_exercise, admin_token):
    create_exercise(categories=["wood"])["id"]
    create_exercise(categories=["stone"])["id"]
    patch_category = {"category": "stone"}
    good_request(
        client.patch,
        "http://localhost:8000/categories/wood",
        headers=auth_header(admin_token),
        json=patch_category,
    )
    good_request(
        client.delete,
        "http://localhost:8000/categories/stone",
        headers=auth_header(admin_token),
    )
