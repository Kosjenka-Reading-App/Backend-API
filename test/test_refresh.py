from conftest import client, auth_header


def test_refresh(superadmin_token):
    # Perform a login to obtain a refresh token
    account_details = {"email": "update@gmail.com", "password": "superadmin"}
    login_resp = client.post("http://localhost:8000/login", json=account_details)
    assert login_resp.status_code == 200
    refresh_token = login_resp.json().get("refresh_token")
    # Use the obtained refresh token to refresh the access token
    resp = client.post(
        "http://localhost:8000/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()  # Ensure a new access token is provided
