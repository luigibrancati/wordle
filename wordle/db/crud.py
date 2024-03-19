from sqlalchemy.orm import Session
from . import models
from .. import schemas
from ..auth import auth_utils
from ..db import database


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(user_id: int, db: Session):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(username: str, db: Session = next(database.get_db())):
    return db.query(models.User).filter(models.User.username == username).first()


def update_user_points(user_id: int, new_points: float, db: Session):
    db_user = get_user(user_id=user_id, db=db)
    db_user.points = new_points
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user(db: Session, user: schemas.UserLogin):
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).offset(skip).limit(limit).all()


def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()


def create_game(db: Session, game: schemas.GameBase):
    db_game = models.Game(**game.model_dump())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game