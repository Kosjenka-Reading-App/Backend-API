from conftest import client
from utils import auth_header


def test_create_account(superadmin_token):
    accounts = client.get("http://localhost:8000/accounts", headers=auth_header(superadmin_token)).json()
    account_count = len(accounts)
    new_account = {
        "email": "email@gmail.com",
        "password": "secret",
    }
    _ = client.post(
        "http://localhost:8000/accounts", json=new_account, headers=auth_header(superadmin_token)
    ).json()
    accounts = client.get("http://localhost:8000/accounts", headers=auth_header(superadmin_token)).json()
    assert len(accounts) == account_count + 1


def test_update_account(superadmin_token):
    accounts = client.get("http://localhost:8000/accounts", headers=auth_header(superadmin_token)).json()
    account_id = accounts[0]["id_account"]
    original_account = client.get(f"http://localhost:8000/accounts/{account_id}", headers=auth_header(superadmin_token)).json()
    body = {"email": "update@gmail.com"}
    client.patch(f"http://localhost:8000/accounts/{account_id}", json=body, headers=auth_header(superadmin_token)).json()
    updated_account = client.get(f"http://localhost:8000/accounts/{account_id}", headers=auth_header(superadmin_token)).json()
    for key in updated_account:
        if key == "email":
            assert updated_account[key] == "update@gmail.com"
            continue
        assert updated_account[key] == original_account[key]


def test_delete_account(superadmin_token):
    accounts = client.get("http://localhost:8000/accounts", headers=auth_header(superadmin_token)).json()
    assert len(accounts) > 0
    account_ids = {ex["id_account"] for ex in accounts}
    while account_ids:
        account_id = account_ids.pop()
        client.delete(f"http://localhost:8000/accounts/{account_id}", headers=auth_header(superadmin_token)).json()
        remaining_account_ids = {
            ex["id_account"]
            for ex in client.get("http://localhost:8000/accounts", headers=auth_header(superadmin_token)).json()
        }
        assert len(remaining_account_ids) == len(account_ids)
        assert account_id not in remaining_account_ids
