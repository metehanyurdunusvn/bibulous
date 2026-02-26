from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter()

@router.post("/posts", response_model=schemas.ForumPostResponse)
def create_post(user_id: int, post_data: schemas.ForumPostCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_post = models.ForumPost(
        user_id=user_id,
        title=post_data.title,
        content=post_data.content
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return schemas.ForumPostResponse(
        id=db_post.id,
        user_id=db_post.user_id,
        user_name=user.name,
        title=db_post.title,
        content=db_post.content,
        created_at=db_post.created_at,
        replies=[]
    )

@router.get("/posts", response_model=List[schemas.ForumPostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.ForumPost).order_by(models.ForumPost.created_at.desc()).all()
    results = []
    
    for p in posts:
        user = db.query(models.User).filter(models.User.id == p.user_id).first()
        replies = db.query(models.ForumReply).filter(models.ForumReply.post_id == p.id).all()
        
        reply_list = []
        for r in replies:
            r_user = db.query(models.User).filter(models.User.id == r.user_id).first()
            reply_list.append(schemas.ForumReplyResponse(
                id=r.id,
                post_id=r.post_id,
                user_id=r.user_id,
                user_name=r_user.name if r_user else "Unknown",
                content=r.content,
                created_at=r.created_at
            ))
            
        results.append(schemas.ForumPostResponse(
            id=p.id,
            user_id=p.user_id,
            user_name=user.name if user else "Unknown",
            title=p.title,
            content=p.content,
            created_at=p.created_at,
            replies=reply_list
        ))
        
    return results

@router.post("/posts/{post_id}/comments", response_model=schemas.ForumReplyResponse)
def create_reply(post_id: int, user_id: int, reply_data: schemas.ForumReplyCreate, db: Session = Depends(get_db)):
    post = db.query(models.ForumPost).filter(models.ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_reply = models.ForumReply(
        post_id=post_id,
        user_id=user_id,
        content=reply_data.content
    )
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    
    return schemas.ForumReplyResponse(
        id=db_reply.id,
        post_id=db_reply.post_id,
        user_id=db_reply.user_id,
        user_name=user.name,
        content=db_reply.content,
        created_at=db_reply.created_at
    )
