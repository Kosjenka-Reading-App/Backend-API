# Development environment setup

Create the database and fill it with test data.
```bash
cat setup.sql | sqlite3 db.sqlite
cat fill_test_data.sql | sqlite3 db.sqlite
```

Activate the virtual environment and install the required packages.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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


# Sources

1. Using SQL databases in fastAPI: https://fastapi.tiangolo.com/tutorial/sql-databases/
