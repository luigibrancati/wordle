from fastapi import Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from ..db import crud
from ..db.database import get_db
from .. import schemas
from sqlalchemy.orm import Session
from ..auth import auth_utils
from typing import Annotated
from .common import templates


router = APIRouter(prefix='/leaderboard')


@router.get("/", response_class=HTMLResponse)
async def show_leaderboard(request: Request, user: Annotated[schemas.User | None, Depends(auth_utils.manager.optional)], db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 100):
    players = sorted(crud.get_users(db, skip=skip, limit=limit), key=lambda a: a.points, reverse=True)
    return templates.TemplateResponse(
        request=request, name="leaderboard/leaderboard.html", context={"players": players, "user": user}, status_code=200
    )
