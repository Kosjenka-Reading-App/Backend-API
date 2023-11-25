from conftest import client, auth_header

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
    print(resp.json())
    assert resp.status_code == 200
    assert (
        "An email has been sent to regular@gmail.com with a link for password reset."
        in resp.json()["result"]
    )


def test_account_reset_password():
    email = {"email": "regular@gmail.com"}
    resp = client.post("http://localhost:8000/password/forget", json=email)
    assert resp.status_code == 200
    reset_request_result = resp.json()
    assert reset_request_result['details'] == "Password reset email sent"
    reset_token = reset_request_result['token']
    new_password_payload = {"password": "new_password", "token": reset_token}
    reset_password_response = client.post("http://localhost:8000/password/reset", json=new_password_payload)
    assert reset_password_response.status_code == 200
    reset_password_result = reset_password_response.json()
    assert reset_password_result['details'] == "Successfully updated password"