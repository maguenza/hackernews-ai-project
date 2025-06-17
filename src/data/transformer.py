"""
Data transformation module for HackerNews AI project.
Handles transforming raw data into analysis-ready formats.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    """Class to handle data transformation for analysis."""
    
    def __init__(self, session: Session):
        """
        Initialize the data transformer.
        
        Args:
            session (Session): SQLAlchemy session
        """
        self.session = session

    def create_analysis_tables(self):
        """Create tables for transformed data."""
        # Create table for story statistics
        self.session.execute(text("""
            CREATE TABLE IF NOT EXISTS story_stats (
                story_id INTEGER PRIMARY KEY,
                total_comments INTEGER,
                avg_comment_length FLOAT,
                max_comment_length INTEGER,
                min_comment_length INTEGER,
                comment_sentiment_score FLOAT,
                user_engagement_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id)
            )
        """))
        
        # Create table for user statistics
        self.session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                total_stories INTEGER,
                total_comments INTEGER,
                avg_story_score FLOAT,
                avg_comment_score FLOAT,
                engagement_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))
        
        # Create table for topic analysis
        self.session.execute(text("""
            CREATE TABLE IF NOT EXISTS topic_analysis (
                id SERIAL PRIMARY KEY,
                topic TEXT,
                story_count INTEGER,
                avg_score FLOAT,
                total_comments INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create table for job statistics
        self.session.execute(text("""
            CREATE TABLE IF NOT EXISTS job_stats (
                job_id INTEGER PRIMARY KEY,
                total_applications INTEGER,
                avg_salary_range FLOAT,
                job_type_distribution JSONB,
                location_distribution JSONB,
                company_distribution JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """))
        
        self.session.commit()

    def transform_story_data(self, story_id: int) -> Optional[Dict[str, Any]]:
        """
        Transform story data into analysis-ready format.
        
        Args:
            story_id (int): ID of the story to transform
            
        Returns:
            Optional[Dict[str, Any]]: Transformed story data or None if not found
        """
        try:
            # Get story and its comments
            result = self.session.execute(text("""
                WITH story_data AS (
                    SELECT 
                        s.*,
                        COUNT(c.id) as total_comments,
                        AVG(LENGTH(c.text)) as avg_comment_length,
                        MAX(LENGTH(c.text)) as max_comment_length,
                        MIN(LENGTH(c.text)) as min_comment_length
                    FROM stories s
                    LEFT JOIN comments c ON s.id = c.story_id
                    WHERE s.id = :story_id
                    GROUP BY s.id
                )
                SELECT * FROM story_data
            """), {'story_id': story_id})
            
            story_data = result.fetchone()
            if not story_data:
                logger.warning(f"No story found with id {story_id}")
                return None
                
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(story_data)
            
            # Store transformed data
            self.session.execute(text("""
                INSERT INTO story_stats (
                    story_id, total_comments, avg_comment_length,
                    max_comment_length, min_comment_length,
                    user_engagement_score
                )
                VALUES (
                    :story_id, :total_comments, :avg_comment_length,
                    :max_comment_length, :min_comment_length,
                    :engagement_score
                )
                ON CONFLICT (story_id) DO UPDATE SET
                    total_comments = EXCLUDED.total_comments,
                    avg_comment_length = EXCLUDED.avg_comment_length,
                    max_comment_length = EXCLUDED.max_comment_length,
                    min_comment_length = EXCLUDED.min_comment_length,
                    user_engagement_score = EXCLUDED.user_engagement_score
            """), {
                'story_id': story_id,
                'total_comments': story_data.total_comments,
                'avg_comment_length': float(story_data.avg_comment_length) if story_data.avg_comment_length else 0.0,
                'max_comment_length': story_data.max_comment_length,
                'min_comment_length': story_data.min_comment_length,
                'engagement_score': float(engagement_score)
            })
            
            self.session.commit()
            return dict(story_data._mapping)
            
        except Exception as e:
            logger.error(f"Error transforming story {story_id}: {str(e)}")
            self.session.rollback()
            raise

    def transform_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Transform user data into analysis-ready format.
        
        Args:
            user_id (str): ID of the user to transform
            
        Returns:
            Optional[Dict[str, Any]]: Transformed user data or None if not found
        """
        try:
            # Get user statistics
            result = self.session.execute(text("""
                WITH user_data AS (
                    SELECT 
                        u.*,
                        COUNT(DISTINCT s.id) as total_stories,
                        COUNT(DISTINCT c.id) as total_comments,
                        AVG(s.score) as avg_story_score,
                        AVG(c.score) as avg_comment_score
                    FROM users u
                    LEFT JOIN stories s ON u.id = s.by
                    LEFT JOIN comments c ON u.id = c.by
                    WHERE u.id = :user_id
                    GROUP BY u.id
                )
                SELECT * FROM user_data
            """), {'user_id': user_id})
            
            user_data = result.fetchone()
            if not user_data:
                logger.warning(f"No user found with id {user_id}")
                return None
                
            # Calculate engagement score
            engagement_score = self._calculate_user_engagement_score(user_data)
            
            # Store transformed data
            self.session.execute(text("""
                INSERT INTO user_stats (
                    user_id, total_stories, total_comments,
                    avg_story_score, avg_comment_score,
                    engagement_score
                )
                VALUES (
                    :user_id, :total_stories, :total_comments,
                    :avg_story_score, :avg_comment_score,
                    :engagement_score
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    total_stories = EXCLUDED.total_stories,
                    total_comments = EXCLUDED.total_comments,
                    avg_story_score = EXCLUDED.avg_story_score,
                    avg_comment_score = EXCLUDED.avg_comment_score,
                    engagement_score = EXCLUDED.engagement_score
            """), {
                'user_id': user_id,
                'total_stories': user_data.total_stories,
                'total_comments': user_data.total_comments,
                'avg_story_score': float(user_data.avg_story_score) if user_data.avg_story_score else 0.0,
                'avg_comment_score': float(user_data.avg_comment_score) if user_data.avg_comment_score else 0.0,
                'engagement_score': float(engagement_score)
            })
            
            self.session.commit()
            return dict(user_data._mapping)
            
        except Exception as e:
            logger.error(f"Error transforming user {user_id}: {str(e)}")
            self.session.rollback()
            raise

    def analyze_topics(self, time_period: int = 24) -> List[Dict[str, Any]]:
        """
        Analyze topics from recent stories.
        
        Args:
            time_period (int): Number of hours to look back
            
        Returns:
            List[Dict[str, Any]]: Topic analysis results
        """
        try:
            # Get recent stories and their comments
            result = self.session.execute(text("""
                WITH recent_stories AS (
                    SELECT 
                        s.id,
                        s.title,
                        s.score,
                        COUNT(c.id) as comment_count
                    FROM stories s
                    LEFT JOIN comments c ON s.id = c.story_id
                    WHERE s.time >= NOW() - INTERVAL ':time_period hours'
                    GROUP BY s.id, s.title, s.score
                )
                SELECT 
                    title as topic,
                    COUNT(*) as story_count,
                    AVG(score) as avg_score,
                    SUM(comment_count) as total_comments
                FROM recent_stories
                GROUP BY title
                ORDER BY story_count DESC
                LIMIT 10
            """), {'time_period': time_period})
            
            topics = result.fetchall()
            
            # Store topic analysis
            for topic in topics:
                self.session.execute(text("""
                    INSERT INTO topic_analysis (
                        topic, story_count, avg_score, total_comments
                    )
                    VALUES (
                        :topic, :story_count, :avg_score, :total_comments
                    )
                """), {
                    'topic': topic.topic,
                    'story_count': topic.story_count,
                    'avg_score': float(topic.avg_score) if topic.avg_score else 0.0,
                    'total_comments': topic.total_comments
                })
            
            self.session.commit()
            return [dict(topic._mapping) for topic in topics]
            
        except Exception as e:
            logger.error(f"Error analyzing topics: {str(e)}")
            self.session.rollback()
            raise

    def _calculate_engagement_score(self, story_data: Any) -> float:
        """
        Calculate engagement score for a story.
        
        Args:
            story_data: Story data from database
            
        Returns:
            float: Engagement score
        """
        # Simple engagement score calculation
        # Can be enhanced with more sophisticated metrics
        score = float(story_data.score) if story_data.score else 0.0
        comments = float(story_data.total_comments) if story_data.total_comments else 0.0
        avg_comment_length = float(story_data.avg_comment_length) if story_data.avg_comment_length else 0.0
        
        return (score * 0.4) + (comments * 0.4) + (avg_comment_length * 0.2)

    def _calculate_user_engagement_score(self, user_data: Any) -> float:
        """
        Calculate engagement score for a user.
        
        Args:
            user_data: User data from database
            
        Returns:
            float: Engagement score
        """
        # Simple user engagement score calculation
        # Can be enhanced with more sophisticated metrics
        stories = float(user_data.total_stories) if user_data.total_stories else 0.0
        comments = float(user_data.total_comments) if user_data.total_comments else 0.0
        avg_story_score = float(user_data.avg_story_score) if user_data.avg_story_score else 0.0
        avg_comment_score = float(user_data.avg_comment_score) if user_data.avg_comment_score else 0.0
        
        return (stories * 0.3) + (comments * 0.3) + (avg_story_score * 0.2) + (avg_comment_score * 0.2)

    def transform_job_data(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Transform job data into analysis-ready format.
        
        Args:
            job_id (int): ID of the job to transform
            
        Returns:
            Optional[Dict[str, Any]]: Transformed job data or None if not found
        """
        try:
            # Get job data
            result = self.session.execute(text("""
                SELECT 
                    j.*,
                    u.username as author_username,
                    u.karma as author_karma
                FROM jobs j
                JOIN users u ON j.author_id = u.id
                WHERE j.id = :job_id
            """), {'job_id': job_id})
            
            job_data = result.fetchone()
            if not job_data:
                logger.warning(f"No job found with id {job_id}")
                return None
                
            # Calculate job metrics
            job_metrics = self._calculate_job_metrics(job_data)
            
            # Store transformed data
            self.session.execute(text("""
                INSERT INTO job_stats (
                    job_id, total_applications, avg_salary_range,
                    job_type_distribution, location_distribution,
                    company_distribution
                )
                VALUES (
                    :job_id, :total_applications, :avg_salary_range,
                    :job_type_distribution, :location_distribution,
                    :company_distribution
                )
                ON CONFLICT (job_id) DO UPDATE SET
                    total_applications = EXCLUDED.total_applications,
                    avg_salary_range = EXCLUDED.avg_salary_range,
                    job_type_distribution = EXCLUDED.job_type_distribution,
                    location_distribution = EXCLUDED.location_distribution,
                    company_distribution = EXCLUDED.company_distribution
            """), {
                'job_id': job_id,
                'total_applications': job_metrics['total_applications'],
                'avg_salary_range': job_metrics['avg_salary_range'],
                'job_type_distribution': job_metrics['job_type_distribution'],
                'location_distribution': job_metrics['location_distribution'],
                'company_distribution': job_metrics['company_distribution']
            })
            
            self.session.commit()
            return dict(job_data._mapping)
            
        except Exception as e:
            logger.error(f"Error transforming job {job_id}: {str(e)}")
            self.session.rollback()
            raise

    def _calculate_job_metrics(self, job_data: Any) -> Dict[str, Any]:
        """
        Calculate metrics for a job posting.
        
        Args:
            job_data: Job data from database
            
        Returns:
            Dict[str, Any]: Job metrics
        """
        # Get similar jobs for comparison
        similar_jobs = self.session.execute(text("""
            SELECT 
                job_type,
                location,
                company,
                salary_range
            FROM jobs
            WHERE created_at >= NOW() - INTERVAL '30 days'
            AND job_type = :job_type
            AND location = :location
        """), {
            'job_type': job_data.job_type,
            'location': job_data.location
        }).fetchall()
        
        # Calculate distributions
        job_types = {}
        locations = {}
        companies = {}
        total_salary = 0
        salary_count = 0
        
        for job in similar_jobs:
            # Update distributions
            job_types[job.job_type] = job_types.get(job.job_type, 0) + 1
            locations[job.location] = locations.get(job.location, 0) + 1
            companies[job.company] = companies.get(job.company, 0) + 1
            
            # Process salary range if available
            if job.salary_range:
                try:
                    # Simple average of min and max salary
                    min_salary, max_salary = map(float, job.salary_range.split('-'))
                    total_salary += (min_salary + max_salary) / 2
                    salary_count += 1
                except (ValueError, AttributeError):
                    pass
        
        return {
            'total_applications': len(similar_jobs),
            'avg_salary_range': total_salary / salary_count if salary_count > 0 else 0,
            'job_type_distribution': job_types,
            'location_distribution': locations,
            'company_distribution': companies
        }

# Example usage:
def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    database_url = "postgresql://user:password@localhost:5432/hackernews"
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        transformer = DataTransformer(session)
        transformer.create_analysis_tables()
        
        # Transform data for a story
        story_data = transformer.transform_story_data(1)
        print(f"Transformed story data: {story_data}")
        
        # Transform data for a user
        user_data = transformer.transform_user_data("user1")
        print(f"Transformed user data: {user_data}")
        
        # Analyze topics
        topics = transformer.analyze_topics()
        print(f"Topic analysis: {topics}")

if __name__ == "__main__":
    main() 