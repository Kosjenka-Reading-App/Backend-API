from pydantic import BaseModel


class ExerciseBase(BaseModel):
    title: str
    text: str
    category: str
    complexity: float | None = 0.0


class ExerciseCreate(ExerciseBase):
    pass


class Exercise(ExerciseBase):
    id: int

    class Config:
        from_attributes = True