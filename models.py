from database import BaseModel
from sqlalchemy import Column, Integer, String

class User(BaseModel):
    __tablename__ = "users" 

    id = Column(Integer, primary_key= True)
    name = Column(String)
    tg_id = Column(Integer)
