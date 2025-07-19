from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user
from database import get_db
from models import File_Metadata, User
from utils.s3 import s3, S3_BUCKET_NAME

router = APIRouter()

class PartETag(BaseModel):
    part_number: int
    etag: str

class CompleteUploadRequest(BaseModel):
    upload_id: str
    s3_key: str
    parts: List[PartETag]
    filename: str
    folder: Optional[str] = ""

@router.post("/upload/complete")
def complete_upload(
    payload: CompleteUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parts = [
        {"PartNumber": part.part_number, "ETag": part.etag}
        for part in sorted(payload.parts, key=lambda p: p.part_number)
    ]

    try:
        s3.complete_multipart_upload(
            Bucket = S3_BUCKET_NAME,
            Key = payload.s3_key,
            UploadId = payload.upload_id,
            MultiPartUpload = {"Parts": parts}
        )

        new_file = File_Metadata(
            filename = payload.filename,
            owner_id = current_user.id,
            s3_key = payload.s3_key
        )
        db.add(new_file)
        db.commit()
        return {"msg": "File uploaded", "s3_key":payload.s3_key}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))