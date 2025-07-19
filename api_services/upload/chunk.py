from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from utils.s3 import s3, S3_BUCKET_NAME

router = APIRouter()

@router.post("/upload/chunks")
def upload_chunks(
    upload_id: str = Form(...),
    s3_key: str = Form(...),
    part_number: int = Form(...),
    chunk: UploadFile = File(...)
):
    try:
        response = s3.upload_part(
            Bucket = S3_BUCKET_NAME,
            Key = s3_key,
            PartNumber = part_number,
            Upload_Id = upload_id,
            Body = chunk.file
        )

        return {
            "part_number": part_number,
            "etag": response["ETag"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

