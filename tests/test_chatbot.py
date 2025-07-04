"""
Unit tests for HackerNews AI Chatbot.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Ensure project root is in the path when running this file directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.ai.chatbot import HackerNewsChatbot
from src.ai.tools import (
    SearchStoriesTool, 
    SearchJobsTool, 
    GetTopStoriesTool, 
    GetUserInfoTool,
    GetTrendingTopicsTool
)
from src.ai.langchain_setup import LangChainSetup

class TestLangChainSetup:
    """Test LangChain setup functionality."""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_langchain_setup_initialization(self, mock_chat_openai):
        """Test LangChain setup initialization."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        setup = LangChainSetup()
        assert setup.model_name == "gpt-3.5-turbo"
        assert setup.temperature == 0.7
        assert setup.llm is not None
        assert setup.memory is not None
        assert setup.chain is not None
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_memory_operations(self, mock_chat_openai):
        """Test memory operations."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        setup = LangChainSetup()
        
        # Test save and load memory
        setup.save_memory("Hello", "Hi there!")
        memory_vars = setup.get_memory_variables()
        assert "chat_history" in memory_vars
        
        # Test clear memory
        setup.clear_memory()
        memory_vars = setup.get_memory_variables()
        assert len(memory_vars.get("chat_history", [])) == 0

class TestHackerNewsTools:
    """Test HackerNews tools functionality."""
    
    def test_search_stories_tool(self):
        """Test search stories tool."""
        tool = SearchStoriesTool()
        assert tool.name == "search_stories"
        assert "Search for HackerNews stories" in tool.description
    
    def test_search_jobs_tool(self):
        """Test search jobs tool."""
        tool = SearchJobsTool()
        assert tool.name == "search_jobs"
        assert "Search for HackerNews job postings" in tool.description
    
    def test_get_top_stories_tool(self):
        """Test get top stories tool."""
        tool = GetTopStoriesTool()
        assert tool.name == "get_top_stories"
        assert "Get the top HackerNews stories" in tool.description
    
    def test_get_user_info_tool(self):
        """Test get user info tool."""
        tool = GetUserInfoTool()
        assert tool.name == "get_user_info"
        assert "Get information about a HackerNews user" in tool.description
    
    def test_get_trending_topics_tool(self):
        """Test get trending topics tool."""
        tool = GetTrendingTopicsTool()
        assert tool.name == "get_trending_topics"
        assert "Analyze trending topics" in tool.description
    
    @patch('src.ai.tools.get_db_connection')
    def test_search_stories_tool_execution(self, mock_db_connection):
        """Test search stories tool execution."""
        # Mock database session and query results
        mock_session = Mock()
        mock_story = Mock()
        mock_story.title = "Test Story"
        mock_story.score = 100
        mock_story.by = "test_user"  # Fix: Set the actual attribute instead of author_id
        mock_story.created_at.strftime.return_value = "2024-01-01"
        mock_story.url = "http://example.com"
        
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_story]
        
        mock_db_connection.return_value.__enter__.return_value = mock_session
        
        tool = SearchStoriesTool()
        result = tool._run("test", limit=1)
        
        assert "Test Story" in result
        assert "Score: 100" in result
        assert "test_user" in result
    
    @patch('src.ai.tools.get_db_connection')
    def test_search_jobs_tool_execution(self, mock_db_connection):
        """Test search jobs tool execution."""
        # Mock database session and query results
        mock_session = Mock()
        mock_job = Mock()
        mock_job.title = "Python Developer"
        mock_job.company = "Test Company"
        mock_job.location = "Remote"
        mock_job.job_type = "full-time"
        mock_job.created_at.strftime.return_value = "2024-01-01"
        mock_job.url = "http://example.com"
        
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_job]
        
        mock_db_connection.return_value.__enter__.return_value = mock_session
        
        tool = SearchJobsTool()
        result = tool._run("python", limit=1)
        
        assert "Python Developer" in result
        assert "Test Company" in result
        assert "Remote" in result

class TestHackerNewsChatbot:
    """Test HackerNews chatbot functionality."""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_initialization(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot initialization."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        assert chatbot.langchain_setup is not None
        assert chatbot.tools is not None
        assert len(chatbot.get_available_tools()) == 5
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_system_info(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot system info."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        info = chatbot.get_system_info()
        
        assert "model" in info
        assert "temperature" in info
        assert "available_tools" in info
        assert "tool_descriptions" in info
        assert "memory_type" in info
        assert info["model"] == "gpt-3.5-turbo"
        assert info["temperature"] == 0.7
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_suggested_queries(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot suggested queries."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        queries = chatbot.suggest_queries()
        
        assert isinstance(queries, list)
        assert len(queries) > 0
        assert all(isinstance(q, str) for q in queries)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_tool_descriptions(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot tool descriptions."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        descriptions = chatbot.get_tool_descriptions()
        
        assert isinstance(descriptions, dict)
        assert len(descriptions) == 5
        assert all(isinstance(desc, str) for desc in descriptions.values())
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_clear_history(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot clear history."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        # Should not raise an exception
        chatbot.clear_chat_history()
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_health_check(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot health check."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        health = chatbot.health_check()
        
        assert "status" in health
        assert "model" in health
        assert "tools_available" in health
        assert "memory_working" in health
        assert "errors" in health
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_direct_tool_call(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot direct tool call."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        
        # Test calling a tool directly
        result = chatbot.direct_tool_call("search_stories", query="test")
        assert isinstance(result, str)

class TestChatbotIntegration:
    """Test chatbot integration scenarios."""
    
    @pytest.fixture
    def mock_environment(self):
        """Mock environment for integration tests."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            yield
    
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_full_chatbot_workflow(self, mock_chat_openai, mock_setup_agent, mock_environment):
        """Test full chatbot workflow."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        
        # Test basic functionality
        assert chatbot.get_available_tools() is not None
        assert chatbot.get_system_info() is not None
        assert chatbot.suggest_queries() is not None

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_tool_execution_error(self):
        """Test tool execution error handling."""
        tool = SearchStoriesTool()
        # This should handle errors gracefully
        result = tool._run("test", limit=1)
        assert isinstance(result, str)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.chatbot.HackerNewsChatbot._setup_agent')
    @patch('src.ai.langchain_setup.ChatOpenAI')
    def test_chatbot_error_handling(self, mock_chat_openai, mock_setup_agent):
        """Test chatbot error handling."""
        # Mock the ChatOpenAI class
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        chatbot = HackerNewsChatbot()
        
        # Test error handling in chat method
        result = chatbot.chat("test message")
        assert isinstance(result, str)

if __name__ == "__main__":
    pytest.main([__file__]) 