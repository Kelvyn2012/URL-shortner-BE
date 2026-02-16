from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class ShortUrlBase(BaseModel):
    original_url: HttpUrl

class ShortUrlCreate(ShortUrlBase):
    pass

class ShortUrlUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    custom_alias: Optional[str] = None

class ShortUrl(ShortUrlBase):
    id: str
    code: str
    short_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    access_count: int
    last_accessed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
