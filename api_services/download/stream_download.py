import botocore.exceptions
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from utils.s3 import s3, S3_BUCKET_NAME
import botocore

router = APIRouter()

@router.get("/download/stream")
def stream_download_large_files(
    key: str,
    current_user = Depends(get_current_user)
):
    try:
        s3_object = s3.get_object(Bucket = S3_BUCKET_NAME, Key = key)
        body = s3_object['Body']

        return StreamingResponse(
            body,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={key.split('/')[-1]}"
            }
        )
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail="Failed to stream file.")