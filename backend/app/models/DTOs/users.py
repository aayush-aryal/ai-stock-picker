from pydantic import BaseModel


class UserDTO(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

    class Config:
        orm_mode=True


class RegisterUser(BaseModel):
    username:str 
    email: str | None = None
    full_name: str | None = None
    password:str


class Token(BaseModel):
    access_token:str 
    token_type:str 

class TokenData(BaseModel):
    username:str| None= None 