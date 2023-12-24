# Load Testing

For the purposes of load testing, a environment resembling production
has to be configured locally.

First, bring up the PostgreSQL container

```bash
docker-compose up 
```

Make sure to provide the local Postgres url in the `.env` file

```bash
DATABASE_URL="postgresql://postgres:example@localhost:5555"
```

Run the application to initialize the database schema

```bash
uvicorn main:app
```

Fill the database with test exercise data (copies of the same book, 320 KB of
text)

```bash
python3 fill_test_data.py
```

Change the database engine configuration in `database.py` to support concurrent
connections. Also make sure to change default postgres `max_connections` in
`/var/lib/postgresql/data/postgres.conf`

```bash
engine = create_engine(
    ...
    pool_size=1000,
)
```

Stop the running application, and start it with 10 workers

```bash
uvicorn main:app --workers 10
```

Start locust (from the `load_test` directory), and go to its WebUI

```bash
locust
```
