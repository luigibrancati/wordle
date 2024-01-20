import random
from enum import Enum
import os


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
        self.finished = False

    def add_letter(self, letter: str) -> None:
        if self.curr_column < 5 and not self.finished:
            self.words[self.curr_row][self.curr_column] = letter
            self.letter_status[self.curr_row][self.curr_column] = LetterResult.TBD
            self.curr_column += 1

    def remove_last_letter(self) -> None:
        if self.words[self.curr_row][0] is not None and not self.finished:
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
        if self.curr_column == self.num_columns and not self.finished:
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
                    self.finished = True
                    self.won = True
                    return
                self.curr_row += 1
                self.curr_column = 0
            if self.curr_row == self.num_rows:
                self.finished = True
    
    def reset(self):
        self.solution = self.word_list[random.randint(0, len(self.word_list) - 1)]
        self.curr_row = 0
        self.curr_column = 0
        self.words = {i:[None]*self.num_columns for i in range(self.num_rows)}
        self.letter_status = {i:[LetterResult.EMPTY]*self.num_columns for i in range(self.num_rows)}
        self.abset_letters = set()
        self.present_letters = set()
        self.correct_letters = set()
        self.won = False
        self.finished = False
