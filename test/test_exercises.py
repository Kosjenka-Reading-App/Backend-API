from datetime import datetime
import time
from conftest import client
from utils import auth_header


def test_create_exercise(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
    exercise_count = len(exercises)
    new_exercise = {
        "title": "Title of the exercise",
        "complexity": "medium",
        "text": "Text of the exercise",
    }
    created_exercise = client.post(
        "http://localhost:8000/exercises",
        json=new_exercise,
        headers=auth_header(admin_token),
    ).json()
    for key in new_exercise:
        assert created_exercise[key] == new_exercise[key]
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
    assert len(exercises) == exercise_count + 1


def test_create_exercise_without_complexity(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
    exercise_count = len(exercises)
    new_exercise = {
        "title": "Title of another exercise",
        "text": "Text of another exercise",
    }
    created_exercise = client.post(
        "http://localhost:8000/exercises",
        json=new_exercise,
        headers=auth_header(admin_token),
    ).json()
    for key in new_exercise:
        assert created_exercise[key] == new_exercise[key]
    assert created_exercise["complexity"] == None
    exercises = client.get(
        "http://localhost:8000/exercises/", headers=auth_header(admin_token)
    ).json()
    assert len(exercises) == exercise_count + 1


def test_get_exercises(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
    assert set(exercises[0].keys()) == {"id", "title", "complexity", "category", "date"}


def test_get_exercise(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises/", headers=auth_header(admin_token)
    ).json()
    exercise_id = exercises[0]["id"]
    exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}",
        headers=auth_header(admin_token),
    ).json()
    assert set(exercise.keys()) == {
        "id",
        "title",
        "category",
        "complexity",
        "text",
        "date",
    }


def test_update_exercise(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
    exercise_id = exercises[0]["id"]
    original_exercise = client.get(
        f"http://localhost:8000/exercises/{exercise_id}",
        headers=auth_header(admin_token),
    ).json()
    body = {"title": "Updated title"}
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
        if key == "title":
            assert updated_exercise[key] == "Updated title"
            continue
        if key == "date":
            assert datetime.fromisoformat(
                updated_exercise[key]
            ) >= datetime.fromisoformat(original_exercise[key])
            continue
        assert updated_exercise[key] == original_exercise[key]


def test_sort_exercises(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=id", headers=auth_header(admin_token)
    )
    assert exercises.status_code == 422
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=title",
        headers=auth_header(admin_token),
    ).json()
    titles = [exercise["title"] for exercise in exercises]
    assert titles == sorted(titles)
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=title&order=desc",
        headers=auth_header(admin_token),
    ).json()
    titles = [exercise["title"] for exercise in exercises]
    assert titles == sorted(titles)[::-1]


def test_search_exercises(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises?title_like=another",
        headers=auth_header(admin_token),
    ).json()
    for exercise in exercises:
        assert exercise["title"] == "Title of another exercise"


def test_delete_exercise(admin_token):
    exercises = client.get(
        "http://localhost:8000/exercises", headers=auth_header(admin_token)
    ).json()
    assert len(exercises) > 0
    exercise_ids = {ex["id"] for ex in exercises}
    while exercise_ids:
        exercise_id = exercise_ids.pop()
        client.delete(
            f"http://localhost:8000/exercises/{exercise_id}",
            headers=auth_header(admin_token),
        ).json()
        remaining_exercise_ids = {
            ex["id"]
            for ex in client.get(
                "http://localhost:8000/exercises", headers=auth_header(admin_token)
            ).json()
        }
        assert len(remaining_exercise_ids) == len(exercise_ids)
        assert exercise_id not in remaining_exercise_ids


def test_sort_complexity(admin_token):
    for complexity in ["hard", "easy", "medium", "hard", "easy", "medium"]:
        new_exercise = {
            "title": "Title of the exercise",
            "complexity": complexity,
            "text": "Text of the exercise",
        }
        resp = client.post(
            "http://localhost:8000/exercises",
            json=new_exercise,
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
    exercises = client.get(
        "http://localhost:8000/exercises?order_by=complexity&order=asc",
        headers=auth_header(admin_token),
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
        "http://localhost:8000/exercises?order_by=complexity&order=desc",
        headers=auth_header(admin_token),
    ).json()
    assert [ex["complexity"] for ex in exercises] == [
        "hard",
        "hard",
        "medium",
        "medium",
        "easy",
        "easy",
    ]


def test_filter_complexity(admin_token):
    for complexity in ["hard", "easy", "medium", "hard", "easy", "medium"]:
        new_exercise = {
            "title": "Title of the exercise",
            "complexity": complexity,
            "text": "Text of the exercise",
        }
        resp = client.post(
            "http://localhost:8000/exercises",
            json=new_exercise,
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
    exercises = client.get(
        "http://localhost:8000/exercises?complexity=hard",
        headers=auth_header(admin_token),
    ).json()
    assert {ex["complexity"] for ex in exercises} == {"hard"}
    test_delete_exercise(admin_token)


def test_filter_category(admin_token):
    for category in [["cats"], ["dogs"], ["cats", "dogs"]]:
        new_exercise = {
            "title": "Title of the exercise",
            "category": category,
            "text": "Text of the exercise",
        }
        resp = client.post(
            "http://localhost:8000/exercises",
            json=new_exercise,
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
    exercises = client.get(
        "http://localhost:8000/exercises?category=cats",
        headers=auth_header(admin_token),
    ).json()
    assert {ex["id"] for ex in exercises} == {1, 3}
    exercises = client.get(
        "http://localhost:8000/exercises?category=something",
        headers=auth_header(admin_token),
    ).json()
    assert len(exercises) == 0
    test_delete_exercise(admin_token)


def test_update_exercise_modifies_date(admin_token):
    # Create an exercise
    exercise_data = {
        "title": "Title Exercise",
        "complexity": "easy",
        "category": ["new"],
        "text": "This is a test exercise",
    }
    res_exercise = client.post(
        "http://localhost/exercises/",
        json=exercise_data,
        headers=auth_header(admin_token),
    )
    assert res_exercise.status_code == 200
    first_exercise = res_exercise.json()
    first_date = first_exercise["date"]
    time.sleep(1)
    # Modify the exercise
    exercise_data = {"title": "Updated Exercise Title"}
    exercise_id = first_exercise["id"]
    response = client.patch(
        f"http://localhost/exercises/{exercise_id}",
        json=exercise_data,
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    updated_exercise = response.json()
    assert updated_exercise is not None
    date_obj1 = datetime.fromisoformat(first_date)
    date_obj2 = datetime.fromisoformat(updated_exercise["date"])
    assert date_obj1 < date_obj2
    test_delete_exercise(admin_token)
