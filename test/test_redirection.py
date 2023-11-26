from conftest import client, auth_header


def test_ending_slash(regular_token):
    resp = client.get("http://localhost:8000/me/", headers=auth_header(regular_token))
    assert resp.status_code == 200
