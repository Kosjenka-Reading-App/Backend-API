from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


exercise_category = Table(
    'exercise_category',
    Base.metadata,
    Column('category', ForeignKey('category.category')),
    Column('exercise_id', ForeignKey('exercise.id'))
)


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    complexity = Column(Float)
    text = Column(String)
    category = relationship('Category', secondary=exercise_category, back_populates='exercises')


class Category(Base):
    __tablename__ = 'category'

    category = Column(String, primary_key=True)
    exercises = relationship('Exercise', secondary=exercise_category, back_populates='category')

