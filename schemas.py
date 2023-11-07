from typing import Optional
from pydantic import BaseModel, EmailStr


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
    id_account: int
    email: EmailStr
    is_user: bool
    is_super_admin: bool

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
