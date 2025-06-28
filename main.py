from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base, get_db
from models import User, File_Metadata
from auth import hash_password, verify_password, create_access_token, get_current_user

from pydantic import BaseModel

import boto3
from datetime import datetime

from dotenv import load_dotenv
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()

class UserCreate(BaseModel):
    username: str
    password:str

@app.post("/register")
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

@app.post("/login")
def login(user:UserCreate, db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token}

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    key = f"{datetime.utcnow().isoformat()}_{file.filename}"
    s3.upload_fileobj(file.file, S3_BUCKET_NAME, key)

    new_file = File_Metadata(
        filename = file.filename,
        owner_id = current_user.id,
        s3_key = key
    )
    db.add(new_file)
    db.commit()

    return {"msg": "File uploaded", "s3_key":key}

@app.get("/download")
def download_file(key: str, current_user: User = Depends(get_current_user)):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
        ExpiresIn=3600
    )
    return {"url": url}

@app.get("/files")
def get_user_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = db.query(File_Metadata).filter(File_Metadata.owner_id == current_user.id).all()
    return [
        {
            "filename": f.filename,
            "s3_key": f.s3_key,
            "uploaded_at": f.uploaded_at.isoformat()
        }
        for f in files
    ]

