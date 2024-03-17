from fastapi import Depends, FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import status
import os
from .db import crud, models
from .db.database import engine, get_db
from . import schemas
from .wordle_status import WordleStatus
from sqlalchemy.orm import Session
# from .auth import auth_exceptions, auth_utils
# from fastapi.security import OAuth2PasswordRequestForm
# from typing import Annotated
# from datetime import timedelta

USERNAME = "luigi"
PASSWORD = "test"

app = FastAPI()
templates = Jinja2Templates(directory=os.path.dirname(os.path.abspath(__file__)) + "/templates")
static_path = os.path.dirname(os.path.abspath(__file__)) + "/static"
app.mount(static_path, StaticFiles(directory=static_path), name="static")
wordle_status = WordleStatus()

models.Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def show_board(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "word_in_list": True, "user": USERNAME}, status_code=200
    )


@app.post("/add_letter/{letter}", response_class=RedirectResponse)
async def add_letter(letter: str):
    wordle_status.add_letter(letter)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/check_word", response_class=RedirectResponse)
async def check_word(request: Request, db: Session = Depends(get_db)):
    wordle_status.check_last_word()
    if wordle_status.finished:
        user = crud.get_user_by_name(db, username=USERNAME)
        game = schemas.GameBase(won=wordle_status.won, steps=wordle_status.curr_row + 1, user_id=user.id)
        crud.create_game(db, game)
    return templates.TemplateResponse(
            request=request, name="index.html", context={"status": wordle_status, "word_in_list": wordle_status.last_word_in_wordlist(), "user": USERNAME}, status_code=200
        )

@app.post("/remove_letter", response_class=RedirectResponse)
async def remove_letter():
    wordle_status.remove_last_letter()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/reset", response_class=RedirectResponse)
async def reset():
    wordle_status.reset()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/solution", response_class=JSONResponse)
async def solution():
    return {"solution": wordle_status.solution}


@app.get("/users", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, username=user.username, password=user.password)


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/games", response_model=list[schemas.Game])
async def read_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = crud.get_games(db, skip=skip, limit=limit)
    return games


@app.post("/games", response_model=schemas.Game)
async def create_game_for_user(
    game: schemas.GameBase, db: Session = Depends(get_db)
):
    user_id = game.user_id
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_game(db=db, game=game)


@app.get("/games/{game_id}", response_model=schemas.Game)
async def read_game(game_id: int, db: Session = Depends(get_db)):
    db_game = crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game


# @app.get("/login")
# async def login():
#     return templates.TemplateResponse(
#         name="login.html", status_code=401
#     )


# @app.post("/login")
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
# ) -> schemas.Token:
#     user = auth_utils.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise auth_exceptions.INCORRECT_EXCEPTION
#     access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = auth_utils.create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return schemas.Token(access_token=access_token, token_type="bearer")
