import pytest

from conftest import client


@pytest.mark.parametrize("category_name", ["Dogs", "Cats"])
def test_create_category(category_name):
    categories = client.get("http://localhost:8000/categories").json()
    category_count = len(categories)
    created_category = client.post(
        f"http://localhost:8000/categories/{category_name}"
    ).json()
    assert created_category["category"] == category_name
    categories = client.get("http://localhost:8000/categories").json()
    assert len(categories) == category_count + 1


def test_get_categories():
    categories = client.get("http://localhost:8000/categories").json()
    assert type(categories) == list
    assert type(categories[0]) == str


def test_update_category():
    categories = client.get("http://localhost:8000/categories").json()
    original_category = categories[0]
    body = {"category": "Mice"}
    updated_category = client.patch(
        f"http://localhost:8000/categories/{original_category}", json=body
    ).json()
    assert updated_category["category"] == "Mice"
    assert (
        original_category not in client.get("http://localhost:8000/categories").json()
    )


def test_delete_category():
    categories = client.get("http://localhost:8000/categories").json()
    assert len(categories) > 0
    while categories:
        category = categories.pop()
        client.delete(f"http://localhost:8000/categories/{category}").json()
        remaining_categories = client.get("http://localhost:8000/categories").json()
        assert len(remaining_categories) == len(categories)
        assert category not in remaining_categories


def test_create_exercise_with_category():
    client.post("http://localhost:8000/categories/cats")
    categories = client.get("http://localhost:8000/categories/").json()
    assert "cats" in categories
    assert "dogs" not in categories
    exercises = client.get("http://localhost:8000/exercises").json()
    exercise_count = len(exercises)
    new_exercise = {
        "title": "Title of exercise about cats",
        "text": "Text of exercise about cats",
        "category": ["cats", "dogs"],
    }
    created_exercise = client.post(
        "http://localhost:8000/exercises", json=new_exercise
    ).json()
    for key in new_exercise:
        if key == "category":
            assert created_exercise[key] == [{"category": "cats"}, {"category": "dogs"}]
            continue
        assert created_exercise[key] == new_exercise[key]
    assert created_exercise["complexity"] == None
    exercises = client.get("http://localhost:8000/exercises").json()
    assert len(exercises) == exercise_count + 1
    categories = client.get("http://localhost:8000/categories/").json()
    assert set(categories) == {"cats", "dogs"}


def test_update_exercise_with_category():
    categories = client.get("http://localhost:8000/categories").json()
    assert set(categories) == {"cats", "dogs"}
    exercises = client.get("http://localhost:8000/exercises").json()
    exercise_id = exercises[0]["id"]
    original_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}"
    ).json()
    body = {"category": ["cats", "mice"]}
    client.patch(f"http://localhost:8000/exercises/{exercise_id}", json=body).json()
    updated_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}"
    ).json()
    for key in updated_exercise:
        if key == "category":
            assert {cat["category"] for cat in updated_exercise[key]} == {
                "cats",
                "mice",
            }
            continue
        assert updated_exercise[key] == original_exercise[key]
    categories = client.get("http://localhost:8000/categories").json()
    assert set(categories) == {"cats", "dogs", "mice"}


def test_rename_category():
    categories = client.get("http://localhost:8000/categories").json()
    assert set(categories) == {"cats", "dogs", "mice"}
    body = {"category": "one mouse"}
    updated_category = client.patch(
        "http://localhost:8000/categories/mice?", json=body
    ).json()
    assert updated_category["category"] == "one mouse"
    categories = client.get("http://localhost:8000/categories").json()
    assert set(categories) == {"cats", "dogs", "one mouse"}
