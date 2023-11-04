from typing import Optional, List

from pydantic import BaseModel


class Category(BaseModel):
    category: str


class ExerciseBase(BaseModel):
    title: str
    complexity: float | None = 0.0
    category: List[str] = []


class Exercise(ExerciseBase):
    id: int

    class Config:
        from_attributes = True


class ExerciseFull(Exercise):
    text: str


class ExerciseCreate(ExerciseBase):
    text: str


class ExercisePatch(ExerciseBase):
    title: Optional[str] = None
    text: Optional[str] = None
    complexity: Optional[float] = None

#Users
class UserSchema(BaseModel):
    id_user : int
    id_account :int
    username : str
    proficiency : float | None = 0.0  

class UserPatch(BaseModel):
    username : Optional[str] = None
    proficiency : Optional[float] = None 

class UserCreate(BaseModel):
    id_account : int
    username : str
    proficiency : float | None = 0.0  
