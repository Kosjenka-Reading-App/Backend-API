#!/bin/bash
rm db.sqlite
cat setup.sql | sqlite3 db.sqlite

nohup venv/bin/uvicorn main:app &
sleep 3
venv/bin/python3 -m pytest
ps -ef | grep "uvicorn main:app" | grep -v grep | awk '{print $2}' | xargs kill
