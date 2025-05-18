from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Boost(Base):
    __tablename__ = "boosts"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    damage = Column(
        Integer, default=0
    )  # значения от 0 до 1 (0.2 это +20%, 0.5 это +50%, -0.4 это -40%...)
    defense = Column(
        Integer, default=0
    )  # значения от 0 до 1 (0.2 это +20%, 0.5 это +50%, -0.4 это -40%...)
    accuracy = Column()

    user_id = Column(ForeignKey("users.user_id"))
    user = relationship("User", back_populates="boosts")
