from fastapi import Depends, APIRouter, Body
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi import status
from ..db.database import get_db
from .. import schemas
from sqlalchemy.orm import Session
from ..auth import auth_utils
from typing import Annotated
from ..game_status import game_status
from ..words import words
from .common import templates
from .game import create_game_for_user


router = APIRouter(prefix='/board')


@router.get("/", response_class=HTMLResponse)
async def show_board(request: Request, user: Annotated[schemas.User | None, Depends(auth_utils.manager.optional)]):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": game_status, "word_in_list": True, "user": user}, status_code=200
    )


@router.post("/add_letter/{letter}", response_class=RedirectResponse)
async def add_letter(request: Request, letter: str):
    game_status.add_letter(letter)
    return RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)


@router.post("/check_word")
async def check_word(request: Request, user: Annotated[schemas.User | None, Depends(auth_utils.manager.optional)], db: Annotated[Session, Depends(get_db)], last_word: dict = Body()):
    last_word = last_word['last_word']
    if words.is_in_wordlist(last_word):
        for letter in last_word:
            game_status.add_letter(letter)
        game_status.check_word(last_word)
        if game_status.finished and user is not None:
            points = game_status.num_rows - game_status.curr_row
            game = schemas.GameBase(won=game_status.won, steps=game_status.curr_row + 1, points = points, solution=game_status.solution, user_id=user.id)
            await create_game_for_user(game=game, db=db)
        return RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)


@router.post("/reset", response_class=RedirectResponse)
async def reset(request: Request):
    game_status.reset()
    return RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)
