from fastapi import Depends, APIRouter, HTTPException
from ..db import crud
from ..db.database import get_db
from .. import schemas
from sqlalchemy.orm import Session
from typing import Annotated


router = APIRouter(prefix='/games')


@router.get("/", response_model=list[schemas.Game])
async def read_games(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    return crud.get_games(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Game)
async def create_game_for_user(
    game: schemas.GameBase, db: Annotated[Session, Depends(get_db)]
):
    user_id = game.user_id
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_game(db=db, game=game)


@router.get("/{game_id}", response_model=schemas.Game)
async def read_game(game_id: int, db: Annotated[Session, Depends(get_db)]):
    db_game = crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game
