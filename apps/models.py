from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class PostRecord(Base):
    __tablename__ = "post_records"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    # Storing platforms as a comma-separated string for simplicity in SQLite
    platforms = Column(String, nullable=False) 
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_time = Column(DateTime(timezone=True), nullable=True)

class PostResultRecord(Base):
    __tablename__ = "post_results"
    
    id = Column(Integer, primary_key=True, index=True)
    post_record_id = Column(Integer, index=True)
    platform = Column(String, nullable=False)
    success = Column(Boolean, default=False)
    platform_post_id = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
