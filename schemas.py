from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr

import models


class ExerciseOrderBy(Enum):
    category = "category"
    complexity = "complexity"
    title = "title"


class ExerciseFilterBy(Enum):
    category = "category"
    complexity = "complexity"


class Order(Enum):
    asc = "asc"
    desc = "desc"


class Category(BaseModel):
    category: str


class ExerciseResponse(BaseModel):
    id: int
    title: str
    complexity: models.Complexity | None
    category: List[Category]


class ExerciseCreate(BaseModel):
    title: str
    text: str
    complexity: models.Complexity | None = None
    category: Optional[List[str]] = []


class ExercisePatch(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    complexity: Optional[models.Complexity] = None
    category: Optional[List[str]] = []


class FullExerciseResponse(ExerciseResponse):
    text: str


class AccountIn(BaseModel):
    email: EmailStr
    password: str
    is_user: bool
    is_super_admin: bool


class AccountOut(BaseModel):
    id_account: int
    email: EmailStr
    is_user: bool
    is_super_admin: bool


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
