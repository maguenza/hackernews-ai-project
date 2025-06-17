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
    title = Column(String(512), nullable=False)
    url = Column(String(1024))
    text = Column(Text)
    score = Column(Integer, default=0)
    author_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_dead = Column(Boolean, default=False)
    descendants = Column(Integer, default=0)  # Number of comments

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
    text = Column(Text, nullable=False)
    author_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'))
    created_at = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_dead = Column(Boolean, default=False)

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
        return f"<Comment(id={self.id}, author_id={self.author_id})>"

class Job(Base):
    """HackerNews job posting model."""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    url = Column(String(1024))
    text = Column(Text)
    score = Column(Integer, default=0)
    author_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_dead = Column(Boolean, default=False)
    job_type = Column(String(50))  # e.g., 'full-time', 'contract', 'remote'
    location = Column(String(255))
    company = Column(String(255))
    salary_range = Column(String(255))

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