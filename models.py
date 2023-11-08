import enum

from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base


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


class Category(Base):
    __tablename__ = "category"

    category = Column(String, primary_key=True)
    exercises = relationship("Exercise", secondary=exercise_category)
