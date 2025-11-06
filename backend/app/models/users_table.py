from sqlalchemy import String,Column ,Float, Integer,Date
from sqlalchemy import ForeignKey
from ..db import Base 
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"

    username=Column(String,primary_key=True)
    hashed_password=Column(String)
    email=Column(String)
    full_name=Column(String)
    total_capital=Column(Float,default=10000)
    holdings=relationship("UserStocks",back_populates="user")




class UserStocks(Base):

    __tablename__="user_stocks"
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String,ForeignKey("users.username"))
    date=Column(Date)
    stock=Column(String)
    shares=Column(Float)

    user=relationship("Users", back_populates="holdings")

