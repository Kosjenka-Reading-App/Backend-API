from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr
from datetime import datetime

import models


class ExerciseOrderBy(Enum):
    category = "category"
    complexity = "complexity"
    title = "title"
    date = "date"


class ExerciseFilterBy(Enum):
    category = "category"
    complexity = "complexity"


class AccountOrderBy(Enum):
    account_category = "account_category"
    email = "email"


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
    date: datetime


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
    # date:datetime


class AccountIn(BaseModel):
    email: EmailStr
    password: str


class AccountOut(BaseModel):
    id_account: int
    email: EmailStr
    account_category: str


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
    username: str
    proficiency: float | None = 0.0


# Auth
class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class AuthSchema(BaseModel):
    account_id: int
    account_category: str
    is_access_token: bool


class RefreshSchema(BaseModel):
    refresh_token: str
