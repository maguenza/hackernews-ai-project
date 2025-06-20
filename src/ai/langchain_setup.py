"""
LangChain setup and configuration for HackerNews AI project.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class LangChainSetup:
    """LangChain configuration and setup for HackerNews chatbot."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize LangChain setup.
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for creativity control
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.memory = None
        self.chain = None
        
        # Load .env file if it exists
        self._load_env()
        
        self._setup_llm()
        self._setup_memory()
        self._setup_chain()
    
    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        try:
            # Try to find .env file in current directory or project root
            env_paths = [
                Path(".env"),
                Path(__file__).parent.parent.parent / ".env",
                Path.cwd() / ".env"
            ]
            
            for env_path in env_paths:
                if env_path.exists():
                    load_dotenv(env_path)
                    logger.info(f"Loaded environment variables from {env_path}")
                    return
            
            logger.warning("No .env file found")
            
        except Exception as e:
            logger.warning(f"Failed to load .env file: {str(e)}")
    
    def _setup_llm(self) -> None:
        """Initialize the language model."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key
            )
            logger.info(f"Initialized LLM: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def _setup_memory(self) -> None:
        """Initialize conversation memory."""
        try:
            # Use ConversationBufferMemory for simple chat history
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="input"
            )
            logger.info("Initialized conversation memory")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory: {str(e)}")
            raise
    
    def _setup_chain(self) -> None:
        """Setup the main conversation chain."""
        try:
            # Create the system prompt template
            system_template = """You are a helpful AI assistant that specializes in analyzing HackerNews data. 
            You have access to a PostgreSQL database containing HackerNews stories, comments, users, and job postings.
            
            Your capabilities include:
            - Searching and analyzing HackerNews stories by topics, keywords, or time periods
            - Finding job postings with specific criteria (location, type, company, etc.)
            - Analyzing user activity and karma scores
            - Providing insights about trending topics and discussions
            - Answering questions about the HackerNews community
            
            Always provide accurate, helpful responses based on the available data. If you don't have enough information
            to answer a question, be honest about it and suggest what additional data might be needed.
            
            Current conversation:
            {chat_history}
            
            Human: {input}
            AI Assistant:"""
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Create the chain
            self.chain = (
                {"chat_history": self.memory.load_memory_variables, "input": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            logger.info("Initialized conversation chain")
            
        except Exception as e:
            logger.error(f"Failed to setup chain: {str(e)}")
            raise
    
    def get_chain(self):
        """Get the configured conversation chain."""
        return self.chain
    
    def get_memory(self):
        """Get the conversation memory."""
        return self.memory
    
    def get_llm(self):
        """Get the language model."""
        return self.llm
    
    def clear_memory(self) -> None:
        """Clear the conversation memory."""
        if self.memory:
            self.memory.clear()
            logger.info("Cleared conversation memory")
    
    def save_memory(self, input_text: str, output_text: str) -> None:
        """
        Save a conversation turn to memory.
        
        Args:
            input_text: User input
            output_text: AI response
        """
        if self.memory:
            self.memory.save_context(
                {"input": input_text},
                {"output": output_text}
            )
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get current memory variables."""
        if self.memory:
            return self.memory.load_memory_variables({})
        return {} 