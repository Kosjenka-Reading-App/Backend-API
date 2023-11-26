from conftest import client


def test_healthz():
    resp = client.get("http://localhost:8000/healthz/")
    assert resp.status_code == 200
