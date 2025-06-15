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
                    created TIMESTAMP,
                    karma INTEGER,
                    about TEXT,
                    submitted INTEGER[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                    INSERT INTO users (id, created, karma, about, submitted)
                    VALUES (:id, :created, :karma, :about, :submitted)
                    ON CONFLICT (id) DO UPDATE SET
                        created = EXCLUDED.created,
                        karma = EXCLUDED.karma,
                        about = EXCLUDED.about,
                        submitted = EXCLUDED.submitted
                """),
                {
                    'id': user['id'],
                    'created': datetime.fromtimestamp(user.get('created', 0)),
                    'karma': user.get('karma'),
                    'about': user.get('about'),
                    'submitted': user.get('submitted', [])
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

# Example usage:
def main():
    database_url = "postgresql://user:password@localhost:5432/hackernews"
    loader = DataLoader(database_url)
    
    # Create tables
    loader.create_tables()
    
    # Example story data
    story = {
        'id': 1,
        'title': 'Example Story',
        'url': 'https://example.com',
        'score': 100,
        'time': datetime.now().timestamp(),
        'by': 'user1',
        'descendants': 2,
        'kids': [2, 3],
        'text': 'Story text',
        'type': 'story'
    }
    loader.load_story(story)

if __name__ == "__main__":
    main() 