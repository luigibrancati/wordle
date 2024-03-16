from fastapi import Depends, FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
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
from .auth.utils import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .auth.exceptions import INCORRECT_EXCEPTION
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

app = FastAPI()
templates = Jinja2Templates(directory=os.path.dirname(os.path.abspath(__file__)) + "/templates")
static_path = os.path.dirname(os.path.abspath(__file__)) + "/static"
app.mount(static_path, StaticFiles(directory=static_path), name="static")
wordle_status = WordleStatus()

models.Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
async def show_board(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "word_in_list": True}, status_code=200
    )


@app.post("/add_letter/{letter}", response_class=RedirectResponse)
async def add_letter(letter: str):
    wordle_status.add_letter(letter)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/check_word", response_class=RedirectResponse)
async def check_word(request: Request):
    wordle_status.check_last_word()
    return templates.TemplateResponse(
            request=request, name="index.html", context={"status": wordle_status, "word_in_list": wordle_status.last_word_in_wordlist()}, status_code=200
        )

@app.post("/remove_letter", response_class=RedirectResponse)
async def remove_letter():
    wordle_status.remove_last_letter()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/reset", response_class=RedirectResponse)
async def reset():
    wordle_status.reset()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/games", response_model=schemas.Game)
async def create_game_for_user(
    game: schemas.GameBase, db: Session = Depends(get_db)
):
    return crud.create_game(db=db, game=game)


@app.get("/games", response_model=list[schemas.Game])
async def read_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = crud.get_games(db, skip=skip, limit=limit)
    return games


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
) -> schemas.Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise INCORRECT_EXCEPTION
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")
