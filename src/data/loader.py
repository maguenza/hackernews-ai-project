"""
Data loading module for HackerNews AI project.
Handles loading data into PostgreSQL database.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Class to handle loading data into PostgreSQL database."""
    
    def __init__(self, database_url: str):
        """
        Initialize the data loader.
        
        Args:
            database_url (str): PostgreSQL database URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT,
                    score INTEGER,
                    time TIMESTAMP,
                    by TEXT,
                    descendants INTEGER,
                    kids INTEGER[],
                    text TEXT,
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY,
                    parent_id INTEGER,
                    story_id INTEGER,
                    by TEXT,
                    text TEXT,
                    time TIMESTAMP,
                    kids INTEGER[],
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES comments(id),
                    FOREIGN KEY (story_id) REFERENCES stories(id)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL,
                    karma INTEGER DEFAULT 0,
                    about TEXT,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT,
                    text TEXT,
                    score INTEGER,
                    time TIMESTAMP,
                    by TEXT,
                    job_type VARCHAR(50),
                    location VARCHAR(255),
                    company VARCHAR(255),
                    salary_range VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (by) REFERENCES users(id)
                )
            """))
            conn.commit()

    def load_story(self, story: Dict[str, Any]) -> None:
        """
        Load a story into the database.
        
        Args:
            story (Dict[str, Any]): Story data to load
        """
        with self.Session() as session:
            session.execute(
                text("""
                    INSERT INTO stories (id, title, url, score, time, by, descendants, kids, text, type)
                    VALUES (:id, :title, :url, :score, :time, :by, :descendants, :kids, :text, :type)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        url = EXCLUDED.url,
                        score = EXCLUDED.score,
                        time = EXCLUDED.time,
                        by = EXCLUDED.by,
                        descendants = EXCLUDED.descendants,
                        kids = EXCLUDED.kids,
                        text = EXCLUDED.text,
                        type = EXCLUDED.type
                """),
                {
                    'id': story['id'],
                    'title': story.get('title'),
                    'url': story.get('url'),
                    'score': story.get('score'),
                    'time': datetime.fromtimestamp(story.get('time', 0)),
                    'by': story.get('by'),
                    'descendants': story.get('descendants'),
                    'kids': story.get('kids', []),
                    'text': story.get('text'),
                    'type': story.get('type')
                }
            )
            session.commit()

    def load_comment(self, comment: Dict[str, Any], story_id: int, parent_id: Optional[int] = None) -> None:
        """
        Load a comment into the database.
        
        Args:
            comment (Dict[str, Any]): Comment data to load
            story_id (int): ID of the parent story
            parent_id (Optional[int]): ID of the parent comment if nested
        """
        with self.Session() as session:
            session.execute(
                text("""
                    INSERT INTO comments (id, parent_id, story_id, by, text, time, kids, type)
                    VALUES (:id, :parent_id, :story_id, :by, :text, :time, :kids, :type)
                    ON CONFLICT (id) DO UPDATE SET
                        parent_id = EXCLUDED.parent_id,
                        story_id = EXCLUDED.story_id,
                        by = EXCLUDED.by,
                        text = EXCLUDED.text,
                        time = EXCLUDED.time,
                        kids = EXCLUDED.kids,
                        type = EXCLUDED.type
                """),
                {
                    'id': comment['id'],
                    'parent_id': parent_id,
                    'story_id': story_id,
                    'by': comment.get('by'),
                    'text': comment.get('text'),
                    'time': datetime.fromtimestamp(comment.get('time', 0)),
                    'kids': comment.get('kids', []),
                    'type': comment.get('type')
                }
            )
            session.commit()

    def load_user(self, user: Dict[str, Any]) -> None:
        """
        Load a user into the database.
        
        Args:
            user (Dict[str, Any]): User data to load
        """
        with self.Session() as session:
            session.execute(
                text("""
                    INSERT INTO users (id, username, created_at, karma, about)
                    VALUES (:id, :username, :created_at, :karma, :about)
                    ON CONFLICT (id) DO UPDATE SET
                        username = EXCLUDED.username,
                        created_at = EXCLUDED.created_at,
                        karma = EXCLUDED.karma,
                        about = EXCLUDED.about
                """),
                {
                    'id': user['id'],
                    'username': user['id'],  # Using id as username since that's what HackerNews uses
                    'created_at': datetime.fromtimestamp(user.get('created', 0)),
                    'karma': user.get('karma'),
                    'about': user.get('about')
                }
            )
            session.commit()

    def load_story_with_comments(self, story: Dict[str, Any]) -> None:
        """
        Load a story and its comments into the database.
        
        Args:
            story (Dict[str, Any]): Story with nested comments
        """
        self.load_story(story)
        
        def load_comments(comments: List[Dict[str, Any]], story_id: int, parent_id: Optional[int] = None):
            for comment in comments:
                if not comment:
                    continue
                self.load_comment(comment, story_id, parent_id)
                if 'comments' in comment:
                    load_comments(comment['comments'], story_id, comment['id'])

        if 'comments' in story:
            load_comments(story['comments'], story['id'])

    def load_job(self, job: Dict[str, Any]) -> None:
        """
        Load a job posting into the database.
        
        Args:
            job (Dict[str, Any]): Job data to load
        """
        with self.Session() as session:
            session.execute(
                text("""
                    INSERT INTO jobs (
                        id, title, url, text, score, time, by,
                        job_type, location, company, salary_range
                    )
                    VALUES (
                        :id, :title, :url, :text, :score, :time, :by,
                        :job_type, :location, :company, :salary_range
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        url = EXCLUDED.url,
                        text = EXCLUDED.text,
                        score = EXCLUDED.score,
                        time = EXCLUDED.time,
                        by = EXCLUDED.by,
                        job_type = EXCLUDED.job_type,
                        location = EXCLUDED.location,
                        company = EXCLUDED.company,
                        salary_range = EXCLUDED.salary_range
                """),
                {
                    'id': job['id'],
                    'title': job.get('title'),
                    'url': job.get('url'),
                    'text': job.get('text'),
                    'score': job.get('score'),
                    'time': datetime.fromtimestamp(job.get('time', 0)),
                    'by': job.get('by'),
                    'job_type': job.get('job_type'),
                    'location': job.get('location'),
                    'company': job.get('company'),
                    'salary_range': job.get('salary_range')
                }
            )
            session.commit()

    def load_recent_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """
        Load multiple job postings into the database.
        
        Args:
            jobs (List[Dict[str, Any]]): List of job data to load
        """
        for job in jobs:
            self.load_job(job)

# Example usage:
def main():
    database_url = "postgresql://user:password@localhost:5432/hackernews"
    loader = DataLoader(database_url)
    
    print("Initializing database...")
    loader.create_tables()
    print("✓ Database tables created successfully")
    
    print("\nStarting data loading process...")
    
    print("\nData loading completed successfully!")
    print(f"Total records loaded:")
    print(f"- Stories: {len(stories)}")
    print(f"- Comments: {len(comments)}")
    print(f"- Users: {len(users)}")
    print(f"- Jobs: {len(jobs)}")

if __name__ == "__main__":
    main() 