from enum import Enum
from .words import words


class LetterResult(Enum):
    EMPTY = 'empty'
    TBD = 'tbd'
    ABSENT = 'absent'
    PRESENT = 'present'
    CORRECT = 'correct'


class GameStatus:
    num_columns = 5
    num_rows = 6

    def __init__(self):
        self.solution = words.random_world()
        self.curr_row = 0
        self.curr_column = 0
        self.grid_letters = {row: [None]*self.num_columns for row in range(self.num_rows)}
        self.grid_letters_status = {row: [LetterResult.EMPTY]*self.num_columns for row in range(self.num_rows)}
        self.abset_letters = set()
        self.present_letters = set()
        self.correct_letters = set()
        self.won = False
        self.finished = False

    @property
    def row_full(self):
        return self.curr_column >= self.num_columns

    @property
    def last_word(self) -> str:
        if not self.row_full:
            return ""
        if not self.finished:
            return "".join(self.grid_letters[self.curr_row])
        else:
            return "".join(self.grid_letters[self.num_rows - 1])

    def add_letter(self, letter:str) -> None:
        if not self.row_full and not self.finished:
            self.grid_letters[self.curr_row][self.curr_column] = letter
            self.grid_letters_status[self.curr_row][self.curr_column] = LetterResult.TBD
            self.curr_column += 1

    def remove_last_letter(self) -> None:
        if self.grid_letters[self.curr_row][0] is not None and not self.finished:
            self.curr_column -= 1
            self.grid_letters[self.curr_row][self.curr_column] = None
            self.grid_letters_status[self.curr_row][self.curr_column] = LetterResult.EMPTY

    def letter_state(self, letter:str) -> LetterResult:
        if letter in self.abset_letters:
            return LetterResult.ABSENT
        if letter in self.present_letters:
            return LetterResult.PRESENT
        if letter in self.correct_letters:
            return LetterResult.CORRECT
        return LetterResult.TBD

    def _update_word_status(self, word:str) -> None:
        for i, letter in enumerate(word):
            if letter in self.solution:
                if letter == self.solution[i]:
                    self.grid_letters_status[self.curr_row][i] = LetterResult.CORRECT
                    self.correct_letters.add(letter)
                    if letter in self.present_letters:
                        self.present_letters.remove(letter)
                else:
                    self.grid_letters_status[self.curr_row][i] = LetterResult.PRESENT
                    self.present_letters.add(letter)
            else:
                self.grid_letters_status[self.curr_row][i] = LetterResult.ABSENT
                self.abset_letters.add(letter)

    def last_word_is_in_wordlist(self) -> bool:
        word = self.last_word
        return words.is_in_wordlist(word)

    def check_last_word(self) -> bool:
        if self.row_full and not self.finished:
            word = self.last_word
            if words.is_in_wordlist(word):
                self._update_word_status(word)
                if word == self.solution:
                    print("Won")
                    self.finished = True
                    self.won = True
                    return
                if self.curr_row == self.num_rows - 1:
                    print("Lost")
                    self.finished = True
                    self.won = False
                    return
                self.curr_row += 1
                self.curr_column = 0

    def reset(self) -> None:
        self.solution = words.random_world()
        self.curr_row = 0
        self.curr_column = 0
        self.grid_letters = {i:[None]*self.num_columns for i in range(self.num_rows)}
        self.grid_letters_status = {i:[LetterResult.EMPTY]*self.num_columns for i in range(self.num_rows)}
        self.abset_letters = set()
        self.present_letters = set()
        self.correct_letters = set()
        self.won = False
        self.finished = False
