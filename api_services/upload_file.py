from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from models import File_Metadata, User
from auth import get_current_user
from database import get_db
from utils.s3 import s3, S3_BUCKET_NAME

router = APIRouter()

@router.post("/upload")
def upload_file(
    file: UploadFile = File(...), 
    folder: Optional[str] = Form(""), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    timestamp = datetime.utcnow().isoformat()
    safe_filename = file.filename.replace(" ", "-")

    if folder:
        s3_key = f"{folder.strip('/')}/{timestamp}_{safe_filename}"
    else:
        s3_key = f"{timestamp}_{safe_filename}"
    
    s3.upload_fileobj(file.file, S3_BUCKET_NAME, s3_key)

    new_file = File_Metadata(
        filename = file.filename,
        owner_id = current_user.id,
        s3_key = s3_key
    )
    db.add(new_file)
    db.commit()
    return {"msg": "File uploaded", "s3_key":s3_key}