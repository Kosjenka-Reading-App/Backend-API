import time
from conftest import client

import pytest

def test_create_account():
        accounts = client.get('http://localhost:8000/accounts').json()     
        account_count = len(accounts)
        new_account = {
            'email': 'email@gmail.com',
            'password': 'secret',
            'is_user': True,
            'is_super_admin' : False
        }
        created_account = client.post('http://localhost:8000/accounts', json=new_account).json()
        accounts = client.get('http://localhost:8000/accounts').json()
        assert len(accounts) == account_count + 1


def test_update_account():
    accounts = client.get('http://localhost:8000/accounts').json()
    account_id = accounts[0]['id_account']
    original_account = client.get(f'http://localhost:8000/accounts/{account_id}').json()
    body = {'email': 'update@gmail.com'}
    client.patch(f'http://localhost:8000/accounts/{account_id}', json=body).json()
    updated_account = client.get(f'http://localhost:8000/accounts/{account_id}').json()
    for key in updated_account:
        if key == 'email':
            assert updated_account[key] == 'update@gmail.com'
            continue
        assert updated_account[key] == original_account[key]


def test_delete_account():
    accounts = client.get('http://localhost:8000/accounts').json()
    assert len(accounts) > 0
    account_ids = {ex['id_account'] for ex in accounts}
    while account_ids:
        account_id = account_ids.pop()
        client.delete(f'http://localhost:8000/accounts/{account_id}').json()
        remaining_account_ids = {ex['id_account'] for ex in client.get('http://localhost:8000/accounts').json()}
        assert len(remaining_account_ids) == len(account_ids)
        assert account_id not in remaining_account_ids

