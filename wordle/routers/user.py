from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi import status
from ..db.database import  get_db
from .. import schemas
from sqlalchemy.orm import Session
from ..auth import auth_utils, auth_forms
from typing import Annotated
from ..db import crud
from .common import templates


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


@router.get("/{username}/access_token")
async def access_token(
    username: str,
) -> str:
    access_token = auth_utils.manager.create_access_token(
        data={"sub": username}
    )
    return access_token


async def _login_redirect(request: Request, username: str):
    token = await access_token(username=username)
    response = RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)
    auth_utils.manager.set_cookie(response, token)
    return response


@router.get("/login")
@router.post("/login")
async def login(
    request: Request,
):
    form_data = await auth_forms.LoginForm.from_formdata(request=request)
    if request.method == "POST":
        if await form_data.validate_on_submit():
            return await _login_redirect(request, form_data.username.data)
    return templates.TemplateResponse(
        request=request, name="forms/login.html", context={"form": form_data, "user": None}, status_code=200
    )


@router.get("/register")
@router.post("/register")
async def register(
    request: Request
):
    form_data = await auth_forms.RegisterForm.from_formdata(request=request)
    if request.method == "POST":
        if await form_data.validate_on_submit():
            db = next(get_db())
            await create_user(user=schemas.UserLogin(username=form_data.username.data, password=form_data.password.data), db=db)
            return await _login_redirect(request, form_data.username.data)
    return templates.TemplateResponse(
        request=request, name="forms/register.html", context={"form": form_data, "user": None}, status_code=200
    )


@router.post("/logout")
async def logout(
    request: Request
) -> str:
    response = RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)
    response.delete_cookie(auth_utils.manager.cookie_name)
    return response


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
