from fastapi import APIRouter, Depends
from models import User
from auth import get_current_user
from utils.s3 import s3, S3_BUCKET_NAME

router = APIRouter()

@router.get("/download")
def download_file(
    key: str, current_user: 
    User = Depends(get_current_user)
):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
        ExpiresIn=3600
    )
    return {"url": url}