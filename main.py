
from fastapi import FastAPI
from database import Base, engine

from api_services import register, login, upload_file, download_file, show_all_files
from api_services.upload import abort, chunk, complete, initiate
from api_services.download import stream_download

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(register.router)
app.include_router(login.router)

app.include_router(upload_file.router)
app.include_router(initiate.router)
app.include_router(chunk.router)
app.include_router(complete.router)
app.include_router(abort.router)

app.include_router(download_file.router)
app.include_router(stream_download.router)

app.include_router(show_all_files.router)

