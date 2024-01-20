from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from wordle_status import WordleStatus


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
qwerty_keyboard_keys = [['q', 'w', 'e', 'r', 't','y','u','i','o','p'],['a','s','d','f','g','h','j','k','l'],['z','x','c','v','b','n','m']]
wordle_status = WordleStatus()


@app.get("/", response_class=HTMLResponse)
async def show_board(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "keys": qwerty_keyboard_keys}
    )


@app.get("/add_letter/{letter}", response_class=RedirectResponse)
async def add_letter(letter: str):
    wordle_status.add_letter(letter)
    return RedirectResponse("/")


@app.get("/check_word", response_class=RedirectResponse)
async def check_word():
    wordle_status.check_last_word()
    return RedirectResponse("/")


@app.get("/remove_letter", response_class=RedirectResponse)
async def remove_letter():
    wordle_status.remove_last_letter()
    return RedirectResponse("/")


@app.get("/reset", response_class=RedirectResponse)
async def reset():
    wordle_status.reset()
    return RedirectResponse("/")
