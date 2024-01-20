import random
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from enum import Enum
from pprint import pprint
import os


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
qwerty_keyboard_keys = [['q', 'w', 'e', 'r', 't','y','u','i','o','p'],['a','s','d','f','g','h','j','k','l'],['z','x','c','v','b','n','m']]

class LetterResult(Enum):
    EMPTY = 'empty'
    TBD = 'tbd'
    ABSENT = 'absent'
    PRESENT = 'present'
    CORRECT = 'correct'


class WordleStatus:
    num_columns = 5
    num_rows = 6

    def __init__(self):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")
        self.word_list = [w[:-1] for w in open(filepath, "r").readlines()]
        self.solution = self.word_list[random.randint(0, len(self.word_list) - 1)]
        self.curr_row = 0
        self.curr_column = 0
        self.words = {i:[None]*self.num_columns for i in range(self.num_rows)}
        self.letter_status = {i:[LetterResult.EMPTY]*self.num_columns for i in range(self.num_rows)}
        self.abset_letters = set()
        self.present_letters = set()
        self.correct_letters = set()
        self.won = False

    def add_letter(self, letter: str) -> None:
        if self.curr_column < 5:
            self.words[self.curr_row][self.curr_column] = letter
            self.letter_status[self.curr_row][self.curr_column] = LetterResult.TBD
            self.curr_column += 1

    def remove_last_letter(self) -> None:
        if self.words[self.curr_row][0] is not None:
            self.curr_column -= 1
            self.words[self.curr_row][self.curr_column] = None
            self.letter_status[self.curr_row][self.curr_column] = LetterResult.EMPTY

    def letter_state(self, letter: str) -> LetterResult:
        if letter in self.abset_letters:
            return LetterResult.ABSENT
        if letter in self.present_letters:
            return LetterResult.PRESENT
        if letter in self.correct_letters:
            return LetterResult.CORRECT
        return LetterResult.TBD

    def check_last_word(self) -> None:
        if self.curr_column == self.num_columns:
            word = "".join(self.words[self.curr_row])
            if word in self.word_list:
                for i, letter in enumerate(word):
                    if letter in self.solution:
                        if letter == self.solution[i]:
                            self.letter_status[self.curr_row][i] = LetterResult.CORRECT
                            self.correct_letters.add(letter)
                            try:
                                self.present_letters.remove(letter)
                            except KeyError:
                                continue
                        else:
                            self.letter_status[self.curr_row][i] = LetterResult.PRESENT
                            self.present_letters.add(letter)
                    else:
                        self.letter_status[self.curr_row][i] = LetterResult.ABSENT
                        self.abset_letters.add(letter)
                if word == self.solution:
                    print("Won")
                    self.won = True
                    return
                self.curr_row += 1
                self.curr_column = 0


wordle_status = WordleStatus()


@app.get("/", response_class=HTMLResponse)
async def show_board(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "keys": qwerty_keyboard_keys}
    )


@app.get("/add_letter/{letter}", response_class=HTMLResponse)
async def add_letter(request: Request, letter: str):
    wordle_status.add_letter(letter)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "keys": qwerty_keyboard_keys}
    )


@app.get("/check_word", response_class=HTMLResponse)
async def check_word(request: Request):
    wordle_status.check_last_word()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "keys": qwerty_keyboard_keys}
    )


@app.get("/remove_letter", response_class=HTMLResponse)
async def remove_letter(request: Request):
    wordle_status.remove_last_letter()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"status": wordle_status, "keys": qwerty_keyboard_keys}
    )
