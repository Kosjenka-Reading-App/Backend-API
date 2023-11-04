from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4


class ExerciseBase(BaseModel):
    title: str
    complexity: float | None = 0.0


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

class AccountIn(BaseModel) :
    email: EmailStr
    password: str
    is_user: bool
    is_super_admin: bool

class AccountOut(BaseModel) :
    id_account: UUID4
    email: EmailStr
    is_user: bool
    is_super_admin: bool
