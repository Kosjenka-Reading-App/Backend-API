import pytest
from fastapi.testclient import TestClient

from crud import password_hasher
from database import SessionLocal
from main import app
from auth import create_account_activation_token
import models


client = TestClient(app)


@pytest.fixture(scope="session")
def regular_token():
    account_details = {"email": "regular@gmail.com", "password": "regular"}
    resp = client.post("http://localhost:8000/login", json=account_details).json()
    if "detail" in resp and resp["detail"] == "Username/Password wrong":
        resp = client.post(
            "http://localhost:8000/register", json=account_details
        ).json()
        resp = client.post("http://localhost:8000/login", json=account_details).json()
    access_token = resp["access_token"]
    yield access_token


@pytest.fixture(scope="session")
def admin_token(superadmin_token):
    account_details = {"email": "admin@gmail.com", "password": "admin"}
    activate = {
        "token": create_account_activation_token("admin@gmail.com", False, 60000),
        "password": "admin",
    }
    resp = client.post("http://localhost:8000/login", json=account_details).json()
    if "detail" in resp and resp["detail"] == "Username/Password wrong":
        resp = client.post(
            "http://localhost:8000/accounts/activate", json=activate
        ).json()
    resp = client.post("http://localhost:8000/login", json=account_details).json()
    access_token = resp["access_token"]
    yield access_token


@pytest.fixture(scope="session")
def superadmin_token():
    account_details = {"email": "superadmin@gmail.com", "password": "superadmin"}
    resp = client.post("http://localhost:8000/login", json=account_details).json()
    if "detail" in resp and resp["detail"] == "Username/Password wrong":
        db = SessionLocal()
        account_db = models.Account(
            email="superadmin@gmail.com",
            account_category=models.AccountType.Superadmin,
            password=password_hasher("superadmin"),
        )
        db.add(account_db)
        db.commit()
        db.close()
        resp = client.post("http://localhost:8000/login", json=account_details).json()
    access_token = resp["access_token"]
    yield access_token


@pytest.fixture
def create_account():
    accounts = []
    id_counter = 0

    def new_account():
        nonlocal id_counter, accounts
        new_account = {
            "email": f"account_to_be_deleted{id_counter}@mail.com",
            "password": "secret",
        }
        id_counter += 1
        id_account = good_request(
            client.post, "http://localhost:8000/register", json=new_account
        )["id_account"]
        access_token = good_request(
            client.post, "http://localhost:8000/login", json=new_account
        )["access_token"]
        accounts.append((id_account, access_token))
        return access_token

    yield new_account

    for id_account, access_token in accounts:
        good_request(
            client.delete,
            f"http://localhost:8000/accounts/{id_account}",
            headers={"Authorization": f"Bearer {access_token}"},
        )


@pytest.fixture
def create_user():
    users = []
    id_counter = 0

    def new_user(access_token: str):
        nonlocal id_counter, users
        new_user = {
            "username": f"user{id_counter}",
            "proficiency": 0,
        }
        id_counter += 1
        user_resp = good_request(
            client.post,
            "http://localhost:8000/users",
            json=new_user,
            headers=auth_header(access_token),
        )
        users.append((user_resp["id_user"], access_token))
        return user_resp

    yield new_user

    for user_id, access_token in users:
        good_request(
            client.delete,
            f"http://localhost:8000/users/{user_id}",
            headers=auth_header(access_token),
        )


@pytest.fixture
def create_exercise(admin_token):
    exercise_ids = []

    def new_exercise():
        nonlocal exercise_ids
        new_exercise = {
            "title": "Exercise to be deleted after the test",
            "text": "sample text",
        }
        exercise_resp = good_request(
            client.post,
            "http://localhost:8000/exercises",
            json=new_exercise,
            headers=auth_header(admin_token),
        )
        exercise_ids.append(exercise_resp["id"])
        return exercise_resp

    yield new_exercise

    for exercise_id in exercise_ids:
        good_request(
            client.delete,
            f"http://localhost:8000/exercises/{exercise_id}",
            headers=auth_header(admin_token),
        )


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def good_request(request_function, *args, **kwargs):
    resp = request_function(*args, **kwargs)
    assert resp.status_code == 200, resp.json()
    return resp.json()


def bad_request(request_function, status_code, *args, **kwargs):
    resp = request_function(*args, **kwargs)
    assert resp.status_code == status_code, resp.json()
    return resp.json()
