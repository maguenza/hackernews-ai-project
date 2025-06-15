"""
HackerNews API data extraction module.
Handles fetching and processing data from the HackerNews API.
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ratelimit import limits, sleep_and_retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HackerNewsExtractor:
    """Class to handle data extraction from HackerNews API."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self, rate_limit: int = 100, time_period: int = 60):
        """
        Initialize the HackerNews extractor.
        
        Args:
            rate_limit (int): Number of requests allowed per time period
            time_period (int): Time period in seconds
        """
        self.rate_limit = rate_limit
        self.time_period = time_period
        self.session = requests.Session()

    @sleep_and_retry
    @limits(calls=100, period=60)
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a request to the HackerNews API with rate limiting.
        
        Args:
            endpoint (str): API endpoint to call
            
        Returns:
            Dict[str, Any]: JSON response from the API
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            raise

    def get_top_stories(self, limit: int = 100) -> List[int]:
        """
        Get IDs of top stories.
        
        Args:
            limit (int): Maximum number of story IDs to return
            
        Returns:
            List[int]: List of story IDs
        """
        stories = self._make_request("topstories.json")
        return stories[:limit]

    def get_story(self, story_id: int) -> Dict[str, Any]:
        """
        Get details of a specific story.
        
        Args:
            story_id (int): ID of the story to fetch
            
        Returns:
            Dict[str, Any]: Story details
        """
        return self._make_request(f"item/{story_id}.json")

    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get details of a specific user.
        
        Args:
            username (str): Username to fetch
            
        Returns:
            Dict[str, Any]: User details
        """
        return self._make_request(f"user/{username}.json")

    def get_story_with_comments(self, story_id: int) -> Dict[str, Any]:
        """
        Get a story and its comments recursively.
        
        Args:
            story_id (int): ID of the story to fetch
            
        Returns:
            Dict[str, Any]: Story with nested comments
        """
        story = self.get_story(story_id)
        if not story or 'kids' not in story:
            return story

        def get_comment(comment_id: int) -> Optional[Dict[str, Any]]:
            comment = self.get_story(comment_id)
            if not comment:
                return None
                
            if 'kids' in comment:
                comment['comments'] = [
                    get_comment(kid) for kid in comment['kids']
                ]
            return comment

        story['comments'] = [
            get_comment(kid) for kid in story['kids']
        ]
        return story

    def get_recent_stories(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get stories from the last N hours.
        
        Args:
            hours (int): Number of hours to look back
            
        Returns:
            List[Dict[str, Any]]: List of stories
        """
        stories = []
        story_ids = self.get_top_stories(limit=500)  # Get more stories to filter by time
        
        for story_id in story_ids:
            story = self.get_story(story_id)
            if not story:
                continue
                
            story_time = datetime.fromtimestamp(story.get('time', 0))
            if (datetime.now() - story_time).total_seconds() <= hours * 3600:
                stories.append(story)
                
        return stories

# Example usage:
def main():
    extractor = HackerNewsExtractor()
    
    # Get top 10 stories
    top_stories = extractor.get_top_stories(limit=10)
    
    # Get details for each story
    for story_id in top_stories:
        story = extractor.get_story(story_id)
        print(f"Title: {story.get('title')}")
        print(f"Score: {story.get('score')}")
        print("---")

if __name__ == "__main__":
    main() 