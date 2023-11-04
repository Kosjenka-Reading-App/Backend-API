import time
import requests
import pytest

def test_create_account():
        accounts = requests.get('http://localhost:8000/accounts').json()     
        account_count = len(accounts)
        new_account = {
            'email': 'email@gmail.com',
            'password': 'secret',
            'is_user': True,
            'is_super_admin' : False
        }
        created_account = requests.post('http://localhost:8000/accounts', json=new_account).json()
        accounts = requests.get('http://localhost:8000/accounts').json()
        assert len(accounts) == account_count + 1


def test_update_account():
    accounts = requests.get('http://localhost:8000/accounts').json()
    account_id = accounts[0]['id_account']
    original_account = requests.get(f'http://localhost:8000/accounts/{account_id}').json()
    body = {'email': 'update@gmail.com'}
    requests.patch(f'http://localhost:8000/accounts/{account_id}', json=body).json()
    updated_account = requests.get(f'http://localhost:8000/accounts/{account_id}').json()
    for key in updated_account:
        if key == 'email':
            assert updated_account[key] == 'update@gmail.com'
            continue
        assert updated_account[key] == original_account[key]


def test_delete_account():
    accounts = requests.get('http://localhost:8000/accounts').json()
    assert len(accounts) > 0
    account_ids = {ex['id_account'] for ex in accounts}
    while account_ids:
        account_id = account_ids.pop()
        requests.delete(f'http://localhost:8000/accounts/{account_id}').json()
        remaining_account_ids = {ex['id_account'] for ex in requests.get('http://localhost:8000/accounts').json()}
        assert len(remaining_account_ids) == len(account_ids)
        assert account_id not in remaining_account_ids

