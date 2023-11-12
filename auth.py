from typing import Type

from sqlalchemy.orm import Session

import models, schemas
import jwt
import time
import bcrypt

JWT_VALID_TIME_ACCESS = 60 * 20  # 20min
JWT_VALID_TIME_REFRESH = 60 * 60 * 24 * 7  # One week
JWT_SECRET = "C0ddVvlcaL4UuChF8ckFQoVCGbtizyvK"
JWT_ALGORITHM = "HS256"


def createToken(
    account_id: int, account_category: str, valid_time: int, is_access_token: bool
):
    payload = {
        "account_id": account_id,
        "account_category": account_category,
        "is_access_token": is_access_token,
        "expires": time.time() + valid_time,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decodeJWT(token: str) -> Type[schemas.AuthSchema] | None:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded_token["expires"] < time.time():
            return None
        ret = schemas.AuthSchema
        ret.account_id = decoded_token["account_id"]
        ret.account_category = decoded_token["account_category"]
        ret.is_access_token = decoded_token["is_access_token"]
        return ret
    except:
        return None


def get_user(db: Session, login: schemas.LoginSchema):
    user = db.query(models.Account).filter(models.Account.email == login.email).first()
    if user == None:
        return None
    if not bcrypt.checkpw(
        login.password.encode("utf-8"), user.password.encode("utf-8")
    ):
        return None
    return user


def generateToken(account: schemas.AccountOut):
    reponse = schemas.TokenSchema
    reponse.access_token = createToken(
        account_id=account.id_account,
        account_category=account.account_category,
        valid_time=JWT_VALID_TIME_ACCESS,
        is_access_token=True,
    )
    reponse.refresh_token = createToken(
        account_id=account.id_account,
        account_category=account.account_category,
        valid_time=JWT_VALID_TIME_REFRESH,
        is_access_token=False,
    )
    return reponse


def generate_refresh_token(old_token: str, decoded_token: Type[schemas.AuthSchema]):
    reponse = schemas.TokenSchema
    reponse.access_token = createToken(
        account_id=decoded_token.account_id,
        account_category=decoded_token.account_category,
        valid_time=JWT_VALID_TIME_ACCESS,
        is_access_token=True,
    )
    reponse.refresh_token = old_token
    return reponse
