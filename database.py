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
    
    user_id = Column(Integer, primary_key= True)
    username = Column(String)
    race = Column(String)
    user_lvl = Column(Integer)
    nickname = Column(String)
    location = Column(String)
    gold = Column(Integer)


engine = create_engine('sqlite:///rpg_bot.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def create_all_table():
    pass

