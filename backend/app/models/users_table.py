from sqlalchemy import String,Column 
from ..db import Base 

class Users(Base):
    __tablename__ = "users"

    username=Column(String,primary_key=True)
    hashed_password=Column(String)
    email=Column(String)
    full_name=Column(String)




