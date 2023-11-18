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
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercise.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id_user"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(back_populates="users")
    completion: Mapped[Optional[int]]
    position: Mapped[Optional[int]]
    time_spent: Mapped[Optional[int]]


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
    category = relationship(
        "Category", secondary=exercise_category, back_populates="exercises"
    )
    users: Mapped[List["DoExercise"]] = relationship(
        back_populates="exercise", lazy="dynamic"
    )
    date = Column(DateTime, default=func.now(), onupdate=func.now())


class Account(Base):
    __tablename__ = "account"

    id_account = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    account_category = Column(Enum(AccountType))


class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_account = Column(Integer)
    username = Column(String)
    proficiency = Column(Float)
    exercises: Mapped[List["DoExercise"]] = relationship(
        back_populates="user", lazy="dynamic"
    )


class Category(Base):
    __tablename__ = "category"

    category = Column(String, primary_key=True)
    exercises = relationship("Exercise", secondary=exercise_category)
