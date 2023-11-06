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

#User
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