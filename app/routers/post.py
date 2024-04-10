from sqlalchemy import func
from app import ormmodels, schemas
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List, Optional

from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostJoin])
def get_all_posts(db: Session = Depends(get_db),
                  current_user: int = Depends(get_current_user),
                  limit: int = 10,
                  skip: int = 0,
                  search: Optional[str] = ""):
    posts = db.query(ormmodels.Post, func.count(ormmodels.Vote.post_id).label("votes")).join(ormmodels.Vote,
                                                                                             ormmodels.Vote.post_id == ormmodels.Post.id,
                                                                                             isouter=True).group_by(
        ormmodels.Post.id).filter(ormmodels.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.get("/latest", response_model=schemas.PostJoin)
def get_latest_post(db: Session = Depends(get_db),
                    current_user: int = Depends(get_current_user)):
    post = db.query(ormmodels.Post, func.count(ormmodels.Vote.post_id).label("votes")).join(ormmodels.Vote,
                                                                                             ormmodels.Vote.post_id == ormmodels.Post.id,
                                                                                             isouter=True).group_by(
        ormmodels.Post.id).order_by(ormmodels.Post.id.desc()).first()

    return post


@router.get("/{id}", response_model=schemas.PostJoin)
def get_post_by_id(id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(get_current_user)):
    post = db.query(ormmodels.Post, func.count(ormmodels.Vote.post_id).label("votes")).join(ormmodels.Vote,
                                                                                             ormmodels.Vote.post_id == ormmodels.Post.id,
                                                                                             isouter=True).group_by(
        ormmodels.Post.id).filter(ormmodels.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with ID {id} was not found")

    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostCreate)
def create_posts(post: schemas.PostCreate,
                 db: Session = Depends(get_db),
                 current_user: int = Depends(get_current_user)):
    new_post = ormmodels.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
                db: Session = Depends(get_db),
                current_user: int = Depends(get_current_user)):
    post_query = db.query(ormmodels.Post).filter(ormmodels.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with ID {id} was not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform the requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostUpdate)
def update_post(id: int,
                post: schemas.PostBase,
                db: Session = Depends(get_db),
                current_user: int = Depends(get_current_user)):
    post_query = db.query(ormmodels.Post).filter(ormmodels.Post.id == id)
    updated_post = post_query.first()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with ID {id} was not found")

    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform the requested action")

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
