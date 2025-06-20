"""
SQLAlchemy models for HackerNews data.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    """HackerNews user model."""
    __tablename__ = 'users'

    id = Column(String(255), primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    karma = Column(Integer, default=0)
    about = Column(Text)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    stories = relationship("Story", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    jobs = relationship("Job", back_populates="author")

    def __repr__(self):
        return f"<User(username='{self.username}', karma={self.karma})>"

class Story(Base):
    """HackerNews story model."""
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    url = Column(Text)
    score = Column(Integer)
    time = Column(DateTime)  # From ETL pipeline
    by = Column(String(255), ForeignKey('users.id'), nullable=True)  # From ETL pipeline
    descendants = Column(Integer)
    kids = Column(String)  # Array stored as string
    text = Column(Text)
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="stories")
    comments = relationship("Comment", back_populates="story")

    # Indexes
    __table_args__ = (
        Index('idx_stories_created_at', 'created_at'),
        Index('idx_stories_score', 'score'),
    )

    def __repr__(self):
        return f"<Story(title='{self.title}', score={self.score})>"

class Comment(Base):
    """HackerNews comment model."""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('comments.id'))
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    by = Column(String(255), ForeignKey('users.id'), nullable=True)  # From ETL pipeline
    text = Column(Text)
    time = Column(DateTime)  # From ETL pipeline
    kids = Column(String)  # Array stored as string
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="comments")
    story = relationship("Story", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    # Indexes
    __table_args__ = (
        Index('idx_comments_story_id', 'story_id'),
        Index('idx_comments_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, by={self.by})>"

class Job(Base):
    """HackerNews job posting model."""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    url = Column(Text)
    text = Column(Text)
    score = Column(Integer)
    time = Column(DateTime)  # From ETL pipeline
    by = Column(String(255), ForeignKey('users.id'), nullable=True)  # From ETL pipeline
    job_type = Column(String(50))
    location = Column(String(255))
    company = Column(String(255))
    salary_range = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="jobs")

    # Indexes
    __table_args__ = (
        Index('idx_jobs_created_at', 'created_at'),
        Index('idx_jobs_score', 'score'),
        Index('idx_jobs_job_type', 'job_type'),
        Index('idx_jobs_location', 'location'),
    )

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>" 