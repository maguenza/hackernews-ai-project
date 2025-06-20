# LangChain Guide for HackerNews AI Chatbot

## What is LangChain?

**LangChain** is a powerful framework for building applications with Large Language Models (LLMs). It provides abstractions and tools to make it easier to work with LLMs and integrate them with external data sources, tools, and systems.

### Key LangChain Concepts

1. **LLMs (Large Language Models)**: The core AI models (GPT-4, Claude, etc.)
2. **Chains**: Sequences of operations that combine LLMs with other components
3. **Agents**: Autonomous systems that can use tools to accomplish tasks
4. **Tools**: Functions that agents can call to interact with external systems
5. **Memory**: Systems for storing and retrieving conversation history
6. **Prompts**: Templates for structuring inputs to LLMs

## How LangChain Works with Your HackerNews Data

### 1. **Data Flow Architecture**

```
User Query → LangChain Agent → Custom Tools → PostgreSQL Database → Structured Response
```

### 2. **Components in Your Implementation**

#### **LangChain Setup (`src/ai/langchain_setup.py`)**
- **LLM Configuration**: Connects to OpenAI's GPT models
- **Memory Management**: Stores conversation history
- **Chain Construction**: Creates the main conversation pipeline

#### **Custom Tools (`src/ai/tools.py`)**
- **SearchStoriesTool**: Query HackerNews stories by keywords
- **SearchJobsTool**: Find job postings with filters
- **GetTopStoriesTool**: Retrieve top stories by score
- **GetUserInfoTool**: Get user information and activity
- **GetTrendingTopicsTool**: Analyze trending topics

#### **Chatbot (`src/ai/chatbot.py`)**
- **Agent Integration**: Combines LLM with tools
- **Conversation Management**: Handles user interactions
- **Error Handling**: Graceful error management

## How to Use LangChain with Your PostgreSQL Data

### 1. **Setting Up the Environment**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key"
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

### 2. **Basic Usage**

```python
from src.ai.chatbot import HackerNewsChatbot

# Initialize chatbot
chatbot = HackerNewsChatbot()

# Send a message
response = chatbot.chat("What are the top stories from the last week?")
print(response)
```

### 3. **Direct Tool Usage**

```python
# Search for stories
result = chatbot.direct_tool_call("search_stories", query="python", limit=5)
print(result)

# Find jobs
result = chatbot.direct_tool_call("search_jobs", query="developer", location="remote")
print(result)

# Get user info
result = chatbot.direct_tool_call("get_user_info", username="pg")
print(result)
```

### 4. **API Usage**

```bash
# Start the API server
uvicorn src.api.routes:app --reload

# Send a chat message
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are the top stories?"}'

# Get system info
curl "http://localhost:8000/system/info"

# Get suggested queries
curl "http://localhost:8000/suggestions"
```

## LangChain Features in Your Implementation

### 1. **Agent-Based Architecture**

Your chatbot uses LangChain's **Agent** pattern, which allows the LLM to:
- Understand user intent
- Choose appropriate tools
- Execute multiple steps to answer complex queries
- Provide natural language responses

```python
# The agent automatically decides which tools to use
response = chatbot.chat("Find me remote Python jobs in San Francisco")
# Agent uses: search_jobs tool with appropriate parameters
```

### 2. **Custom Tools Integration**

Each tool is a LangChain `BaseTool` that:
- Has a defined input schema (Pydantic models)
- Executes database queries
- Returns structured responses
- Handles errors gracefully

```python
class SearchStoriesTool(BaseTool):
    name = "search_stories"
    description = "Search for HackerNews stories by keywords"
    args_schema = SearchStoriesInput
    
    def _run(self, query: str, limit: int = 10) -> str:
        # Database query logic
        # Return formatted response
```

### 3. **Memory Management**

LangChain's memory system maintains conversation context:

```python
# Memory automatically stores conversation history
chatbot.chat("What are the top stories?")
chatbot.chat("Tell me more about the first one")
# The second query has context from the first
```

### 4. **Prompt Engineering**

Your implementation uses structured prompts to:
- Define the AI's role and capabilities
- Provide context about available data
- Guide the AI's behavior and responses

```python
system_template = """You are a helpful AI assistant that specializes in analyzing HackerNews data.
Your capabilities include:
- Searching and analyzing HackerNews stories
- Finding job postings with specific criteria
- Analyzing user activity and karma scores
- Providing insights about trending topics
"""
```

