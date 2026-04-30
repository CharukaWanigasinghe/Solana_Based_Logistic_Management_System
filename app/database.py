# Database configuration and connection management for INTELLICA Logistics System
# Supports both SQLite (development) and PostgreSQL (production/cloud)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from .config import Config

# Database URL from environment or config
DATABASE_URL = Config.DATABASE_URL

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        echo=Config.DEBUG,
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=Config.DEBUG,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency function to get database session.
    Use with FastAPI's dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables.
    Call this during application startup.
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all database tables.
    Use with caution - this deletes all data!
    """
    Base.metadata.drop_all(bind=engine)

# Example usage in FastAPI routes:
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
"""