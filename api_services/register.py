from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from auth import hash_password
from database import get_db
from schemas import UserCreate

router = APIRouter()

@router.post("/register")
def register(user:UserCreate, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username exists")
    
    hashed = hash_password(user.password)
    
    new_user = User(
        username=user.username, 
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()

    return {"msg": "User created"}