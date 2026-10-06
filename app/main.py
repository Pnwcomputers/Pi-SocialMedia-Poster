from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime, timezone
from typing import List, Optional
import asyncio

# Import your new modules
from . import models, schemas, database, queue
from .scheduler import start_scheduler
from .database import engine, get_db

# Create the SQLite database tables automatically
models.Base.metadata.create_all(bind=engine)

# Manage startup events (like starting the scheduler)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background scheduler...")
    start_scheduler()
    yield
    print("Shutting down...")

app = FastAPI(
    title="Pi-SocialMedia-Poster",
    description="Self-hosted FastAPI social media cross-poster for Raspberry Pi",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates for the Dashboard
app.mount("/static", StaticFiles(directory="app/dashboard/static"), name="static")
templates = Jinja2Templates(directory="app/dashboard/templates")

# --- Web Dashboard Routes ---

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Renders the main post creation form."""
    return templates.TemplateResponse(
    request=request, 
    name="index.html", 
    context={"posts": []}
)

@app.get("/logs", response_class=HTMLResponse)
async def get_logs(request: Request, db: Session = Depends(get_db)):
    """Renders the history of posts from the database."""
    posts = db.query(models.PostRecord).order_by(models.PostRecord.created_at.desc()).all()
    return templates.TemplateResponse("logs.html", {"request": request, "posts": posts})

@app.post("/api/web/post")
async def create_web_post(
    content: str = Form(...),
    platforms: List[str] = Form(...),
    schedule_time: Optional[datetime] = Form(None),
    db: Session = Depends(get_db)
):
    """Handles the form submission from the web dashboard."""
    # Convert platform list to a comma-separated string for SQLite storage
    platforms_str = ",".join(platforms)
    
    # Save the post to the database as 'pending'
    new_post = models.PostRecord(
        content=content,
        platforms=platforms_str,
        status="pending",
        scheduled_time=schedule_time
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # If it is meant to post immediately, trigger the queue worker
    if not schedule_time or schedule_time <= datetime.now(timezone.utc):
        asyncio.create_task(queue.process_post(new_post.id))

    # Redirect the user to the logs page to see the status
    return RedirectResponse(url="/logs", status_code=303)


# --- REST API Routes (for external triggers) ---

@app.post("/api/post")
async def api_create_post(post_data: schemas.PostCreate, db: Session = Depends(get_db)):
    """API endpoint for programmatic posting (e.g., from Shortcuts or other apps)."""
    platforms_str = ",".join(post_data.platforms)
    
    new_post = models.PostRecord(
        content=post_data.content,
        platforms=platforms_str,
        status="pending",
        scheduled_time=post_data.schedule_time
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    if not post_data.schedule_time or post_data.schedule_time <= datetime.now(timezone.utc):
        asyncio.create_task(queue.process_post(new_post.id))

    return {"message": "Post queued successfully", "post_id": new_post.id}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
