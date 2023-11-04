from uuid import UUID
from sqlalchemy.orm import Session

import models, schemas
import bcrypt

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

def password_hasher(raw_password:str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def save_user(db: Session,account_in:schemas.AccountIn):
    hashed_password = password_hasher(account_in.password)
    account_db = models.Account(
        email=account_in.email, 
        is_user=account_in.is_user,
        is_super_admin=account_in.is_super_admin,
        password=hashed_password)
    db.add(account_db)
    db.commit()
    db.refresh(account_db)
    return account_db

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id_account == account_id).first()

def delete_account(db: Session, account_id: UUID):
    db.delete(db.query(models.Account).filter(models.Account.id_account == account_id).first())
    db.commit()

def update_account(db: Session, account_id: int, account: schemas.AccountOut):
    stored_account = db.query(models.Account).filter(models.Account.id_account == account_id).first()
    if stored_account is None:
        return None
    update_data = account.model_dump(exclude_unset=True)
    for key in update_data:
        setattr(stored_account, key, update_data[key])
    db.commit()
    db.refresh(stored_account)
    return stored_account