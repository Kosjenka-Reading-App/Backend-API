from conftest import client, auth_header, good_request, bad_request


def test_create_account(superadmin_token):
    accounts = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    account_count = len(accounts)
    new_account = {"email": "email@gmail.com", "password": "secret"}
    resp = client.post(
        "http://localhost:8000/accounts",
        json=new_account,
        headers=auth_header(superadmin_token),
    )
    assert resp.status_code == 200
    accounts = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    assert len(accounts) == account_count + 1


def test_update_account(superadmin_token):
    # Get the superadmin
    accounts = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    account_id = accounts[0]["id_account"]
    # Get the superadmin's account
    original_account = client.get(
        f"http://localhost:8000/accounts/{account_id}",
        headers=auth_header(superadmin_token),
    ).json()
    body = {"email": "update@gmail.com"}
    # Update the email
    client.patch(
        f"http://localhost:8000/accounts/{account_id}",
        json=body,
        headers=auth_header(superadmin_token),
    ).json()
    # Get the superadmin's update account
    updated_account = client.get(
        f"http://localhost:8000/accounts/{account_id}",
        headers=auth_header(superadmin_token),
    ).json()
    # Check that the email has been updated
    for key in updated_account:
        if key == "email":
            assert updated_account[key] == "update@gmail.com"
            continue
        assert updated_account[key] == original_account[key]


def test_search_account(superadmin_token):
    new_account = {
        "email": "exercise_master@gmail.com",
        "password": "secret",
    }
    resp = client.post(
        "http://localhost:8000/accounts",
        json=new_account,
        headers=auth_header(superadmin_token),
    )
    assert resp.status_code == 200
    accounts = client.get(
        "http://localhost:8000/accounts?email_like=email@",
        headers=auth_header(superadmin_token),
    ).json()
    assert len(accounts) == 1
    assert accounts[0]["email"] == "email@gmail.com"


def test_sort_account(superadmin_token):
    accounts = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    assert len(accounts) >= 2
    sorted_emails = sorted([acc["email"] for acc in accounts])
    assert sorted_emails == [
        acc["email"]
        for acc in client.get(
            "http://localhost:8000/accounts?order_by=email",
            headers=auth_header(superadmin_token),
        ).json()
    ]
    assert sorted_emails[::-1] == [
        acc["email"]
        for acc in client.get(
            "http://localhost:8000/accounts?order_by=email&order=desc",
            headers=auth_header(superadmin_token),
        ).json()
    ]


def test_delete_account(superadmin_token):
    accounts = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    assert len(accounts) > 0
    account_ids = {
        ex["id_account"] for ex in accounts if ex["account_category"] == "admin"
    }
    while account_ids:
        account_id = account_ids.pop()
        client.delete(
            f"http://localhost:8000/accounts/{account_id}",
            headers=auth_header(superadmin_token),
        ).json()
        remaining_account_ids = {
            ex["id_account"]
            for ex in client.get(
                "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
            ).json()
            if ex["account_category"] == "admin"
        }
        assert len(remaining_account_ids) == len(account_ids)
        assert account_id not in remaining_account_ids


def test_me_endpoint(regular_token):
    resp = client.get(
        "http://localhost:8000/me", headers=auth_header(regular_token)
    ).json()
    print(resp)
    assert resp["account_category"] == "regular"


def test_me_for_deleted_account():
    new_account = {
        "email": "toBeDeleted@gmail.com",
        "password": "secret",
    }
    good_request(client.post, "http://localhost:8000/register", json=new_account)
    login_resp = good_request(
        client.post, "http://localhost:8000/login", json=new_account
    )
    auth_header = {"Authorization": f"Bearer {login_resp['access_token']}"}
    me_resp = good_request(client.get, "http://localhost:8000/me", headers=auth_header)
    good_request(
        client.delete,
        f"http://localhost:8000/accounts/{me_resp['id_account']}",
        headers=auth_header,
    )
    bad_request(client.get, 404, "http://localhost:8000/me", headers=auth_header)


def test_create_error_account(superadmin_token):
    # Get the initial count of accounts
    accounts_before = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    account_count_before = len(accounts_before)

    # Try creating an account with invalid data
    invalid_account = {"email": "invalid_email", "password": "password1234"}
    resp = client.post(
        "http://localhost:8000/accounts",
        json=invalid_account,
        headers=auth_header(superadmin_token),
    )
    assert resp.status_code == 422  # Expecting a validation error

    # Ensure that the count of accounts remains the same
    accounts_after = client.get(
        "http://localhost:8000/accounts", headers=auth_header(superadmin_token)
    ).json()
    account_count_after = len(accounts_after)
    assert account_count_after == account_count_before


def test_update_account_invalid_email(superadmin_token):
    # Try updating an account with invalid data
    invalid_data = {"email": "invalid_email"}
    resp = client.patch(
        "http://localhost:8000/accounts/1",  # superadmin is ID 1
        json=invalid_data,
        headers=auth_header(superadmin_token),
    )
    assert resp.status_code == 422  # Expecting a validation error


def test_update_account_invalid_email(superadmin_token):
    # Try updating a non-existent account
    non_existent_account_id = 999999  # Assuming this ID doesn't exist
    resp = client.patch(
        f"http://localhost:8000/accounts/{non_existent_account_id}",
        json={"email": "new_email@gmail.com"},
        headers=auth_header(superadmin_token),
    )
    assert resp.status_code == 404  # Expecting a not found error

def test_send_password_mail_superadmin(superadmin_token):
    reset_mail_payload = {"email": "superadmin@gmail.com"}
    resp = client.post(
        "http://localhost:8000/password/forgot",
        json=reset_mail_payload,
        headers=auth_header(superadmin_token),
    )
    assert resp.status_code == 200
    assert "An email has been sent to superadmin@gmail.com with a link for password reset." in resp.json()["result"]

def test_send_password_mail_user(regular_token):
    reset_mail_payload = {"email": "regular@gmail.com"}
    resp = client.post(
        "http://localhost:8000/password/forgot",
        json=reset_mail_payload,
        headers=auth_header(regular_token),
    )
    print(resp.json())
    assert resp.status_code == 200
    assert "An email has been sent to regular@gmail.com with a link for password reset." in resp.json()["result"]