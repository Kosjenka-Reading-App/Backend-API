from typing import Optional, List
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Table,
    ForeignKey,
    Enum,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

from database import Base


ACCESS_LEVELS = {
    "superadmin": 3,
    "admin": 2,
    "regular": 1,
}


class AccountType(str, enum.Enum):
    Regular = "regular"
    Admin = "admin"
    Superadmin = "superadmin"


exercise_category = Table(
    "exercise_category",
    Base.metadata,
    Column("category_name", String, ForeignKey("category.category")),
    Column("exercise_id", Integer, ForeignKey("exercise.id")),
)


class DoExercise(Base):
    __tablename__ = "do_exercise"
    exercise_id = Column(Integer, ForeignKey("exercise.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id_user"), primary_key=True)
    user = relationship("User", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="users")
    completion = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    time_spent = Column(Integer, nullable=True)


class Complexity(enum.Enum):
    _easy = "easy"
    _medium = "medium"
    hard = "hard"


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    complexity = Column(Enum(Complexity), nullable=True)
    text = Column(String)
    category = relationship("Category", secondary=exercise_category)
    users = relationship("DoExercise", back_populates="exercise", lazy="dynamic")
    date = Column(DateTime, default=func.now(), onupdate=func.now())


class Account(Base):
    __tablename__ = "account"

    id_account = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    account_category = Column(Enum(AccountType))
    users = relationship("User", back_populates="account")


class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_account = Column(Integer, ForeignKey("account.id_account"))
    username = Column(String)
    proficiency = Column(Float)
    exercises = relationship("DoExercise", back_populates="user", lazy="dynamic")
    account = relationship("Account", back_populates="users")


class Category(Base):
    __tablename__ = "category"

    category = Column(String, primary_key=True)
    exercises = relationship(
        "Exercise", secondary=exercise_category, back_populates="category"
    )
