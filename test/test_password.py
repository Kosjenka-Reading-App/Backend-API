import pytest
from conftest import client, auth_header
from auth import createPasswortResetToken


def test_send_password_mail_superadmin():
    email = {"email": "superadmin@gmail.com"}
    resp = client.post(
        "http://localhost:8000/password/forgot",
        json=email,
    )
    assert resp.status_code == 200
    assert (
        "An email has been sent to superadmin@gmail.com with a link for password reset."
        in resp.json()["result"]
    )


def test_send_password_mail_user():
    email = {"email": "regular@gmail.com"}
    resp = client.post(
        "http://localhost:8000/password/forgot",
        json=email,
    )
    assert resp.status_code == 200
    assert (
        "An email has been sent to regular@gmail.com with a link for password reset."
        in resp.json()["result"]
    )


def test_regular_account_reset_password():
    email = {"email": "regular@gmail.com"}
    resp = client.post(
        "http://localhost:8000/password/forgot",
        json=email,
    )
    assert resp.status_code == 200
    assert (
        "An email has been sent to regular@gmail.com with a link for password reset."
        in resp.json()["result"]
    )
    reset_token = createPasswortResetToken("regular@gmail.com", 6000)
    new_password_payload = {"password": "new_password_regular", "token": reset_token}
    reset_password_response = client.post(
        "http://localhost:8000/password/reset", json=new_password_payload
    )
    assert reset_password_response.status_code == 200
    reset_password_result = reset_password_response.json()
    assert reset_password_result["details"] == "Successfully updated password"
    login_json = {"email": "regular@gmail.com", "password": "new_password_regular"}
    login_respose = client.post("http://localhost:8000/login", json=login_json)
    assert login_respose.status_code == 200

    # Change password back, otherwise no login possible and a lots of test fail
    new_password_payload = {"password": "regular", "token": reset_token}
    reset_password_response = client.post(
        "http://localhost:8000/password/reset", json=new_password_payload
    )
    assert reset_password_response.status_code == 200
    reset_password_result = reset_password_response.json()
    assert reset_password_result["details"] == "Successfully updated password"
    login_json = {"email": "regular@gmail.com", "password": "regular"}
    login_respose = client.post("http://localhost:8000/login", json=login_json)
    assert login_respose.status_code == 200


def test_superadmin_account_reset_password():
    email = {"email": "update@gmail.com"}
    resp = client.post(
        "http://localhost:8000/password/forgot",
        json=email,
    )
    assert resp.status_code == 200
    assert (
        "An email has been sent to update@gmail.com with a link for password reset."
        in resp.json()["result"]
    )
    reset_token = createPasswortResetToken("update@gmail.com", 6000)
    new_password_payload = {"password": "new_password_superadmin", "token": reset_token}
    reset_password_response = client.post(
        "http://localhost:8000/password/reset", json=new_password_payload
    )
    assert reset_password_response.status_code == 200
    reset_password_result = reset_password_response.json()
    assert reset_password_result["details"] == "Successfully updated password"

    login_json = {
        "email": "update@gmail.com",
        "password": "new_password_superadmin",
    }
    login_respose = client.post("http://localhost:8000/login", json=login_json)
    assert login_respose.status_code == 200

    # Change password back, otherwise no login possible and a lots of test fail
    new_password_payload = {"password": "superadmin", "token": reset_token}
    reset_password_response = client.post(
        "http://localhost:8000/password/reset", json=new_password_payload
    )
    assert reset_password_response.status_code == 200
    reset_password_result = reset_password_response.json()
    assert reset_password_result["details"] == "Successfully updated password"
    login_json = {"email": "update@gmail.com", "password": "superadmin"}
    login_respose = client.post("http://localhost:8000/login", json=login_json)
    assert login_respose.status_code == 200
