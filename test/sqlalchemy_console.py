from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, declarative_base

import models
import schemas


SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite"
connect_args = {"check_same_thread": False}
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
