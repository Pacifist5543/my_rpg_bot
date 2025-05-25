# models.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///game.db')

# ... ваши модели (User, Boost и др.) ...

# main.py (при запуске бота)
from models import Base, engine

def init_db():
    Base.metadata.create_all(engine)  # <- Вот эта строка
    print("Таблицы созданы")

if __name__ == "__main__":
    init_db()