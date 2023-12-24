# import sqlite3
import psycopg2


if __name__ == "__main__":
    with open("booktext.txt", "r") as f:
        exercise = {"title": "Eduard Kerner", "complexity": "hard", "text": f.read()}
    complexity = ["_easy", "_medium", "hard"]

    conn = psycopg2.connect(
        database="postgres",
        host="localhost",
        port="5555",
        user="postgres",
        password="example",
    )
    # "postgresql://postgres:example@localhost:5555"
    # conn = sqlite3.connect("../db.sqlite")
    cur = conn.cursor()

    for i in range(1000):
        exercise["complexity"] = complexity[i % 3]
        cur.execute(
            "insert into exercise(title, complexity, text, date) values (%s, %s, %s, CURRENT_TIMESTAMP)",
            tuple(exercise.values()),
        )
    conn.commit()
