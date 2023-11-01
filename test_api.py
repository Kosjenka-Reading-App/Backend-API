import subprocess
import time

import requests
import pytest


@pytest.fixture
def setup_api(scope="module"):
    p = subprocess.Popen(["uvicorn", "main:app"])
    print("Process ID of subprocess %s" % p.pid)
    time.sleep(1);

    yield

    p.terminate()
    returncode = p.wait()
    print("Returncode of subprocess: %s" % returncode) 


def test_get_exercises(setup_api):
    exercises = requests.get("http://localhost:8000/exercises").json()
    assert len(exercises) == 2


def test_get_exercise(setup_api):
    exercises = requests.get("http://localhost:8000/exercises/1").json()
    assert exercises['id'] == 1

