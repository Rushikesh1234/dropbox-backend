from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import File_Metadata, User
from auth import get_current_user
from database import get_db

router = APIRouter()

@router.get("/files")
def get_user_files(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    files = db.query(File_Metadata).filter(File_Metadata.owner_id == current_user.id).all()
    return [
        {
            "filename": f.filename,
            "s3_key": f.s3_key,
            "uploaded_at": f.uploaded_at.isoformat()
        }
        for f in files
    ]
