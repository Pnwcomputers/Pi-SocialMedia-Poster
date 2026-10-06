import asyncio
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import PostRecord, PostResultRecord
from .dispatcher import PostDispatcher
from .schemas import PostCreate

dispatcher = PostDispatcher()

async def process_post(post_id: int):
    """Processes a single post record from the database."""
    db: Session = SessionLocal()
    try:
        post = db.query(PostRecord).filter(PostRecord.id == post_id).first()
        if not post or post.status != "pending":
            return

        # Prepare payload
        platforms = post.platforms.split(",")
        post_data = PostCreate(
            content=post.content,
            platforms=platforms
        )

        # Send to platforms
        results = await dispatcher.dispatch(post_data)

        # Log results
        all_success = True
        for res in results:
            if not res.success:
                all_success = False

            result_record = PostResultRecord(
                post_record_id=post.id,
                platform=res.platform,
                success=res.success,
                platform_post_id=res.post_id,
                error_message=res.error_message
            )
            db.add(result_record)

        post.status = "completed" if all_success else "failed"
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
