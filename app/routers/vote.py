from app import ormmodels, schemas
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db

from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(current_vote: schemas.Vote,
         db: Session = Depends(get_db),
         current_user: int = Depends(get_current_user)):

    found_post = db.query(ormmodels.Post).filter(ormmodels.Post.id == current_vote.post_id).first()
    if found_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {current_vote.post_id} does not exist")

    vote_query = db.query(ormmodels.Vote).filter(ormmodels.Vote.post_id == current_vote.post_id,
                                                 ormmodels.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if current_vote.direction == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already voted on post {current_vote.post_id}")

        new_vote = ormmodels.Vote(post_id=current_vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added the vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Vote does not exist")

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "Successfully deleted the existing vote"}