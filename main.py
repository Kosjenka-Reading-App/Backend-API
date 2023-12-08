import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_pagination import Page, add_pagination
import fastapi_pagination
from dotenv import load_dotenv

import crud
import models
import schemas
import auth
from auth_bearer import JWTBearer
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="html_templates")

load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
optional_auth = JWTBearer(auto_error=False)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def assert_first_super_admin():
    db = SessionLocal()
    db_superadmin = (
        db.query(models.Account)
        .filter(models.Account.account_category == models.AccountType.Superadmin)
        .first()
    )
    if db_superadmin is None:
        login, password = (
            os.environ["SUPERADMIN_LOGIN"],
            os.environ["SUPERADMIN_PASSWORD"],
        )
        if not login or not password:
            raise ValueError(
                "SUPERADMIN_LOGIN and SUPERADMIN_PASSWORD must be set for the first superadmin"
            )
        account_db = models.Account(
            email=login,
            account_category=models.AccountType.Superadmin,
            password=crud.password_hasher(password),
        )
        db.add(account_db)
        db.commit()
        db.close()


def validate_access_level(
    auth_user: schemas.AuthSchema, access_level: models.AccountType
):
    user_level = models.ACCESS_LEVELS[auth_user.account_category]
    required_level = models.ACCESS_LEVELS[access_level]
    if user_level < required_level:
        raise HTTPException(
            status_code=401,
            detail=f"Permission only for {[lvl for lvl in models.ACCESS_LEVELS if models.ACCESS_LEVELS[lvl] > user_level]}",
        )


