"""
Main script to run the HackerNews AI data pipeline.
"""

import os
import logging
from dotenv import load_dotenv
from src.data.extractor import HackerNewsExtractor
from src.data.loader import DataLoader
from src.data.transformer import DataTransformer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the data pipeline."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database URL from environment
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/hackernews_ai"
        )
        
        logger.info("Initializing data pipeline...")
        
        # Initialize components
        extractor = HackerNewsExtractor()
        loader = DataLoader(database_url)
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        transformer = DataTransformer(session)
        
        # Create database tables
        logger.info("Creating database tables...")
        loader.create_tables()
        transformer.create_analysis_tables()
        
        # Process Stories and Comments
        logger.info("Processing stories and comments...")
        story_ids = extractor.get_top_stories(limit=100)
        stories_processed = 0
        comments_processed = 0
        users_processed = set()
        
        for story_id in story_ids:
            try:
                # Get story with comments
                story = extractor.get_story_with_comments(story_id)
                if not story:
                    continue
                
                # Load story and its comments
                logger.info(f"Loading story {story_id} and its comments...")
                loader.load_story_with_comments(story)
                stories_processed += 1
                
                # Count comments
                if 'kids' in story:
                    comments_processed += len(story['kids'])
                
                # Get and load user data
                if 'by' in story:
                    user = extractor.get_user(story['by'])
                    if user:
                        loader.load_user(user)
                        users_processed.add(user['id'])
                
                # Transform story data
                logger.info(f"Transforming story {story_id} data...")
                transformer.transform_story_data(story_id)
                
            except Exception as e:
                logger.error(f"Error processing story {story_id}: {str(e)}")
                continue
        
        # Process Jobs
        logger.info("Processing job postings...")
        job_ids = extractor.get_job_postings(limit=100)
        jobs_processed = 0
        
        for job_id in job_ids:
            try:
                # Get job details
                job = extractor.get_job(job_id)
                if not job:
                    continue
                
                # First, ensure the user exists
                if 'by' in job:
                    user = extractor.get_user(job['by'])
                    if user:
                        logger.info(f"Loading user {job['by']} for job {job_id}...")
                        loader.load_user(user)
                        users_processed.add(user['id'])
                    else:
                        logger.warning(f"User {job['by']} not found, skipping job {job_id}")
                        continue
                
                # Load job
                logger.info(f"Loading job {job_id}...")
                loader.load_job(job)
                jobs_processed += 1
                
                # Transform job data
                logger.info(f"Transforming job {job_id} data...")
                transformer.transform_job_data(job_id)
                
            except Exception as e:
                logger.error(f"Error processing job {job_id}: {str(e)}")
                continue
        
        # Analyze topics
        logger.info("Analyzing topics...")
        transformer.analyze_topics()
        
        # Print summary
        logger.info("\nData pipeline completed successfully!")
        logger.info("Summary of processed data:")
        logger.info(f"- Stories processed: {stories_processed}")
        logger.info(f"- Comments processed: {comments_processed}")
        logger.info(f"- Users processed: {len(users_processed)}")
        logger.info(f"- Jobs processed: {jobs_processed}")
        
    except Exception as e:
        logger.error(f"Error in data pipeline: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main() 