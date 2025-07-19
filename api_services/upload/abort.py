from fastapi import APIRouter, HTTPException, Form
from utils.s3 import s3, S3_BUCKET_NAME

router = APIRouter()

@router.post("/upload/abort")
def abort_uploaded(
    upload_id: str = Form(...),
    s3_key: str = Form(...)
):
    try:
        s3.abort_multipart_upload(
            Bucket = S3_BUCKET_NAME,
            Key = s3_key,
            UploadId = upload_id
        )
        return {"msg": "Upload aborted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))