def validate_user_belongs_to_account(
    user_id: int,
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    db_user = crud.get_user(db, user_id, auth_user.account_id)
    if (
        db_user is None
        or schemas.UserSchema.model_validate(db_user).id_account != auth_user.account_id
    ):
        raise HTTPException(
            status_code=404,
            detail=f"user with id {user_id} not found for this account",
        )


@app.get("/healthz", status_code=200)
def health_check():
    return {"status": "ok"}


@app.post("/exercises", response_model=schemas.FullExerciseResponse)
def create_exercise(
    exercise: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Admin)
    return crud.create_exercise(db=db, exercise=exercise)


@app.get("/exercises", response_model=Page[schemas.ExerciseResponse])
def read_exercises(
    order_by: schemas.ExerciseOrderBy | None = None,
    order: schemas.Order | None = None,
    complexity: models.Complexity | None = None,
    category: str | None = None,
    title_like: str | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema | None = Depends(optional_auth),
):
    if user_id:
        if not auth_user:
            raise HTTPException(
                status_code=403, detail="account must be authorized to access user data"
            )
        validate_access_level(auth_user, models.AccountType.Regular)
        validate_user_belongs_to_account(user_id, auth_user, db)
    if category:
        db_category = crud.get_category(db, category)
        if db_category is None:
            db_category = models.Category(category="NULL")
    else:
        db_category = None
    exercises = crud.get_exercises(
        db,
        order_by=order_by,
        order=order,
        complexity=complexity,
        category=db_category,
        title_like=title_like,
        user_id=user_id,
    )
    if user_id:
        return fastapi_pagination.paginate(exercises)
    return exercises


@app.get("/exercises/{exercise_id}", response_model=schemas.FullExerciseResponse)
def read_exercise(
    exercise_id: int,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema | None = Depends(optional_auth),
):
    if user_id:
        if not auth_user:
            raise HTTPException(
                status_code=403, detail="account must be authorized to access user data"
            )
        validate_access_level(auth_user, models.AccountType.Regular)
        validate_user_belongs_to_account(user_id, auth_user, db)
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id, user_id=user_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    return db_exercise


@app.delete("/exercises/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Admin)
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    crud.delete_exercise(db=db, exercise_id=exercise_id)
    return {"ok": True}


@app.patch("/exercises/{exercise_id}", response_model=schemas.FullExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise: schemas.ExercisePatch,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Admin)
    stored_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if stored_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    updated_exercise = crud.update_exercise(
        db, exercise_id=exercise_id, exercise=exercise
    )
    return updated_exercise


@app.post("/exercises/{exercise_id}/track_completion")
def track_exercise_completion(
    exercise_id: int,
    completion: schemas.ExerciseCompletion,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Regular)
    validate_user_belongs_to_account(completion.user_id, auth_user, db)
    db_user = crud.get_user(db, completion.user_id, auth_user.account_id)
    db_exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="exercise not found")
    db_do_exercise = crud.update_exercise_completion(
        db, db_user, db_exercise, completion
    )
    return db_do_exercise


@app.post("/accounts")
async def create_account(
    account_in: schemas.AccountPostAdminIn,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Superadmin)

    try:
        await auth.send_account_password_mail(account=account_in)
        return {
            "result": f"An email has been sent to {account_in.email} with a link for activating the account."
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")


@app.post("/accounts/activate", response_model=schemas.AccountOut)
def account_reset_password_result(
    input: schemas.ActivateAccountSchema,
    db: Session = Depends(get_db),
):
    result = auth.check_account_activation_token(input.token)
    if result == None:
        raise HTTPException(status_code=401, detail="Token is expired or not valid")
    if crud.email_is_registered(db, result["email"]):
        raise HTTPException(status_code=409, detail="Email already registered")
    if result["is_superadmin"]:
        type_account = models.AccountType.Superadmin
    else:
        type_account = models.AccountType.Admin
    new_account = schemas.AccountPostAdmin
    new_account.email = result["email"]
    new_account.password = input.password
    account_saved = crud.create_account(db, new_account, type_account)
    return account_saved


@app.post("/register", response_model=schemas.AccountOut)
def register_account(account_in: schemas.AccountIn, db: Session = Depends(get_db)):
    if crud.email_is_registered(db, account_in.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    account_saved = crud.create_account(db, account_in, models.AccountType.Regular)
    return account_saved


@app.get("/accounts", response_model=Page[schemas.AccountOut])
def get_all_accounts(
    order_by: schemas.AccountOrderBy | None = None,
    order: schemas.Order | None = None,
    email_like: str | None = None,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Superadmin)
    accounts = crud.get_accounts(
        db,
        order_by=order_by,
        order=order,
        email_like=email_like,
    )
    return accounts


@app.get("/accounts/{account_id}")
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    account = crud.get_account(db, auth_user=auth_user, account_id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    return account


@app.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    db_account = crud.get_account(db, auth_user=auth_user, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="account not found")
    crud.delete_account(db=db, account_id=account_id)
    return {"message": "account deleted"}


@app.patch("/accounts/{account_id}")
def update_account(
    account_id: int,
    updated_data: schemas.AccountPatch,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    account = crud.get_account(db, auth_user=auth_user, account_id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="account not found")
    changed_account = crud.update_account(
        db, account_id=account_id, account=updated_data
    )
    return changed_account


# User
@app.get("/users", response_model=Page[schemas.UserSchema])
def read_all_users(
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    users = crud.get_users(db, account_id=auth_user.account_id)
    return users


@app.get("/users/{user_id}", response_model=schemas.UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    db_user = crud.get_user(db, user_id=user_id, account_id=auth_user.account_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.patch("/users/{user_id}")
def update_user(
    user_id: int,
    user: schemas.UserPatch,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    db_user = crud.get_user(db, user_id=user_id, account_id=auth_user.account_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user = crud.update_user(db, user_id=user_id, user=user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    db_user = crud.get_user(db, user_id=user_id, account_id=auth_user.account_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db=db, user_id=user_id)
    return {"ok": True}


@app.post("/users", response_model=schemas.UserSchema)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    return crud.create_user(db=db, account_id=auth_user.account_id, user=user)


@app.post("/categories/{category}", response_model=schemas.Category)
def create_category(
    category: str,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Admin)
    stored_category = crud.get_category(db, category=category)
    if stored_category is not None:
        raise HTTPException(status_code=404, detail="category already exists")
    return crud.create_category(db=db, category=category)


@app.get("/categories", response_model=Page[schemas.Category])
def read_categories(
    order: schemas.Order | None = None,
    name_like: str | None = None,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Regular)
    db_categories = crud.get_categories(db, order=order, name_like=name_like)
    return db_categories


@app.delete("/categories/{category}")
def delete_category(
    category: str,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Admin)
    db_category = crud.get_category(db, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="category not found")
    crud.delete_category(db, category=category)
    return {"ok": True}


@app.patch("/categories/{old_category}", response_model=schemas.Category)
def update_category(
    old_category: str,
    new_category: schemas.Category,
    db: Session = Depends(get_db),
    auth_user: schemas.AuthSchema = Depends(JWTBearer()),
):
    validate_access_level(auth_user, models.AccountType.Admin)
    stored_category = crud.get_category(db, category=old_category)
    if stored_category is None:
        raise HTTPException(status_code=404, detail="category not found")
    updated_category = crud.update_category(
        db, old_category=old_category, new_category=new_category
    )
    return updated_category


# Auth
@app.post("/login", response_model=schemas.TokenSchema)
def login(login: schemas.LoginSchema, db: Session = Depends(get_db)):
    auth_account = auth.get_user(db=db, login=login)
    if auth_account is None:
        raise HTTPException(status_code=400, detail="Username/Password wrong")
    token = auth.generateToken(account=auth_account)
    return token


@app.post("/refresh", response_model=schemas.TokenSchema)
def refresh(token: schemas.RefreshSchema):
    decoded_token = auth.decodeJWT(token=token.refresh_token)
    if decoded_token is None:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    if decoded_token.is_access_token != False:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    refresh_token = auth.generate_refresh_token(
        old_token=token.refresh_token, decoded_token=decoded_token
    )
    return refresh_token


@app.get("/me", response_model=schemas.AccountOut)
def me(
    db: Session = Depends(get_db), auth_user: schemas.AuthSchema = Depends(JWTBearer())
):
    validate_access_level(auth_user, models.AccountType.Regular)
    db_account = crud.get_account(db, auth_user, auth_user.account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account


# Password Reset
@app.post("/password/forgot")
async def send_password_mail(
    forget_passwort_input: schemas.ForgetPasswordSchema,
    db: Session = Depends(get_db),
):
    account = auth.get_account_by_email(db=db, email=forget_passwort_input.email)
    if account is None:
        return {
            "result": f"An email has been sent to {forget_passwort_input.email} with a link for password reset."
        }
        # raise HTTPException(status_code=404, detail=f"Email not found")
    try:
        await auth.send_password_reset_mail(account=account)
        return {
            "result": f"An email has been sent to {account.email} with a link for password reset."
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")


@app.post("/password/reset", response_model=schemas.ResetPasswordResultSchema)
def account_reset_password_result(
    input: schemas.ResetPasswordSchema,
    db: Session = Depends(get_db),
):
    result = auth.reset_password(db, input.password, input.token)
    if result == "SUCCESS":
        result = schemas.ResetPasswordResultSchema
        result.details = "Successfully updated password"
        return result
    elif result == "TOKEN_EXPIRED":
        raise HTTPException(status_code=401, detail="Token is expired")
    elif result == "EMAIL_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Email not found")
    else:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


assert_first_super_admin()
add_pagination(app)
