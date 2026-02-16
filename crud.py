from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import models, schemas
import string
import random

def get_url(db: Session, code: str):
    return db.query(models.ShortUrl).filter(models.ShortUrl.code == code).first()

def get_urls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ShortUrl).offset(skip).limit(limit).all()

def create_short_url(db: Session, url: schemas.ShortUrlCreate):
    # Generate a random code
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(6))
    
    # Check for collision (simple implementation, ideally loop until unique)
    while get_url(db, code):
        code = ''.join(random.choice(chars) for _ in range(6))

    db_url = models.ShortUrl(original_url=str(url.original_url), code=code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def get_url_by_code(db: Session, code: str):
    return db.query(models.ShortUrl).filter(models.ShortUrl.code == code).first()

def update_url(db: Session, db_url: models.ShortUrl, url_update: schemas.ShortUrlUpdate):
    if url_update.original_url:
        db_url.original_url = str(url_update.original_url)
    if url_update.custom_alias:
        # Check if alias exists and it's not the same as current code
        existing_url = get_url_by_code(db, url_update.custom_alias)
        if existing_url and existing_url.id != db_url.id:
            raise ValueError("Alias already exists")
        db_url.code = url_update.custom_alias
    
    db.commit()
    db.refresh(db_url)
    return db_url

def delete_url(db: Session, db_url: models.ShortUrl):
    db.delete(db_url)
    db.commit()

def increment_access_count(db: Session, db_url: models.ShortUrl):
    db_url.access_count += 1
    db_url.last_accessed_at = func.now()
    db.commit()
    db.refresh(db_url)

