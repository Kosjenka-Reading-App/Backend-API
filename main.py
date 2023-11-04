from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/exercises/", response_model=schemas.ExerciseFull)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    return crud.create_exercise(db=db, exercise=exercise)


@app.get("/exercises/", response_model=list[schemas.Exercise])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exercises = crud.get_exercises(db, skip=skip, limit=limit)
    return exercises


@app.get("/exercises/{exercise_id}", response_model=schemas.ExerciseFull)
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


@app.patch("/exercises/{exercise_id}")
def update_exercise(exercise_id: int, exercise: schemas.ExercisePatch, db: Session = Depends(get_db)):
    updated_exercise = crud.update_exercise(db, exercise_id=exercise_id, exercise=exercise)
    if updated_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return updated_exercise

@app.post("/accounts/", response_model=schemas.AccountOut)
def create_account(account_in: schemas.AccountIn,db: Session = Depends(get_db)):
    account_saved= crud.save_user(db,account_in)
    return account_saved

@app.get("/accounts/", response_model=list[schemas.AccountOut])
def get_all_accounts(db: Session = Depends(get_db)):
    accounts = db.query(models.Account).all()
    if not accounts:
        return []
    return accounts

@app.delete("/accounts/{account_id}")
def delete_account(account_id: UUID, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="account not found")
    crud.delete_account(db=db, account_id=account_id)
    return {"message": "account deleted"}


@app.patch("/accounts/{account_id}")
def update_account(account_id: int, account: schemas.AccountIn, db: Session = Depends(get_db)):
    updated_account = crud.update_account(db, account_id=account_id, account=account)
    if updated_account is None:
        raise HTTPException(status_code=404, detail="account not found")
    return updated_account