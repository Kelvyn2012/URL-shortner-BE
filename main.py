from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

# Add allowed origins from environment variable (comma separated)
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    if env_origins == "*":
        origins = ["*"]
    else:
        # Split by comma, strip whitespace, and remove empty strings to be robust against formatting
        additional_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
        origins.extend(additional_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_short_url_str(request: Request, code: str):
    # Use request.base_url which includes scheme, host, and port
    return str(request.base_url).rstrip('/') + "/" + code

def map_url_response(db_url, request: Request):
    return schemas.ShortUrl(
        id=db_url.id,
        code=db_url.code,
        original_url=db_url.original_url,
        short_url=get_short_url_str(request, db_url.code),
        created_at=db_url.created_at,
        updated_at=db_url.updated_at,
        access_count=db_url.access_count,
        last_accessed_at=db_url.last_accessed_at
    )

@app.post("/api/urls", response_model=schemas.ShortUrl)
def create_url(url: schemas.ShortUrlCreate, request: Request, db: Session = Depends(get_db)):
    db_url = crud.create_short_url(db=db, url=url)
    return map_url_response(db_url, request)

@app.get("/api/urls", response_model=list[schemas.ShortUrl])
def read_urls(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    urls = crud.get_urls(db, skip=skip, limit=limit)
    return [map_url_response(url, request) for url in urls]

@app.get("/api/urls/{code}", response_model=schemas.ShortUrl)
def read_url(code: str, request: Request, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_code(db, code=code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return map_url_response(db_url, request)

@app.put("/api/urls/{code}", response_model=schemas.ShortUrl)
def update_url(code: str, url: schemas.ShortUrlUpdate, request: Request, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_code(db, code=code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    try:
        updated_url = crud.update_url(db=db, db_url=db_url, url_update=url)
        return map_url_response(updated_url, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/urls/{code}")
def delete_url(code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_code(db, code=code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    crud.delete_url(db=db, db_url=db_url)
    return {"detail": "URL deleted"}

@app.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_code(db, code=code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    crud.increment_access_count(db, db_url)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=db_url.original_url)

@app.get("/api/urls/{code}/stats", response_model=schemas.ShortUrl)
def get_url_stats(code: str, request: Request, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_code(db, code=code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return map_url_response(db_url, request)

