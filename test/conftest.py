import pytest
from fastapi.testclient import TestClient
from main import app
from utils import auth_header

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
    resp = client.post("http://localhost:8000/login", json=account_details).json()
    if "detail" in resp and resp["detail"] == "Username/Password wrong":
        resp = client.post(
            "http://localhost:8000/accounts",
            json=account_details,
            headers=auth_header(superadmin_token),
        ).json()
        resp = client.post("http://localhost:8000/login", json=account_details).json()
    access_token = resp["access_token"]
    yield access_token


@pytest.fixture(scope="session")
def superadmin_token():
    account_details = {"email": "superadmin@gmail.com", "password": "superadmin"}
    resp = client.post("http://localhost:8000/login", json=account_details).json()
    if "detail" in resp and resp["detail"] == "Username/Password wrong":
        resp = client.post(
            "http://localhost:8000/createsuperadmin", json=account_details
        ).json()
        resp = client.post("http://localhost:8000/login", json=account_details).json()
    access_token = resp["access_token"]
    yield access_token
