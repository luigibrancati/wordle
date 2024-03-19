from pydantic import BaseModel


class GameBase(BaseModel):
    won: bool
    steps: int
    points: float
    solution: str
    user_id: int


class Game(GameBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    points: float
    games: list[Game] = []

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str

    def header(self):
        if self.token_type == 'bearer':
            return {"Authorization": f"Bearer {self.access_token}"}
