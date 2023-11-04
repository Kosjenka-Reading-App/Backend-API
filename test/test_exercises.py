import requests
import pytest


def test_create_exercise():
    exercises = requests.get('http://localhost:8000/exercises').json()
    exercise_count = len(exercises)
    new_exercise = {
        'title': 'Title of the exercise',
        'complexity': 3.0,
        'text': 'Text of the exercise'
    }
    created_exercise = requests.post('http://localhost:8000/exercises', json=new_exercise).json()
    for key in new_exercise:
        assert created_exercise[key] == new_exercise[key]
    exercises = requests.get('http://localhost:8000/exercises').json()
    assert len(exercises) == exercise_count + 1


def test_create_exercise_without_complexity():
    exercises = requests.get('http://localhost:8000/exercises').json()
    exercise_count = len(exercises)
    new_exercise = {
        'title': 'Title of another exercise',
        'text': 'Text of another exercise'
    }
    created_exercise = requests.post('http://localhost:8000/exercises', json=new_exercise).json()
    for key in new_exercise:
        assert created_exercise[key] == new_exercise[key]
    assert created_exercise['complexity'] == 0.0
    exercises = requests.get('http://localhost:8000/exercises').json()
    assert len(exercises) == exercise_count + 1


def test_get_exercises():
    exercises = requests.get('http://localhost:8000/exercises').json()
    assert set(exercises[0].keys()) == {'id', 'title', 'complexity'}


def test_get_exercise():
    exercises = requests.get('http://localhost:8000/exercises').json()
    exercise_id = exercises[0]['id']
    exercise = requests.get(f'http://localhost:8000/exercises/{exercise_id}').json()
    assert set(exercise.keys()) == {'id', 'title', 'complexity', 'text'}


def test_update_exercise():
    exercises = requests.get('http://localhost:8000/exercises').json()
    exercise_id = exercises[0]['id']
    original_exercise = requests.get(f'http://localhost:8000/exercises/{exercise_id}').json()
    body = {'title': 'Updated title'}
    requests.patch(f'http://localhost:8000/exercises/{exercise_id}', json=body).json()
    updated_exercise = requests.get(f'http://localhost:8000/exercises/{exercise_id}').json()
    for key in updated_exercise:
        if key == 'title':
            assert updated_exercise[key] == 'Updated title'
            continue
        assert updated_exercise[key] == original_exercise[key]


def test_sort_exercises():
    exercises = requests.get('http://localhost:8000/exercises?order_by=id')
    assert exercises.status_code == 404
    exercises = requests.get('http://localhost:8000/exercises?order_by=complexity').json()
    complexities = [exercise['complexity'] for exercise in exercises]
    assert complexities == sorted(complexities)


def test_search_exercises():
    exercises = requests.get('http://localhost:8000/exercises?title_like=another').json()
    for exercise in exercises:
        assert exercise['title'] == 'Title of another exercise'


def test_delete_exercise():
    exercises = requests.get('http://localhost:8000/exercises').json()
    assert len(exercises) > 0
    exercise_ids = {ex['id'] for ex in exercises}
    while exercise_ids:
        exercise_id = exercise_ids.pop()
        requests.delete(f'http://localhost:8000/exercises/{exercise_id}').json()
        remaining_exercise_ids = {ex['id'] for ex in requests.get('http://localhost:8000/exercises').json()}
        assert len(remaining_exercise_ids) == len(exercise_ids)
        assert exercise_id not in remaining_exercise_ids

