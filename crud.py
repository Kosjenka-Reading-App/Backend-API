from sqlalchemy.orm import Session

import models, schemas


def get_exercise(db: Session, exercise_id: int):
    return db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()


def get_exercises(db: Session, skip: int = 0, limit: int = 100, order_by: str = "", title_like: str = ""):
    exercises = db.query(models.Exercise)
    if title_like:
        exercises = exercises.filter(models.Exercise.title.like(f"%{title_like}%"))
    if order_by:
        match order_by:
            case "complexity":
                exercises = exercises.order_by(models.Exercise.complexity)
    return exercises.offset(skip).limit(limit).all()


def create_exercise(db: Session, exercise: schemas.ExerciseCreate):
    db_exercise = models.Exercise(
        title=exercise.title,
        text=exercise.text,
        complexity=exercise.complexity,
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(db: Session, exercise_id: int):
    db.delete(db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first())
    db.commit()


def update_exercise(db: Session, exercise_id: int, exercise: schemas.ExercisePatch):
    stored_exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if stored_exercise is None:
        return None
    update_data = exercise.model_dump(exclude_unset=True)
    for key in update_data:
        setattr(stored_exercise, key, update_data[key])
    db.commit()
    db.refresh(stored_exercise)
    return stored_exercise

