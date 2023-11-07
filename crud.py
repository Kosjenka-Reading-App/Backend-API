from sqlalchemy.orm import Session

import models, schemas


def get_exercise(db: Session, exercise_id: int):
    return db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()


def get_exercises(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Exercise).offset(skip).limit(limit).all()


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

#Users
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id_user == user_id).first()

def update_user(db: Session, user_id: int, user: schemas.UserPatch):
    user_id = db.query(models.User).filter(models.User.id_user == user_id).first()
    update_data = user.model_dump(exclude_unset=True)
    for key in update_data:
        setattr(user_id, key, update_data[key])
    db.commit()
    db.refresh(user_id)
    return user_id

def delete_user(db: Session, user_id: int):
    db.delete(db.query(models.User).filter(models.User.id_user == user_id).first())
    db.commit()
    
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        id_account = user.id_account,
        username = user.username, 
        proficiency = user.proficiency,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user