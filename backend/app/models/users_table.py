from sqlalchemy import String,Column ,Float, Integer,Date, Numeric
from sqlalchemy import ForeignKey
from ..db import Base 
from sqlalchemy.orm import relationship
from typing import Optional
from enum import Enum
from sqlalchemy import Enum as DbEnum

class Users(Base):
    __tablename__ = "users"

    username=Column(String,primary_key=True)
    hashed_password=Column(String)
    email=Column(String)
    full_name=Column(String)
    total_capital=Column(Numeric(10,2),default=10000)
    holdings=relationship("UserStocks",back_populates="user")



class UserStocks(Base):

    __tablename__="user_stocks"
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String,ForeignKey("users.username"))
    date=Column(Date)
    stock=Column(String)
    shares=Column(Numeric(10,2))
    avg_buy_price:Optional[float]=Column(Numeric(10,2)) # type: ignore

    user=relationship("Users", back_populates="holdings")



class Activity(Enum):
    buy="buy"
    sell="sell"



class Transanctions(Base):
    __tablename__="user_transanctions"
    id=Column(Integer,primary_key=True, index=True)
    username=Column(String, ForeignKey("users.username"))
    date=Column(Date)
    stock=Column(String)
    shares=Column(Numeric(10,2))
    activity = Column(DbEnum(Activity), nullable=False)





