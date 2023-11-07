from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import dotenv_values


SQLALCHEMY_DATABASE_URL = dotenv_values()["DATABASE_URL"]
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL not provided in .env")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": not ("sqlite" in SQLALCHEMY_DATABASE_URL)},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
