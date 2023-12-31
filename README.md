# Development environment setup

Activate the virtual environment and install the required packages.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run the API server.
```bash
uvicorn main:app --reload
```

Main API entrypoint: http://127.0.0.1:8000

FastAPI generated docs: http://127.0.0.1:8000/docs

ReDoc generated docs: http://127.0.0.1:8000/redoc


# Testing

Make sure the local server is running
```
uvicorn main:app
```
Launch tests from the root directory with
```
python3 -m pytest
```

To experiment with the ORM, run:
```
ipython3 -i test/sqlalchemy_console.py
```

To see the coverage report:
```
coverage run -m pytest
coverage report
coverage html
```


# Sources

1. Using SQL databases in fastAPI: https://fastapi.tiangolo.com/tutorial/sql-databases/
