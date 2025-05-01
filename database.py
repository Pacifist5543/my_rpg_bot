# from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
# from sqlalchemy import create_engine

# BaseModel: DeclarativeBase = declarative_base()

# engine = create_engine(
#     "sqlite:///data.sqlite", connect_args={"check_same_thread": False, "timeout": 30}
# )
# create_session = sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)


# def create_all_table():
#     BaseModel.metadata.create_all(bind=engine)


from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key= True)
    name = Column(String)
    tg_id = Column(Integer)

# Для SQLite (файл будет создан в текущей директории)
engine = create_engine('sqlite:///rpg_bot.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

