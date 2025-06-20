"""
HackerNews AI Chatbot implementation using LangChain.
"""

import logging
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage

from src.ai.langchain_setup import LangChainSetup
from src.ai.tools import HackerNewsTools

logger = logging.getLogger(__name__)

class HackerNewsChatbot:
    """Main chatbot class for HackerNews AI interactions."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the HackerNews chatbot.
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for creativity control
        """
        self.langchain_setup = LangChainSetup(model_name, temperature)
        self.tools = HackerNewsTools()
        self.agent = None
        self.agent_executor = None
        
        self._setup_agent()
    
    def _setup_agent(self) -> None:
        """Setup the LangChain agent with tools."""
        try:
            # Create the agent prompt template
            agent_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful AI assistant that specializes in analyzing HackerNews data. 
                You have access to a PostgreSQL database containing HackerNews stories, comments, users, and job postings.
                
                Your capabilities include:
                - Searching and analyzing HackerNews stories by topics, keywords, or time periods
                - Finding job postings with specific criteria (location, type, company, etc.)
                - Analyzing user activity and karma scores
                - Providing insights about trending topics and discussions
                - Answering questions about the HackerNews community
                
                IMPORTANT: When using tools, always use the correct parameter types:
                - Integer parameters (limit, days_back, min_score) must be numbers, not strings
                - String parameters (query, username, location) should be text
                - For time periods, use integers: 7 for last week, 30 for last month, 365 for last year
                
                Examples:
                - "last week" → use days_back=7
                - "top 10 stories" → use limit=10
                - "stories about python" → use query="python"
                
                Always provide accurate, helpful responses based on the available data. If you don't have enough information
                to answer a question, be honest about it and suggest what additional data might be needed.
                
                When using tools, be specific and use the most appropriate tool for the query.
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Create the agent
            self.agent = create_openai_tools_agent(
                llm=self.langchain_setup.get_llm(),
                tools=self.tools.get_tools(),
                prompt=agent_prompt
            )
            
            # Create the agent executor with memory
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools.get_tools(),
                memory=self.langchain_setup.get_memory(),
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            logger.info("Initialized HackerNews chatbot agent")
            
        except Exception as e:
            logger.error(f"Failed to setup agent: {str(e)}")
            raise
    
    def chat(self, message: str) -> str:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            message: User message
            
        Returns:
            str: Chatbot response
        """
        try:
            if not self.agent_executor:
                raise ValueError("Agent executor not initialized")
            
            # Get response from agent
            response = self.agent_executor.invoke({"input": message})
            
            # Save to memory
            self.langchain_setup.save_memory(message, response["output"])
            
            return response["output"]
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def get_chat_history(self) -> List[BaseMessage]:
        """Get the current chat history."""
        try:
            memory_vars = self.langchain_setup.get_memory_variables()
            return memory_vars.get("chat_history", [])
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        try:
            self.langchain_setup.clear_memory()
            logger.info("Cleared chat history")
        except Exception as e:
            logger.error(f"Error clearing chat history: {str(e)}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return self.tools.get_tool_names()
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available tools."""
        tools = self.tools.get_tools()
        return {tool.name: tool.description for tool in tools}
    
    def direct_tool_call(self, tool_name: str, **kwargs) -> str:
        """
        Call a specific tool directly.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments for the tool
            
        Returns:
            str: Tool response
        """
        try:
            tools = self.tools.get_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            
            if not tool:
                return f"Tool '{tool_name}' not found. Available tools: {self.get_available_tools()}"
            
            return tool.run(kwargs)
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return f"Error calling tool {tool_name}: {str(e)}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information about the chatbot."""
        return {
            "model": self.langchain_setup.model_name,
            "temperature": self.langchain_setup.temperature,
            "available_tools": self.get_available_tools(),
            "tool_descriptions": self.get_tool_descriptions(),
            "memory_type": "ConversationBufferMemory"
        }
    
    def suggest_queries(self) -> List[str]:
        """Get suggested queries for users."""
        return [
            "What are the top stories from the last week?",
            "Find job postings for remote Python developers",
            "Search for stories about artificial intelligence",
            "Get information about user 'pg'",
            "What are the trending topics right now?",
            "Find jobs in San Francisco",
            "Search for stories about blockchain from the last month",
            "Show me high-scoring stories about machine learning"
        ]
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the chatbot system."""
        try:
            # Test basic functionality
            test_response = self.chat("Hello, can you help me with HackerNews data?")
            
            return {
                "status": "healthy",
                "model": self.langchain_setup.model_name,
                "tools_available": len(self.tools.get_tools()),
                "memory_working": True,
                "test_response_length": len(test_response),
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.langchain_setup.model_name,
                "tools_available": len(self.tools.get_tools()),
                "memory_working": False,
                "errors": [str(e)]
            } 