from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from auth import verify_password, create_access_token
from database import get_db
from schemas import UserCreate

router = APIRouter()

@router.post("/login")
def login(
    user:UserCreate, 
    db:Session=Depends(get_db)
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token}