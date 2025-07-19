from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from models import User
from auth import get_current_user
from database import get_db
from utils.s3 import s3, S3_BUCKET_NAME

router = APIRouter()

@router.post("/upload/initiate")
def initiate_upload(
        filename: str = Form(...),
        folder: Optional[str] = Form(""),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    timestemp = datetime.utcnow().isoformat()
    safe_filename = filename.replace(" ", "-")

    if folder:
        s3_key = f"{folder.strip('/')}/{timestemp}_{safe_filename}"
    else:
        s3_key = f"{timestemp}_{safe_filename}"

    response = s3.create_multipart_upload(
        Bucket = S3_BUCKET_NAME,
        Key = s3_key
    )

    upload_id = response["uploadId"]

    return {
        "upload_id" : upload_id,
        "s3_key" : s3_key,
        "msg" : "Multipart uploaded started"
    }