from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .database import SessionLocal
from .models import PostRecord
from .queue import process_post
import asyncio

scheduler = AsyncIOScheduler()

async def check_scheduled_posts():
    """Polls the database for scheduled posts that are due."""
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        pending_posts = db.query(PostRecord).filter(
            PostRecord.status == "pending",
            PostRecord.scheduled_time <= now
        ).all()

        for post in pending_posts:
            # Fire and forget the processing task
            asyncio.create_task(process_post(post.id))
    finally:
        db.close()

def start_scheduler():
    """Initializes the background polling."""
    scheduler.add_job(check_scheduled_posts, 'interval', minutes=1)
    scheduler.start()
