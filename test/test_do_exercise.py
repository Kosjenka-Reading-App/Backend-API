from conftest import client, auth_header, good_request, bad_request


def test_track_exercise_completion_metrics(regular_token, create_user, create_exercise):
    created_user_id = create_user(regular_token)["id_user"]
    exercise_id = create_exercise()["id"]

    exercise_completion = {
        "user_id": created_user_id,
        "completion": 45,
        "time_spent": 100,
        "position": 29,
    }
    good_request(
        client.post,
        f"http://localhost:8000/exercises/{exercise_id}/track_completion",
        json=exercise_completion,
        headers=auth_header(regular_token),
    )
    exercise_resp = good_request(
        client.get,
        f"http://localhost:8000/exercises/{exercise_id}?user_id={created_user_id}",
        headers=auth_header(regular_token),
    )
    assert exercise_resp["completion"]["completion"] == 45
    assert exercise_resp["completion"]["time_spent"] == 100
    assert exercise_resp["completion"]["position"] == 29


def test_track_multiple_users_per_exercise(regular_token, create_user, create_exercise):
    id_alice = create_user(regular_token)["id_user"]
    id_bob = create_user(regular_token)["id_user"]
    exercise_id = create_exercise()["id"]

    exercise_completion = {
        "user_id": id_alice,
        "completion": 20,
    }
    good_request(
        client.post,
        f"http://localhost:8000/exercises/{exercise_id}/track_completion",
        json=exercise_completion,
        headers=auth_header(regular_token),
    )
    exercise_completion = {
        "user_id": id_bob,
        "completion": 40,
    }
    good_request(
        client.post,
        f"http://localhost:8000/exercises/{exercise_id}/track_completion",
        json=exercise_completion,
        headers=auth_header(regular_token),
    )

    exercise_resp = good_request(
        client.get,
        f"http://localhost:8000/exercises/{exercise_id}?user_id={id_alice}",
        headers=auth_header(regular_token),
    )
    assert exercise_resp["completion"]["completion"] == 20
    exercise_resp = good_request(
        client.get,
        f"http://localhost:8000/exercises/{exercise_id}?user_id={id_bob}",
        headers=auth_header(regular_token),
    )
    assert exercise_resp["completion"]["completion"] == 40


def test_track_multiple_exercises_per_user(regular_token, create_user, create_exercise):
    id_alice = create_user(regular_token)["id_user"]
    exercise_one_id = create_exercise()["id"]
    exercise_two_id = create_exercise()["id"]

    for exercise_id, completion in (exercise_one_id, 20), (exercise_two_id, 40):
        exercise_completion = {
            "user_id": id_alice,
            "completion": completion,
        }
        good_request(
            client.post,
            f"http://localhost:8000/exercises/{exercise_id}/track_completion",
            json=exercise_completion,
            headers=auth_header(regular_token),
        )

    for exercise_id, completion in (exercise_one_id, 20), (exercise_two_id, 40):
        exercise_resp = good_request(
            client.get,
            f"http://localhost:8000/exercises/{exercise_id}?user_id={id_alice}",
            headers=auth_header(regular_token),
        )
        assert exercise_resp["completion"]["completion"] == completion


def test_read_all_exercises_with_completion(
    regular_token, create_user, create_exercise
):
    id_alice = create_user(regular_token)["id_user"]
    created_exercises: dict[str, int | None] = {
        create_exercise()["id"]: i * 10 for i in range(1, 4)
    }
    for ex_id, completion in created_exercises.items():
        exercise_completion = {
            "user_id": id_alice,
            "completion": completion,
        }
        good_request(
            client.post,
            f"http://localhost:8000/exercises/{ex_id}/track_completion",
            json=exercise_completion,
            headers=auth_header(regular_token),
        )
    created_exercises[create_exercise()["id"]] = None
    exercises = [
        ex
        for ex in good_request(client.get, "http://localhost:8000/exercises")["items"]
        if ex["id"] in created_exercises.keys()
    ]
    for ex in exercises:
        assert ex["completion"] == None
    exercises = [
        ex
        for ex in good_request(
            client.get,
            f"http://localhost:8000/exercises?user_id={id_alice}",
            headers=auth_header(regular_token),
        )["items"]
        if ex["id"] in created_exercises.keys()
    ]
    for ex in exercises:
        if not created_exercises[ex["id"]]:
            assert ex["completion"] is None
        else:
            assert ex["completion"]["completion"] == created_exercises[ex["id"]]


def test_read_exercises_of_other_account_user(create_account, create_exercise):
    access_token = create_account()
    ex_id = create_exercise()["id"]
    bad_request(client.get, 403, f"http://localhost:8000/exercises/{ex_id}?user_id=2")
    bad_request(
        client.get,
        404,
        f"http://localhost:8000/exercises/{ex_id}?user_id=2",
        headers=auth_header(access_token),
    )


def test_sort_completion(regular_token, create_user, create_exercise):
    created_user_id = create_user(regular_token)["id_user"]
    exercise_id1 = create_exercise()["id"]
    exercise_id2 = create_exercise()["id"]
    exercise_id3 = create_exercise()["id"]

    exercise_completion1 = {
        "user_id": created_user_id,
        "completion": 15,
        "time_spent": 100,
        "position": 29,
    }
    exercise_completion2 = {
        "user_id": created_user_id,
        "completion": 45,
        "time_spent": 100,
        "position": 29,
    }
    exercise_completion3 = {
        "user_id": created_user_id,
        "completion": 0,
        "time_spent": 100,
        "position": 29,
    }
    good_request(
        client.post,
        f"http://localhost:8000/exercises/{exercise_id1}/track_completion",
        json=exercise_completion1,
        headers=auth_header(regular_token),
    )
    good_request(
        client.post,
        f"http://localhost:8000/exercises/{exercise_id2}/track_completion",
        json=exercise_completion2,
        headers=auth_header(regular_token),
    )
    good_request(
        client.post,
        f"http://localhost:8000/exercises/{exercise_id3}/track_completion",
        json=exercise_completion3,
        headers=auth_header(regular_token),
    )
    # check the order
    exercises = [
        ex
        for ex in good_request(
            client.get,
            f"http://localhost:8000/exercises?user_id={created_user_id}&order_by=completion",
            headers=auth_header(regular_token),
        )["items"]
    ]
    completions = []
    for exercise in exercises:
        completions.append(exercise["completion"]["completion"])
    print(completions)
    assert completions == sorted(completions)
    exercises = [
        ex
        for ex in good_request(
            client.get,
            f"http://localhost:8000/exercises?user_id={created_user_id}&order_by=completion&order=desc",
            headers=auth_header(regular_token),
        )["items"]
    ]
    completions = []
    for exercise in exercises:
        completions.append(exercise["completion"]["completion"])
    assert completions == sorted(completions)[::-1]
