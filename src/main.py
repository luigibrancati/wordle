from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from wordle_status import WordleStatus
from fastapi import status
import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.dirname(os.path.abspath(__file__)) + "/templates")
static_path = os.path.dirname(os.path.abspath(__file__)) + "/static"
app.mount(static_path, StaticFiles(directory=static_path), name="static")
wordle_status = WordleStatus()


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
