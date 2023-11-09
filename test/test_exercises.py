from datetime import datetime
import time
import pytest

from conftest import client


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_create_exercise():
    exercises = client.get("http://localhost:8000/exercises").json()
    exercise_count = len(exercises)
    new_exercise = {
        "title": "Title of the exercise",
        "complexity": "medium",
        "text": "Text of the exercise",
    }
    created_exercise = client.post(
        "http://localhost:8000/exercises", json=new_exercise
    ).json()
    for key in new_exercise:
        assert created_exercise[key] == new_exercise[key]
    exercises = client.get("http://localhost:8000/exercises").json()
    assert len(exercises) == exercise_count + 1


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_create_exercise_without_complexity():
    exercises = client.get("http://localhost:8000/exercises").json()
    exercise_count = len(exercises)
    new_exercise = {
        "title": "Title of another exercise",
        "text": "Text of another exercise",
    }
    created_exercise = client.post(
        "http://localhost:8000/exercises", json=new_exercise
    ).json()
    for key in new_exercise:
        assert created_exercise[key] == new_exercise[key]
    assert created_exercise["complexity"] == None
    exercises = client.get("http://localhost:8000/exercises").json()
    assert len(exercises) == exercise_count + 1


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_get_exercises():
    exercises = client.get("http://localhost:8000/exercises").json()
    assert set(exercises[0].keys()) == {"id", "title", "complexity", "category"}


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_get_exercise():
    exercises = client.get("http://localhost:8000/exercises").json()
    exercise_id = exercises[0]["id"]
    exercise = client.get(f"http://localhost:8000/exercises/{exercise_id}").json()
    assert set(exercise.keys()) == {"id", "title", "category", "complexity", "text"}


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_update_exercise():
    exercises = client.get("http://localhost:8000/exercises").json()
    exercise_id = exercises[0]["id"]
    original_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}"
    ).json()
    body = {"title": "Updated title"}
    client.patch(f"http://localhost:8000/exercises/{exercise_id}", json=body).json()
    updated_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}"
    ).json()
    for key in updated_exercise:
        if key == "title":
            assert updated_exercise[key] == "Updated title"
            continue
        assert updated_exercise[key] == original_exercise[key]


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_sort_exercises():
    exercises = client.get("http://localhost:8000/exercises?order_by=id")
    assert exercises.status_code == 422
    exercises = client.get("http://localhost:8000/exercises?order_by=title").json()
    titles = [exercise["title"] for exercise in exercises]
    assert titles == sorted(titles)
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=title&order=desc"
    ).json()
    titles = [exercise["title"] for exercise in exercises]
    assert titles == sorted(titles)[::-1]


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_search_exercises():
    exercises = client.get("http://localhost:8000/exercises?title_like=another").json()
    for exercise in exercises:
        assert exercise["title"] == "Title of another exercise"


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_delete_exercise():
    exercises = client.get("http://localhost:8000/exercises").json()
    assert len(exercises) > 0
    exercise_ids = {ex["id"] for ex in exercises}
    while exercise_ids:
        exercise_id = exercise_ids.pop()
        client.delete(f"http://localhost:8000/exercises/{exercise_id}").json()
        remaining_exercise_ids = {
            ex["id"] for ex in client.get("http://localhost:8000/exercises").json()
        }
        assert len(remaining_exercise_ids) == len(exercise_ids)
        assert exercise_id not in remaining_exercise_ids


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_sort_complexity():
    for complexity in ["hard", "easy", "medium", "hard", "easy", "medium"]:
        new_exercise = {
            "title": "Title of the exercise",
            "complexity": complexity,
            "text": "Text of the exercise",
        }
        resp = client.post("http://localhost:8000/exercises", json=new_exercise)
        assert resp.status_code == 200
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=complexity&order=asc"
    ).json()
    assert [ex["complexity"] for ex in exercises] == [
        "easy",
        "easy",
        "medium",
        "medium",
        "hard",
        "hard",
    ]
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=complexity&order=desc"
    ).json()
    assert [ex["complexity"] for ex in exercises] == [
        "hard",
        "hard",
        "medium",
        "medium",
        "easy",
        "easy",
    ]


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_filter_complexity():
    for complexity in ["hard", "easy", "medium", "hard", "easy", "medium"]:
        new_exercise = {
            "title": "Title of the exercise",
            "complexity": complexity,
            "text": "Text of the exercise",
        }
        resp = client.post("http://localhost:8000/exercises", json=new_exercise)
        assert resp.status_code == 200
    exercises = client.get("http://localhost:8000/exercises?complexity=hard").json()
    assert {ex["complexity"] for ex in exercises} == {"hard"}
    test_delete_exercise()


@pytest.mark.skip(reason="need to adapt tests for auth tokens")
def test_filter_category():
    for category in [["cats"], ["dogs"], ["cats", "dogs"]]:
        new_exercise = {
            "title": "Title of the exercise",
            "category": category,
            "text": "Text of the exercise",
        }
        resp = client.post("http://localhost:8000/exercises", json=new_exercise)
        assert resp.status_code == 200
    exercises = client.get("http://localhost:8000/exercises?category=cats").json()
    assert {ex["id"] for ex in exercises} == {1, 3}
    exercises = client.get("http://localhost:8000/exercises?category=something").json()
    assert len(exercises) == 0
    test_delete_exercise()


def test_update_exercise_modifies_date():
    # Create a superadmin
    account_data = {
        "email": "superadmin1@gmail.com",
        "password": "superadminpassword"
    }
    # if superadmin1@gmail.com is already in database, this will fail 
    res_admin = client.post("/createsuperadmin/", json=account_data)
    assert res_admin.status_code == 200
    # Login
    res_login = client.post("/login/",json=account_data)
    assert res_login.status_code == 200
    jwt_token = res_login.json()["access_token"]
    # Create an exercise
    exercise_data = {
        "title": "Title Exercise",
        "complexity":"easy",
        "category": ["new"],
        "text": "This is a test exercise"
    }
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    res_exercise = client.post("http://localhost/exercises/", json=exercise_data, headers=headers)
    assert res_exercise.status_code == 200
    first_exercise = res_exercise.json()
    first_date = first_exercise["date"]
    time.sleep(1)
    # Modify the exercise
    exercise_data = {"title": "Updated Exercise Title"}
    exercise_id = first_exercise["id"]
    response = client.patch(f"http://localhost/exercises/{exercise_id}", json=exercise_data, headers=headers)
    assert response.status_code == 200
    updated_exercise = response.json()
    assert updated_exercise is not None
    date_obj1 = datetime.fromisoformat(first_date)
    date_obj2 = datetime.fromisoformat(updated_exercise["date"] )
    assert date_obj1 < date_obj2