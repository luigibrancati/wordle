from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from .db import models
from .db.database import engine
from .routers import board, debug, game, user, leaderboard, dashboard
from .conf import STATIC_DIR


app = FastAPI()
app.mount(str(STATIC_DIR), StaticFiles(directory=str(STATIC_DIR)), name="static")


models.Base.metadata.create_all(bind=engine)


app.include_router(board.router)
app.include_router(user.router)
app.include_router(game.router)
app.include_router(leaderboard.router)
app.include_router(dashboard.router)
app.include_router(debug.router)


@app.get("/", response_class=RedirectResponse)
def index(request: Request):
    return RedirectResponse(request.url_for("show_board"), status_code=status.HTTP_302_FOUND)
