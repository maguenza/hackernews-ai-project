"""
FastAPI routes for HackerNews AI chatbot.
"""

import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from src.ai.chatbot import HackerNewsChatbot
from src.database.connection import get_db_connection

logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot: HackerNewsChatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global chatbot
    
    # Startup
    logger.info("Starting HackerNews AI chatbot...")
    try:
        chatbot = HackerNewsChatbot()
        logger.info("Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down HackerNews AI chatbot...")

# Create FastAPI app
app = FastAPI(
    title="HackerNews AI Chatbot",
    description="AI-powered chatbot for analyzing HackerNews data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str = None

class HealthResponse(BaseModel):
    status: str
    chatbot_status: Dict[str, Any]
    database_status: str

class SystemInfoResponse(BaseModel):
    model: str
    temperature: float
    available_tools: List[str]
    tool_descriptions: Dict[str, str]
    memory_type: str

class SuggestedQueriesResponse(BaseModel):
    queries: List[str]

# Dependency to get chatbot instance
def get_chatbot() -> HackerNewsChatbot:
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    return chatbot

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check chatbot health
        chatbot_health = chatbot.health_check() if chatbot else {"status": "not_initialized"}
        
        # Check database connection
        try:
            with get_db_connection() as db:
                db.execute("SELECT 1")
            db_status = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = f"error: {str(e)}"
        
        return HealthResponse(
            status="healthy" if chatbot_health.get("status") == "healthy" and db_status == "connected" else "unhealthy",
            chatbot_status=chatbot_health,
            database_status=db_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, chatbot_instance: HackerNewsChatbot = Depends(get_chatbot)):
    """Send a message to the chatbot."""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = chatbot_instance.chat(request.message)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# System information endpoint
@app.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info(chatbot_instance: HackerNewsChatbot = Depends(get_chatbot)):
    """Get system information about the chatbot."""
    try:
        info = chatbot_instance.get_system_info()
        return SystemInfoResponse(**info)
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")

# Suggested queries endpoint
@app.get("/suggestions", response_model=SuggestedQueriesResponse)
async def get_suggested_queries(chatbot_instance: HackerNewsChatbot = Depends(get_chatbot)):
    """Get suggested queries for users."""
    try:
        queries = chatbot_instance.suggest_queries()
        return SuggestedQueriesResponse(queries=queries)
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")

# Clear chat history endpoint
@app.post("/chat/clear")
async def clear_chat_history(chatbot_instance: HackerNewsChatbot = Depends(get_chatbot)):
    """Clear the chat history."""
    try:
        chatbot_instance.clear_chat_history()
        return {"message": "Chat history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")

# Direct tool call endpoint
@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, params: Dict[str, Any], chatbot_instance: HackerNewsChatbot = Depends(get_chatbot)):
    """Call a specific tool directly."""
    try:
        result = chatbot_instance.direct_tool_call(tool_name, **params)
        return {"tool": tool_name, "result": result}
        
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling tool {tool_name}: {str(e)}")

# Available tools endpoint
@app.get("/tools")
async def get_available_tools(chatbot_instance: HackerNewsChatbot = Depends(get_chatbot)):
    """Get list of available tools."""
    try:
        tools = chatbot_instance.get_available_tools()
        descriptions = chatbot_instance.get_tool_descriptions()
        return {
            "tools": tools,
            "descriptions": descriptions
        }
        
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")

# Replace the root endpoint to serve the chatbot UI
@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html")) 