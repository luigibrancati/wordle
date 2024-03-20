from fastapi import Depends, APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi import status
from ..db.database import  get_db
from .. import schemas
from sqlalchemy.orm import Session
from ..auth import auth_exceptions, auth_utils
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..db import crud


router = APIRouter(prefix='/users')


@router.get("/", response_model=list[schemas.User])
async def read_users(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    return crud.get_users(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserLogin, db: Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user_by_name(username=user.username, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
) -> str:
    user = auth_utils.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise auth_exceptions.INCORRECT_EXCEPTION
    access_token = auth_utils.manager.create_access_token(
        data={"sub": user.username}
    )
    return access_token


@router.post("/login_redirect", response_class=RedirectResponse)
async def login_redirect(
    request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
):
    token = await login(form_data=form_data, db=db)
    response = RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)
    auth_utils.manager.set_cookie(response, token)
    return response


@router.post("/register", response_class=RedirectResponse)
async def register(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()], db: Annotated[Session, Depends(get_db)]):
    await create_user(user=schemas.UserLogin(username=username, password=password), db=db)
    return await login_redirect(request=request, form_data=OAuth2PasswordRequestForm(username=username, password=password), db=db)
