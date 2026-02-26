from pydantic import BaseModel
from typing import List
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    surname: str
    country: str
    language: str

class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    country: str
    language: str

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode

class BookResponse(BaseModel):
    ISBN: str
    title: str
    authors: str
    image_url: str

class LikedBookCreate(BaseModel):
    isbn: str

class BookCommentCreate(BaseModel):
    comment: str
    rating: float

class BookCommentResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    isbn: str
    comment: str
    rating: float
    created_at: datetime

    class Config:
        from_attributes = True

class ForumReplyCreate(BaseModel):
    content: str

class ForumReplyResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ForumPostCreate(BaseModel):
    title: str
    content: str

class ForumPostResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    title: str
    content: str
    created_at: datetime
    replies: List[ForumReplyResponse] = []

    class Config:
        from_attributes = True
