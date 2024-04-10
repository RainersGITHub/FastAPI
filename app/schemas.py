from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional


# pydantic Model to describe the structure of the Post-Object which comes from the API-Call
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    owner_id: int
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    # This ist neccessary to convert a pydantic model to the ORM model
    class Config:
        orm_mode = True


# pydantic Model to describe the structure of the Post-Response
class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    # This ist neccessary to convert a pydantic model to the ORM model
    class Config:
        orm_mode = True


class PostJoin(BaseModel):
    Post: Post
    votes: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(UserCreate):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    direction: conint(le=1)
