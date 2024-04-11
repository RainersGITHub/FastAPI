from app import ormmodels, schemas, utils
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db),
                  current_user: int = Depends(get_current_user)):
    users = db.query(ormmodels.User).all()
    return users


@router.get("/latest", response_model=schemas.UserOut)
def get_latest_user(db: Session = Depends(get_db),
                    current_user: int = Depends(get_current_user)):
    user = db.query(ormmodels.User).order_by(ormmodels.User.id.desc()).first()

    return user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user_by_id(id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(get_current_user)):
    user = db.query(ormmodels.User).filter(ormmodels.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID {id} was not found")

    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(get_db)):
    #                current_user: int = Depends(get_current_user)):
    # hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = ormmodels.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int,
                db: Session = Depends(get_db),
                current_user: int = Depends(get_current_user)):
    user = db.query(ormmodels.User).filter(ormmodels.User.id == id)

    if user.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID {id} was not found")

    user.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id: int,
                user: schemas.UserUpdate,
                db: Session = Depends(get_db),
                current_user: int = Depends(get_current_user)):
    user_query = db.query(ormmodels.User).filter(ormmodels.User.id == id)
    updated_user = user_query.first()

    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with ID {id} was not found")

    user_query.update(user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()
