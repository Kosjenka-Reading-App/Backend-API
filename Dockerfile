#
FROM python:3.11-bullseye

RUN apt update && apt upgrade
RUN apt install sqlite3


#
WORKDIR /app

RUN cat setup.sql | sqlite3 db.sqlite

#
COPY ./requirements.txt /app/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 80

#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
