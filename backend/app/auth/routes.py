from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from ..models.DTOs.users import UserDTO, Token,RegisterUser
from ..models.users_table import Users
from .dependencies import  get_current_user, authenticate_user,create_access_token,register_user
from fastapi import Depends, status
from datetime import timedelta
from sqlalchemy.orm import Session
from ..db import get_db

router=APIRouter(prefix='/auth',tags=['auth'])

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
   user=authenticate_user(form_data.username,form_data.password,db)
   if not user:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Incorrect username or password",
           headers={'WWW-Authenticate':"Bearer"}
       )
   access_token_expires= timedelta(minutes=30)
   access_token=create_access_token(
       data={"sub":user.username},experies_delta=access_token_expires # type: ignore
   )
   return Token(access_token=access_token, token_type="Bearer")

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
):
    return current_user


@router.post("/users/register")
async def register(user:RegisterUser, db:Session=Depends(get_db)):
    user_dto=await register_user(user, db)
    return user_dto
