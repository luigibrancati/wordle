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
from .game_status import GameStatus
from sqlalchemy.orm import Session
from .auth import auth_exceptions, auth_utils, auth_conf
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

app = FastAPI()
templates = Jinja2Templates(directory=os.path.dirname(os.path.abspath(__file__)) + "/templates")
static_path = os.path.dirname(os.path.abspath(__file__)) + "/static"
app.mount(static_path, StaticFiles(directory=static_path), name="static")
game_status = GameStatus()

models.Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def show_board(request: Request, user: Annotated[schemas.User | None, Depends(auth_utils.get_current_user)]):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": game_status, "word_in_list": True, "user": user}, status_code=200
    )


@app.post("/add_letter/{letter}", response_class=RedirectResponse)
async def add_letter(letter: str):
    game_status.add_letter(letter)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/remove_letter", response_class=RedirectResponse)
async def remove_letter():
    game_status.remove_last_letter()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/check_word", response_class=RedirectResponse)
async def check_word(request: Request, user: Annotated[schemas.User | None, Depends(auth_utils.get_current_user)], db: Annotated[Session, Depends(get_db)]):
    game_status.check_last_word()
    if game_status.finished and user is not None:
        game = schemas.GameBase(won=game_status.won, steps=game_status.curr_row + 1, solution=game_status.solution, user_id=user.id)
        crud.create_game(db, game)
    return templates.TemplateResponse(
            request=request, name="index.html", context={"status": game_status, "word_in_list": game_status.last_word_is_in_wordlist(), "user": user}, status_code=200
        )


@app.post("/reset", response_class=RedirectResponse)
async def reset():
    game_status.reset()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/solution", response_class=JSONResponse)
async def solution():
    return {"solution": game_status.solution}


@app.get("/users", response_model=list[schemas.User])
async def read_users(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserLogin, db: Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user_by_name(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, username=user.username, password=user.password)


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/games", response_model=list[schemas.Game])
async def read_games(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    games = crud.get_games(db, skip=skip, limit=limit)
    return games


@app.post("/games", response_model=schemas.Game)
async def create_game_for_user(
    game: schemas.GameBase, db: Annotated[Session, Depends(get_db)]
):
    user_id = game.user_id
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_game(db=db, game=game)


@app.get("/games/{game_id}", response_model=schemas.Game)
async def read_game(game_id: int, db: Annotated[Session, Depends(get_db)]):
    db_game = crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game


@app.post("/login")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
) -> schemas.Token:
    user = auth_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise auth_exceptions.INCORRECT_EXCEPTION
    access_token_expires = timedelta(minutes=auth_conf.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/login_redirect", response_class=RedirectResponse)
async def login_redirect(
    request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
):
    token = await login_access_token(form_data=form_data, db=db)
    headers = {**request.headers, **token.header()}
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND, headers=headers)