from sqlalchemy import case
from sqlalchemy.orm import Session

import models, schemas
import bcrypt


order_by_column = {
    schemas.ExerciseOrderBy.category: models.Exercise.category,
    schemas.ExerciseOrderBy.complexity: models.Exercise.complexity,
    schemas.ExerciseOrderBy.title: models.Exercise.title,
}


def get_exercise(db: Session, exercise_id: int):
    return db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()


def get_exercises(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    order_by: schemas.ExerciseOrderBy | None = None,
    order: schemas.Order | None = None,
    complexity: models.Complexity | None = None,
    category: models.Category | None = None,
    title_like: str | None = None,
):
    exercises = db.query(models.Exercise)
    if complexity:
        exercises = exercises.filter(models.Exercise.complexity == complexity)
    if category:
        exercises = exercises.filter(models.Exercise.category.contains(category))
    if title_like:
        exercises = exercises.filter(models.Exercise.title.like(f"%{title_like}%"))
    if order_by:
        exercises = exercises.order_by(
            order_by_column[order_by].desc()
            if order == schemas.Order.desc
            else order_by_column[order_by]
        )
    return exercises.offset(skip).limit(limit).all()


def create_exercise(db: Session, exercise: schemas.ExerciseCreate):
    db_exercise = models.Exercise(
        title=exercise.title,
        text=exercise.text,
        complexity=exercise.complexity,
    )
    db.add(db_exercise)
    if exercise.category:
        for category in exercise.category:
            db_category = get_category(db, category)
            if db_category is None:
                db_category = create_category(db, category)
            db_exercise.category.append(db_category)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(db: Session, exercise_id: int):
    db.delete(
        db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    )
    db.commit()


def update_exercise(db: Session, exercise_id: int, exercise: schemas.ExercisePatch):
    stored_exercise = (
        db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    )
    update_data = exercise.model_dump(exclude_unset=True)
    if exercise.category:
        _update_exercise_categories(db, stored_exercise, exercise.category)
        update_data.pop("category")
    for key in update_data:
        setattr(stored_exercise, key, update_data[key])
    db.commit()
    db.refresh(stored_exercise)
    return stored_exercise


def password_hasher(raw_password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def get_account(db: Session, account_id: int):
    return (
        db.query(models.Account).filter(models.Account.id_account == account_id).first()
    )


def delete_account(db: Session, account_id: int):
    db.delete(
        db.query(models.Account).filter(models.Account.id_account == account_id).first()
    )
    db.commit()


def update_account(db: Session, account_id: int, account: schemas.AccountOut):
    stored_account = (
        db.query(models.Account).filter(models.Account.id_account == account_id).first()
    )
    update_data = account.model_dump(exclude_unset=True)
    for key in update_data:
        setattr(stored_account, key, update_data[key])
    db.commit()
    db.refresh(stored_account)
    return stored_account


def get_accounts(db: Session):
    return db.query(models.Account).all()


def save_user(db: Session, account_in: schemas.AccountIn):
    hashed_password = password_hasher(account_in.password)
    account_db = models.Account(
        email=account_in.email,
        is_user=account_in.is_user,
        is_super_admin=account_in.is_super_admin,
        password=hashed_password,
    )
    db.add(account_db)
    db.commit()
    db.refresh(account_db)
    return account_db


# Users
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
        id_account=user.id_account,
        username=user.username,
        proficiency=user.proficiency,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def _update_exercise_categories(
    db: Session, exercise: models.Exercise, categories: list[str]
):
    new_categories = []
    for category in categories:
        db_category = get_category(db, category)
        if db_category is None:
            db_category = create_category(db, category)
        new_categories.append(db_category)
    exercise.category = new_categories


def get_categories(db: Session):
    return [cat.category for cat in db.query(models.Category).all()]


def get_category(db: Session, category: str):
    return (
        db.query(models.Category).filter(models.Category.category == category).first()
    )


def create_category(db: Session, category: str):
    db_category = models.Category(
        category=category,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category: str):
    db.delete(
        db.query(models.Category).filter(models.Category.category == category).first()
    )
    db.commit()


def update_category(db: Session, old_category: str, new_category: schemas.Category):
    stored_category = (
        db.query(models.Category)
        .filter(models.Category.category == old_category)
        .first()
    )
    setattr(stored_category, "category", new_category.category)
    db.commit()
    db.refresh(stored_category)
    return stored_category
