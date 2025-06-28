from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class File_Metadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    s3_key = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
