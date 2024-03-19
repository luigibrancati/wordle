from fastapi import Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi import status
from ..db import crud
from ..db.database import get_db
from .. import schemas
from sqlalchemy.orm import Session
from ..auth import auth_utils
from typing import Annotated
from ..game_status import game_status
from .common import templates


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


@router.post("/remove_letter", response_class=RedirectResponse)
async def remove_letter(request: Request):
    game_status.remove_last_letter()
    return RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)


@router.post("/check_word", response_class=RedirectResponse)
async def check_word(request: Request, user: Annotated[schemas.User | None, Depends(auth_utils.manager.optional)], db: Annotated[Session, Depends(get_db)]):
    word_in_list = game_status.last_word_is_in_wordlist()
    game_status.check_last_word()
    if game_status.finished and user is not None:
        game = schemas.GameBase(won=game_status.won, steps=game_status.curr_row + 1, solution=game_status.solution, user_id=user.id)
        crud.create_game(db, game)
    return templates.TemplateResponse(
            request=request, name="index.html", context={"status": game_status, "word_in_list": word_in_list, "user": user}, status_code=200
        )


@router.post("/reset", response_class=RedirectResponse)
async def reset(request: Request):
    game_status.reset()
    return RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)
