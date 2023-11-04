from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


exercise_order_by = {"", "complexity"}


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
def read_exercises(skip: int = 0, limit: int = 100, order_by: str = "", title_like: str = "", db: Session = Depends(get_db)):
    if order_by not in exercise_order_by:
        raise HTTPException(status_code=404, detail=f"order_by must be one of {exercise_order_by}")
    exercises = crud.get_exercises(db, skip=skip, limit=limit, order_by=order_by, title_like=title_like)
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

