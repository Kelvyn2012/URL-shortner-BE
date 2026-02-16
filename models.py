from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid

class ShortUrl(Base):
    __tablename__ = "short_urls"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, index=True)
    original_url = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
