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
