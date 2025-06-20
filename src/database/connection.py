"""
Database connection management for HackerNews AI project.
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from src.database.models import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/hackernews_ai"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        raise Exception(f"Failed to initialize database: {str(e)}")

@contextmanager
def get_db_connection() -> Generator[Session, None, None]:
    """
    Get a database connection using a context manager.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        with get_db_connection() as db:
            db.query(User).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection.
    
    Yields:
        Session: SQLAlchemy database session
    """
    with get_db_connection() as session:
        yield session 