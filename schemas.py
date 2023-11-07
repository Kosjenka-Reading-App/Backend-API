from typing import Optional, List

from pydantic import BaseModel


class Category(BaseModel):
    category: str


class ExerciseResponse(BaseModel):
    id: int
    title: str
    complexity: float
    category: List[Category]


class ExerciseCreate(BaseModel):
    title: str
    text: str
    complexity: float | None = 0.0
    category: Optional[List[str]] = []


class ExercisePatch(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    complexity: Optional[float] = None
    category: Optional[List[str]] = []


class FullExerciseResponse(ExerciseResponse):
    text: str


# Users
class UserSchema(BaseModel):
    id_user: int
    id_account: int
    username: str
    proficiency: float | None = 0.0


class UserPatch(BaseModel):
    username: Optional[str] = None
    proficiency: Optional[float] = None


class UserCreate(BaseModel):
    id_account: int
    username: str
    proficiency: float | None = 0.0
