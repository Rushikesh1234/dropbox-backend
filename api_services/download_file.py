from fastapi import APIRouter, Depends, HTTPException
from models import User
from auth import get_current_user
from utils.s3 import s3, S3_BUCKET_NAME
import os

router = APIRouter()
API_URL = os.getenv("API_URL")

@router.get("/download")
def download_file(
    key: str, 
    current_user = Depends(get_current_user),
):
    try:
        head = s3.head_object(Bucket = S3_BUCKET_NAME, Key = key)
        size = head["ContentLength"]
        ONE_GB = 1 * 1024 * 1024 * 1024

        if ONE_GB > size:
            url = s3.generate_presigned_url(
                ClientMethod= 'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
                ExpiresIn=3600
            )
            return {"url": url}
        else:
            stream_url = f"{API_URL}/download/stream?key={key}"
            return {"url": stream_url, "stream": True}
    
    except s3.exceptions.ClientError as e:
        raise HTTPException(status_code=404, detail="File not found or access denied - {e}")