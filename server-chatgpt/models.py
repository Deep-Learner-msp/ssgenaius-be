from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    response = Column(Text, nullable=False)
    feedback = Column(String(255), nullable=False)
    user_query = Column(Text, nullable=False)