## Advanced LangChain Features You Can Add

### 1. **Vector Stores for Semantic Search**

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Create embeddings for story content
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

# Semantic search
results = vectorstore.similarity_search("machine learning")
```

### 2. **Conversation Summary Memory**

```python
from langchain.memory import ConversationSummaryMemory

# For long conversations, summarize instead of storing all messages
memory = ConversationSummaryMemory(llm=llm)
```

### 3. **Retrieval-Augmented Generation (RAG)**

```python
from langchain.chains import RetrievalQA

# Combine vector search with LLM responses
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)
```

### 4. **Multi-Agent Systems**

```python
# Multiple specialized agents
story_agent = HackerNewsChatbot(model_name="gpt-4")
job_agent = HackerNewsChatbot(model_name="gpt-3.5-turbo")

# Route queries to appropriate agents
def route_query(query):
    if "job" in query.lower():
        return job_agent.chat(query)
    else:
        return story_agent.chat(query)
```

## Testing Your LangChain Implementation

### 1. **Unit Tests**

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_chatbot.py

# Run with coverage
pytest --cov=src tests/
```

### 2. **Integration Tests**

```python
# Test full workflow
def test_chatbot_workflow():
    chatbot = HackerNewsChatbot()
    
    # Test system info
    info = chatbot.get_system_info()
    assert info["model"] == "gpt-3.5-turbo"
    
    # Test tool availability
    tools = chatbot.get_available_tools()
    assert "search_stories" in tools
    
    # Test chat functionality
    response = chatbot.chat("Hello")
    assert len(response) > 0
```

### 3. **Manual Testing**

```bash
# Run the test script
python test_chatbot.py

# Test API endpoints
curl "http://localhost:8000/health"
curl "http://localhost:8000/tools"
```

## Best Practices for LangChain Development

### 1. **Tool Design**
- Keep tools focused and single-purpose
- Provide clear descriptions for the LLM
- Handle errors gracefully
- Return structured, readable responses

### 2. **Prompt Engineering**
- Be specific about the AI's role and capabilities
- Include examples when helpful
- Set appropriate constraints and guidelines
- Test prompts with various inputs

### 3. **Memory Management**
- Choose appropriate memory types for your use case
- Consider memory limits for long conversations
- Implement memory clearing when needed

### 4. **Error Handling**
- Catch and handle tool execution errors
- Provide meaningful error messages
- Implement fallback strategies
- Log errors for debugging

### 5. **Performance Optimization**
- Use appropriate model sizes for your needs
- Implement caching for frequent queries
- Optimize database queries in tools
- Monitor API usage and costs

## Deployment Considerations

### 1. **Environment Variables**
```bash
# Production environment
OPENAI_API_KEY=your_production_key
DATABASE_URL=your_production_db_url
MODEL_NAME=gpt-4  # or gpt-3.5-turbo
TEMPERATURE=0.7
```

### 2. **Rate Limiting**
```python
# Implement rate limiting for API calls
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=60, period=60)  # 60 calls per minute
def rate_limited_api_call():
    # Your API call here
    pass
```

### 3. **Monitoring**
```python
# Add logging and monitoring
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_chat_interaction(user_query, response, duration):
    logger.info(f"Chat interaction: {duration}s - Query: {user_query[:100]}...")
```

## Troubleshooting Common Issues

### 1. **API Key Issues**
```python
# Check API key configuration
import os
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not set")
```

### 2. **Database Connection Issues**
```python
# Test database connection
from src.database.connection import get_db_connection

try:
    with get_db_connection() as db:
        db.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

### 3. **Tool Execution Errors**
```python
# Add error handling to tools
def _run(self, query: str) -> str:
    try:
        # Tool logic here
        return result
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return f"Error executing tool: {str(e)}"
```

## Next Steps and Enhancements

1. **Add Vector Search**: Implement embeddings for semantic story search
2. **Real-time Updates**: Add streaming responses for long queries
3. **User Authentication**: Implement user sessions and history
4. **Analytics Dashboard**: Create insights from chatbot usage
5. **Multi-language Support**: Add support for different languages
6. **Advanced Filtering**: Implement more sophisticated search filters

This implementation provides a solid foundation for building AI-powered applications with LangChain and your HackerNews data. The modular design makes it easy to extend and customize for your specific needs. 