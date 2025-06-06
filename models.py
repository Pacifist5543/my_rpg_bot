from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase

Base: DeclarativeBase = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key= True)
    username = Column(String)
    race = Column(String)
    user_lvl = Column(Integer)
    nickname = Column(String)
    location = Column(String)
    gold = Column(Integer)

    boosts = relationship("Boost", back_populates="user")


engine = create_engine('sqlite:///rpg_bot.db')

Session = sessionmaker(bind=engine)

def create_all_table():
    from boost import Boost

    Base.metadata.create_all(engine)

