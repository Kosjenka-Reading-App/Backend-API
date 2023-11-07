import enum

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/healthz", status_code=200)
def health_check():
    return {"status": "ok"}


@app.post("/exercises/", response_model=schemas.FullExerciseResponse)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = crud.create_exercise(db=db, exercise=exercise)
    return db_exercise


@app.get("/exercises/", response_model=list[schemas.ExerciseResponse])
def read_exercises(
    skip: int = 0,
    limit: int = 100,
    order_by: schemas.ExerciseOrderBy | None = None,
    order: schemas.Order | None = None,
    complexity: models.Complexity | None = None,
    category: str | None = None,
    title_like: str | None = None,
    db: Session = Depends(get_db),
):
    if category:
        db_category = crud.get_category(db, category)
        if db_category is None:
            return []
    else:
        db_category = None
    exercises = crud.get_exercises(
        db, skip=skip, limit=limit, order_by=order_by, order=order, complexity=complexity, category=db_category, title_like=title_like
    )
    return exercises


@app.get("/exercises/{exercise_id}", response_model=schemas.FullExerciseResponse)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return db_exercise


@app.delete("/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    crud.delete_exercise(db=db, exercise_id=exercise_id)
    return {"ok": True}


@app.patch("/exercises/{exercise_id}", response_model=schemas.FullExerciseResponse)
def update_exercise(
    exercise_id: int, exercise: schemas.ExercisePatch, db: Session = Depends(get_db)
):
    stored_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if stored_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    updated_exercise = crud.update_exercise(
        db, exercise_id=exercise_id, exercise=exercise
    )
    return updated_exercise


@app.post("/accounts/", response_model=schemas.AccountOut)
def create_account(account_in: schemas.AccountIn, db: Session = Depends(get_db)):
    account_saved = crud.save_user(db, account_in)
    return account_saved


@app.get("/accounts/", response_model=list[schemas.AccountOut])
def get_all_accounts(db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db)
    return accounts


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="account not found")
    crud.delete_account(db=db, account_id=account_id)
    return {"message": "account deleted"}


@app.patch("/accounts/{account_id}")
def update_account(
    account_id: int, account: schemas.AccountIn, db: Session = Depends(get_db)
):
    account = crud.get_account(db, account_id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    changed_account = crud.update_account(db, account_id=account_id, account=account)
    return changed_account


# User
@app.get("/users/", response_model=list[schemas.UserSchema])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.patch("/users/{user_id}")
def update_user(user_id: int, user: schemas.UserPatch, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user = crud.update_user(db, user_id=user_id, user=user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db=db, user_id=user_id)
    return {"ok": True}


@app.post("/users/", response_model=schemas.UserSchema)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.post("/categories/{category}", response_model=schemas.Category)
def create_category(category: str, db: Session = Depends(get_db)):
    stored_category = crud.get_category(db, category=category)
    if stored_category is not None:
        raise HTTPException(status_code=404, detail="category already exists")
    return crud.create_category(db=db, category=category)


@app.get("/categories/", response_model=list[str])
def read_categories(db: Session = Depends(get_db)):
    db_categories = crud.get_categories(db)
    return db_categories


@app.delete("/categories/{category}")
def delete_category(category: str, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="category not found")
    crud.delete_category(db, category=category)
    return {"ok": True}


@app.patch("/categories/{old_category}", response_model=schemas.Category)
def update_category(
    old_category: str, new_category: schemas.Category, db: Session = Depends(get_db)
):
    stored_category = crud.get_category(db, category=old_category)
    if stored_category is None:
        raise HTTPException(status_code=404, detail="category not found")
    updated_category = crud.update_category(
        db, old_category=old_category, new_category=new_category
    )
    return updated_category
