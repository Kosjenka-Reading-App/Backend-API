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


# NOTES ON WORK IN PROGRESS


db_exercise = (
    db.query(models.DoExercise)
    .select_from(models.Exercise)
    .join(models.Exercise.users)
    .filter(models.Exercise.id == 1)
    .filter(models.DoExercise.user_id == 1)
    .add_entity(models.Exercise)
    .first()
)
exercise_completion = schemas.ExerciseCompletion.model_validate(db_exercise[0])
exercise = schemas.FullExerciseResponse.model_validate(db_exercise[1])
exercise.completion = exercise_completion

db_exercises = (
    db.query(models.Exercise)
    .join(models.DoExercise, isouter=True)
    .add_entity(models.DoExercise)
    .filter(or_(models.DoExercise.user_id == 1, models.Exercise.users == None))
    .all()
)
