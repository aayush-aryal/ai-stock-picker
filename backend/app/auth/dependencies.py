from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from ..models.DTOs.users import UserDTO, TokenData, RegisterUser
from pwdlib import PasswordHash
import jwt 
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.users_table import Users
from ..core.config import settings


SECRET_KEY=settings.SECRET_KEY
ALGORITHM=settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES


password_hash=PasswordHash.recommended()

def verify_password(plain_password,hashed_password):
    return password_hash.verify(plain_password,hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def authenticate_user(username:str,password:str,db:Session):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    user_dto = UserDTO(
        username=user.username, # type: ignore
        email=user.email, # type: ignore
        full_name=user.full_name # type: ignore
    )
    return user_dto

def create_access_token(data:dict,experies_delta:timedelta|None=None):
    to_encode=data.copy()
    if experies_delta:
        expire=datetime.now(timezone.utc)+experies_delta
    else:
        expire=datetime.now(timezone.utc)+ timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data=TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user=db.query(Users).filter(Users.username==username).first()
    if user is None:
        raise credentials_exception
    return UserDTO(
        username=user.username, # type: ignore
        email=user.email, # type: ignore
        full_name=user.full_name, # type: ignore
        total_capital=user.total_capital  # type: ignore
    )


async def register_user(register_user:RegisterUser, db:Session):
    #check if username present 
    user=db.query(Users).filter(Users.username==register_user.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    hashed_password=get_password_hash(register_user.password)
    new_user=Users(
        username=register_user.username ,
        hashed_password=hashed_password,
        email=register_user.email ,
        full_name=register_user.full_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_dto=UserDTO(
        username=new_user.username, # type: ignore
        email=new_user.email, # type: ignore
        full_name=new_user.full_name # type: ignore
    )
    return user_dto