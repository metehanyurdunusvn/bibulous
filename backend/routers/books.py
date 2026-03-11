from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import models, schemas
from database import get_db
from oneri import recommender

router = APIRouter()

@router.get("/top", response_model=List[schemas.BookResponse])
def get_top_books(skip: int = 0, limit: int = 50):
    """Returns top books by popularity/rating for the user to select"""
    return recommender.get_top_books(skip=skip, limit=limit)

@router.get("/random", response_model=List[schemas.BookResponse])
def get_random_books(n: int = 50):
    """Returns random books for the user to select their initial favorites"""
    return recommender.get_random_books(n=n)

@router.get("/search", response_model=List[schemas.BookResponse])
def search_books(q: str, n: int = 10):
    """Search books by title or author"""
    return recommender.search_books(q, n=n)

@router.get("/recommend/{user_id}")
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Get recommendations for a user based on their liked books and CF model"""
    print(f"--- Incoming request for user {user_id} ---")
    # Fetch liked books from DB
    liked_books = db.query(models.UserLikedBook).filter(models.UserLikedBook.user_id == user_id).all()
    liked_isbns = [lb.isbn for lb in liked_books]
    
    # 1. Independent (CF) recommendations
    try:
        cf_recs = recommender.get_recommendations_cf(
            user_id=user_id, # Can use their ID if they have rated before, otherwise acts as cold start
            n=10,
            liked_isbns=liked_isbns
        )
    except Exception as e:
        cf_recs = []
        print(f"CF Error: {e}")

    # 2. Same Author recommendations
    author_recs = recommender.get_recommendations_same_author(liked_isbns, n=10)
    
    # 3. Same Series (Similar Title) recommendations
    series_recs = recommender.get_recommendations_similar_title(liked_isbns, n=10)
    
    return {
        "independent": cf_recs,
        "same_author": author_recs,
        "same_series": series_recs
    }

@router.post("/{isbn}/comments", response_model=schemas.BookCommentResponse)
def add_comment(isbn: str, user_id: int, comment_data: schemas.BookCommentCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_comment = models.BookComment(
        user_id=user_id,
        isbn=isbn,
        comment=comment_data.comment,
        rating=comment_data.rating
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Return matched to schema
    return schemas.BookCommentResponse(
        id=db_comment.id,
        user_id=db_comment.user_id,
        user_name=user.name,
        isbn=db_comment.isbn,
        comment=db_comment.comment,
        rating=db_comment.rating,
        created_at=db_comment.created_at
    )

@router.get("/{isbn}/comments", response_model=List[schemas.BookCommentResponse])
def get_comments(isbn: str, db: Session = Depends(get_db)):
    comments = db.query(models.BookComment).filter(models.BookComment.isbn == isbn).all()
    results = []
    for c in comments:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        results.append(schemas.BookCommentResponse(
            id=c.id,
            user_id=c.user_id,
            user_name=user.name if user else "Unknown",
            isbn=c.isbn,
            comment=c.comment,
            rating=c.rating,
            created_at=c.created_at
        ))
    return results

@router.get("/{isbn}/similar", response_model=List[schemas.BookResponse])
def get_similar_books(isbn: str):
    """Get recommendations based on CF, excluding the book's own author"""
    info = recommender.books_dict.get(isbn)
    exclude_authors = set()
    if info and info.get('authors') and str(info['authors']) != 'nan':
        exclude_authors.add(str(info['authors']).lower().strip())

    # 1. Get similar titles explicitly excluding the author
    title_recs = recommender.get_recommendations_similar_title([isbn], n=10, exclude_authors=exclude_authors)

    # 2. Get CF/popularity fallbacks
    try:
        cf_recs = recommender.get_recommendations_cf(
            user_id=None,
            n=10,
            liked_isbns=[isbn]
        )
    except Exception as e:
        cf_recs = []
        print(f"CF Similar Error: {e}")

    # Deduplicate — hard filter: never show same author regardless of source
    seen_isbns = {isbn}
    combined = []

    for rec in title_recs + cf_recs:
        rec_isbn = rec["ISBN"]
        rec_author = str(rec.get("authors", "")).lower().strip()
        if rec_isbn not in seen_isbns and rec_author not in exclude_authors:
            combined.append(rec)
            seen_isbns.add(rec_isbn)
        if len(combined) >= 10:
            break

    return combined

@router.get("/metrics/{user_id}")
def get_recommendation_metrics(user_id: int, db: Session = Depends(get_db)):
    """Get recommendations for a user along with their exact SVD/CF, POP, TAG scores"""
    liked_books = db.query(models.UserLikedBook).filter(models.UserLikedBook.user_id == user_id).all()
    liked_isbns = [lb.isbn for lb in liked_books]
    
    try:
        metrics_recs = recommender.get_recommendations_with_metrics(
            user_id=user_id,
            liked_isbns=liked_isbns,
            n=50
        )
    except Exception as e:
        metrics_recs = []
        print(f"Metrics Error: {e}")
        
    return metrics_recs

@router.get("/detail/{isbn}", response_model=schemas.BookResponse)
def get_book(isbn: str):
    info = recommender.books_dict.get(isbn)
    if not info:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "ISBN": isbn,
        "title": info['title'],
        "authors": info['authors'],
        "image_url": info['image_url']
    }
