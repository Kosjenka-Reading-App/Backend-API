import pytest

from conftest import client, auth_header


@pytest.mark.parametrize("category_name", ["Dogs", "Cats"])
def test_create_category(category_name, admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()
    category_count = len(categories)
    created_category = client.post(
        f"http://localhost:8000/categories/{category_name}",
        headers=auth_header(admin_token),
    ).json()
    assert created_category["category"] == category_name
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()
    assert len(categories) == category_count + 1


def test_get_categories(regular_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(regular_token)
    ).json()
    assert type(categories) == list
    assert type(categories[0]) == str


def test_update_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()
    original_category = categories[0]
    body = {"category": "Mice"}
    updated_category = client.patch(
        f"http://localhost:8000/categories/{original_category}",
        json=body,
        headers=auth_header(admin_token),
    ).json()
    assert updated_category["category"] == "Mice"
    assert (
        original_category
        not in client.get(
            "http://localhost:8000/categories", headers=auth_header(admin_token)
        ).json()
    )


def test_delete_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()
    assert len(categories) > 0
    while categories:
        category = categories.pop()
        client.delete(
            f"http://localhost:8000/categories/{category}",
            headers=auth_header(admin_token),
        ).json()
        remaining_categories = client.get(
            "http://localhost:8000/categories", headers=auth_header(admin_token)
        ).json()
        assert len(remaining_categories) == len(categories)
        assert category not in remaining_categories


def test_create_exercise_with_category(admin_token):
    client.post(
        "http://localhost:8000/categories/cats", headers=auth_header(admin_token)
    )
    categories = client.get(
        "http://localhost:8000/categories/", headers=auth_header(admin_token)
    ).json()
    assert "cats" in categories
    assert "dogs" not in categories
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
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
    ).json()
    assert len(exercises) == exercise_count + 1
    categories = client.get(
        "http://localhost:8000/categories/", headers=auth_header(admin_token)
    ).json()
    assert set(categories) == {"cats", "dogs"}


def test_update_exercise_with_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()
    assert set(categories) == {"cats", "dogs"}
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
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
    ).json()
    assert set(categories) == {"cats", "dogs", "mice"}


def test_rename_category(admin_token):
    categories = client.get(
        "http://localhost:8000/categories/", headers=auth_header(admin_token)
    ).json()
    assert set(categories) == {"cats", "dogs", "mice"}
    body = {"category": "one mouse"}
    updated_category = client.patch(
        "http://localhost:8000/categories/mice?",
        json=body,
        headers=auth_header(admin_token),
    ).json()
    assert updated_category["category"] == "one mouse"
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(admin_token)
    ).json()
    assert set(categories) == {"cats", "dogs", "one mouse"}


def test_sort_categories(regular_token):
    categories = client.get(
        "http://localhost:8000/categories", headers=auth_header(regular_token)
    ).json()
    print(categories)
    assert len(categories) > 0
    assert client.get(
        "http://localhost:8000/categories?order=asc", headers=auth_header(regular_token)
    ).json() == sorted(categories)
    assert (
        client.get(
            "http://localhost:8000/categories?order=desc",
            headers=auth_header(regular_token),
        ).json()
        == sorted(categories)[::-1]
    )


def test_search_categories(regular_token):
    categories = client.get(
        "http://localhost:8000/categories?name_like=use",
        headers=auth_header(regular_token),
    ).json()
    assert len(categories) > 0
    print(categories)
    assert categories[0] == "one mouse"

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
    non_existent_category = "nonexistent_category"
    resp = client.patch(
        f"http://localhost:8000/categories/{non_existent_category}",
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 404 
    assert resp.json()["detail"] == "category not found"