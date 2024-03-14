from database import Base
from sqlalchemy.orm import validates
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    games = relationship("Game", back_populates="owner")

    @validates('name')
    def _(name: str):
        if len(name) < 3:
            raise ValueError('name is too short')
        return name.lower()    


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    won = Column(Boolean, index=True)
    steps = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    player = relationship("User", back_populates="games")