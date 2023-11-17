def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def good_request(request_function, *args, **kwargs):
    resp = request_function(*args, **kwargs)
    assert resp.status_code == 200
    return resp.json()


def bad_request(request_function, status_code, *args, **kwargs):
    resp = request_function(*args, **kwargs)
    assert resp.status_code == status_code
    return resp.json()
