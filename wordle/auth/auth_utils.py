from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..db import crud
from .auth_conf import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi_login import LoginManager
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
manager = LoginManager(SECRET_KEY, "/login", use_cookie=True, use_header=False, default_expiry=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session):
    user = crud.get_user_by_name(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
