import os
import random


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Words(metaclass=SingletonMeta):
    def __init__(self):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/words.txt")
        self.word_list = [w[:-1] for w in open(filepath, "r").readlines()]

    def is_in_wordlist(self, word: str) -> bool:
        return word in self.word_list
    
    def random_world(self) -> str:
        return self.word_list[random.randint(0, len(self.word_list) - 1)]


words = Words()
