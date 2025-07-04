"""
Custom LangChain tools for HackerNews database queries.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text, func, desc, and_
from sqlalchemy.orm import Session
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.database.connection import get_db_connection
from src.database.models import Story, Comment, User, Job

logger = logging.getLogger(__name__)

class SearchStoriesInput(BaseModel):
    """Input schema for searching stories."""
    query: str = Field(description="Search query for story titles and content (string)")
    limit: int = Field(default=10, description="Maximum number of results to return (integer)")
    min_score: Optional[int] = Field(default=None, description="Minimum story score (integer)")
    days_back: Optional[int] = Field(default=30, description="Number of days back to search (integer)")

class SearchJobsInput(BaseModel):
    """Input schema for searching jobs."""
    query: str = Field(description="Search query for job titles and descriptions (string)")
    location: Optional[str] = Field(default=None, description="Job location filter (string)")
    job_type: Optional[str] = Field(default=None, description="Job type (string: full-time, contract, remote)")
    limit: int = Field(default=10, description="Maximum number of results to return (integer)")

class GetTopStoriesInput(BaseModel):
    """Input schema for getting top stories."""
    limit: int = Field(default=10, description="Number of top stories to return (integer)")
    days_back: int = Field(default=7, description="Number of days back to consider (integer, e.g., 7 for last week, 30 for last month)")

class GetUserInfoInput(BaseModel):
    """Input schema for getting user information."""
    username: str = Field(description="HackerNews username (string)")

class SearchStoriesTool(BaseTool):
    """Tool for searching HackerNews stories."""
    
    name: str = "search_stories"
    description: str = "Search for HackerNews stories by keywords in title or content. Use query (string) for search terms, limit (integer) for number of results, min_score (integer) for minimum score, days_back (integer) for time period"
    args_schema: type = SearchStoriesInput
    
    def _run(self, query: str, limit: int = 10, min_score: Optional[int] = None, days_back: Optional[int] = 30) -> str:
        """Search for stories matching the query."""
        try:
            with get_db_connection() as db:
                # Build the query
                search_condition = Story.title.ilike(f"%{query}%")
                
                if min_score is not None:
                    search_condition = and_(search_condition, Story.score >= min_score)
                
                if days_back:
                    cutoff_date = datetime.now() - timedelta(days=days_back)
                    search_condition = and_(search_condition, Story.created_at >= cutoff_date)
                
                stories = db.query(Story).filter(search_condition).order_by(desc(Story.score)).limit(limit).all()
                
                if not stories:
                    return f"No stories found matching '{query}'"
                
                result = f"Found {len(stories)} stories matching '{query}':\n\n"
                for story in stories:
                    result += f"📰 {story.title}\n"
                    result += f"   Score: {story.score} | Author: {story.by} | Date: {story.created_at.strftime('%Y-%m-%d') if story.created_at else 'N/A'}\n"
                    if story.url:
                        result += f"   URL: {story.url}\n"
                    result += "\n"
                
                return result
                
        except Exception as e:
            logger.error(f"Error searching stories: {str(e)}")
            return f"Error searching stories: {str(e)}"

class SearchJobsTool(BaseTool):
    """Tool for searching HackerNews job postings."""
    
    name: str = "search_jobs"
    description: str = "Search for HackerNews job postings by keywords, location, or job type. Use query (string) for search terms, location (string) for location filter, job_type (string) for job type, limit (integer) for number of results"
    args_schema: type = SearchJobsInput
    
    def _run(self, query: str, location: Optional[str] = None, job_type: Optional[str] = None, limit: int = 10) -> str:
        """Search for jobs matching the criteria."""
        try:
            with get_db_connection() as db:
                # Build the query
                search_condition = Job.title.ilike(f"%{query}%")
                
                if location:
                    search_condition = and_(search_condition, Job.location.ilike(f"%{location}%"))
                
                if job_type:
                    search_condition = and_(search_condition, Job.job_type.ilike(f"%{job_type}%"))
                
                jobs = db.query(Job).filter(search_condition).order_by(desc(Job.created_at)).limit(limit).all()
                
                if not jobs:
                    return f"No jobs found matching '{query}'"
                
                result = f"Found {len(jobs)} jobs matching '{query}':\n\n"
                for job in jobs:
                    result += f"💼 {job.title}\n"
                    result += f"   Company: {job.company or 'N/A'} | Location: {job.location or 'N/A'}\n"
                    result += f"   Type: {job.job_type or 'N/A'} | Posted: {job.created_at.strftime('%Y-%m-%d') if job.created_at else 'N/A'}\n"
                    if job.url:
                        result += f"   URL: {job.url}\n"
                    result += "\n"
                
                return result
                
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return f"Error searching jobs: {str(e)}"

class GetTopStoriesTool(BaseTool):
    """Tool for getting top stories by score."""
    
    name: str = "get_top_stories"
    description: str = "Get the top HackerNews stories by score for a given time period. Use limit (integer) for number of stories and days_back (integer) for time period (e.g., 7 for last week, 30 for last month)"
    args_schema: type = GetTopStoriesInput
    
    def _run(self, limit: int = 10, days_back: int = 7) -> str:
        """Get top stories by score."""
        try:
            with get_db_connection() as db:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                stories = db.query(Story).filter(
                    Story.created_at >= cutoff_date
                ).order_by(desc(Story.score)).limit(limit).all()
                
                if not stories:
                    return f"No stories found in the last {days_back} days"
                
                result = f"Top {len(stories)} stories in the last {days_back} days:\n\n"
                for i, story in enumerate(stories, 1):
                    result += f"{i}. {story.title}\n"
                    result += f"   Score: {story.score} | Author: {story.by} | Date: {story.created_at.strftime('%Y-%m-%d') if story.created_at else 'N/A'}\n"
                    if story.url:
                        result += f"   URL: {story.url}\n"
                    result += "\n"
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting top stories: {str(e)}")
            return f"Error getting top stories: {str(e)}"

class GetUserInfoTool(BaseTool):
    """Tool for getting user information."""
    
    name: str = "get_user_info"
    description: str = "Get information about a HackerNews user including karma and activity. Use username (string) for the HackerNews username"
    args_schema: type = GetUserInfoInput
    
    def _run(self, username: str) -> str:
        """Get user information."""
        try:
            with get_db_connection() as db:
                user = db.query(User).filter(
                    User.username == username
                ).first()
                
                if not user:
                    return f"User '{username}' not found"
                
                # Get user's story and comment counts
                story_count = db.query(Story).filter(
                    Story.by == user.id
                ).count()
                
                comment_count = db.query(Comment).filter(
                    Comment.by == user.id
                ).count()
                
                result = f"👤 User: {user.username}\n"
                result += f"   Karma: {user.karma}\n"
                result += f"   Member since: {user.created_at.strftime('%Y-%m-%d')}\n"
                result += f"   Stories posted: {story_count}\n"
                result += f"   Comments made: {comment_count}\n"
                
                if user.about:
                    result += f"   About: {user.about}\n"
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return f"Error getting user info: {str(e)}"

class GetTrendingTopicsTool(BaseTool):
    """Tool for analyzing trending topics."""
    
    name: str = "get_trending_topics"
    description: str = "Analyze trending topics from recent HackerNews stories. Use limit (integer) for number of stories and days_back (integer) for time period (e.g., 7 for last week, 30 for last month)"
    args_schema: type = GetTopStoriesInput
    
    def _run(self, limit: int = 10, days_back: int = 7) -> str:
        """Get trending topics from recent stories."""
        try:
            with get_db_connection() as db:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                # Get recent stories with high scores
                stories = db.query(Story).filter(
                    and_(
                        Story.created_at >= cutoff_date,
                        Story.score >= 50  # Only high-scoring stories
                    )
                ).order_by(desc(Story.score)).limit(limit).all()
                
                if not stories:
                    return f"No trending stories found in the last {days_back} days"
                
                result = f"🔥 Trending topics in the last {days_back} days:\n\n"
                for i, story in enumerate(stories, 1):
                    result += f"{i}. {story.title}\n"
                    result += f"   Score: {story.score} | Comments: {story.descendants or 0}\n"
                    result += "\n"
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            return f"Error getting trending topics: {str(e)}"

class HackerNewsTools:
    """Collection of HackerNews-specific LangChain tools."""
    
    def __init__(self):
        """Initialize all HackerNews tools."""
        self.tools = [
            SearchStoriesTool(),
            SearchJobsTool(),
            GetTopStoriesTool(),
            GetUserInfoTool(),
            GetTrendingTopicsTool()
        ]
    
    def get_tools(self) -> List[BaseTool]:
        """Get all available tools."""
        return self.tools
    
    def get_tool_names(self) -> List[str]:
        """Get names of all available tools."""
        return [tool.name for tool in self.tools] 