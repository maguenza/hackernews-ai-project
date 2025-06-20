# HackerNews AI Project

A personal project to build a HackerNews AI tool that analyzes and interacts with HackerNews data using LangChain and PostgreSQL.

## Project Structure

```
hackernews-ai-project/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── extractor.py      # HackerNews API data extraction
│   │   ├── loader.py         # PostgreSQL data loading
│   │   └── transformer.py    # Data transformation logic
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemy models
│   │   └── connection.py     # Database connection management
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── langchain_setup.py # LangChain configuration
│   │   ├── tools.py          # Custom LangChain tools
│   │   └── chatbot.py        # Chatbot implementation
│   └── api/
│       ├── __init__.py
│       └── routes.py         # FastAPI endpoints
├── tests/
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_loader.py
│   ├── test_transformer.py
│   └── test_chatbot.py
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration settings
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml              # Render deployment configuration
├── test_chatbot.py          # Chatbot test script
└── LANGCHAIN_GUIDE.md       # Comprehensive LangChain guide
```

## Features

### 🤖 AI-Powered Chatbot
- **LangChain Integration**: Built with LangChain framework for LLM interactions
- **Custom Tools**: Specialized tools for HackerNews data queries
- **Conversation Memory**: Maintains chat history and context
- **Natural Language Processing**: Understands and responds to natural language queries

### 📊 Data Analysis Capabilities
- **Story Search**: Find stories by keywords, topics, or time periods
- **Job Search**: Search job postings with location, type, and company filters
- **User Analytics**: Get user information, karma scores, and activity
- **Trending Topics**: Analyze popular topics and discussions
- **Top Stories**: Retrieve highest-scoring stories by time period

### 🛠️ Technical Features
- **PostgreSQL Integration**: Robust database storage and querying
- **FastAPI Web Interface**: RESTful API with automatic documentation
- **Comprehensive Testing**: Unit and integration tests
- **Error Handling**: Graceful error management and logging
- **Health Monitoring**: System health checks and diagnostics

## Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Set Environment Variables**
```bash
export OPENAI_API_KEY="your_openai_api_key"
export DATABASE_URL="postgresql://user:password@host:port/dbname"
export HACKERNEWS_API_URL="https://hacker-news.firebaseio.com/v0"
```

### 3. **Run Data Pipeline**
```bash
python run.py
```

### 4. **Test the Chatbot**
```bash
python test_chatbot.py
```

### 5. **Start the API Server**
```bash
uvicorn src.api.routes:app --reload
```

## Usage Examples

### Basic Chatbot Usage
```python
from src.ai.chatbot import HackerNewsChatbot

# Initialize chatbot
chatbot = HackerNewsChatbot()

# Ask questions
response = chatbot.chat("What are the top stories from the last week?")
print(response)

# Search for specific topics
response = chatbot.chat("Find stories about artificial intelligence")
print(response)

# Look for jobs
response = chatbot.chat("Find remote Python developer jobs")
print(response)
```

### Direct Tool Usage
```python
# Search stories
result = chatbot.direct_tool_call("search_stories", query="python", limit=5)

# Find jobs
result = chatbot.direct_tool_call("search_jobs", query="developer", location="remote")

# Get user info
result = chatbot.direct_tool_call("get_user_info", username="pg")
```

### API Usage
```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are the top stories?"}'

# Get system information
curl "http://localhost:8000/system/info"

# Get suggested queries
curl "http://localhost:8000/suggestions"
```

## LangChain Implementation

This project uses **LangChain** to create an intelligent chatbot that can:

### 🔧 **Custom Tools**
- **SearchStoriesTool**: Query stories by keywords and filters
- **SearchJobsTool**: Find job postings with multiple criteria
- **GetTopStoriesTool**: Retrieve top stories by score
- **GetUserInfoTool**: Get user information and activity
- **GetTrendingTopicsTool**: Analyze trending topics

### 🧠 **Agent Architecture**
- **Intelligent Routing**: Automatically chooses appropriate tools
- **Multi-step Reasoning**: Can combine multiple tools for complex queries
- **Natural Language Understanding**: Processes conversational queries
- **Context Awareness**: Maintains conversation history

### 💾 **Memory Management**
- **Conversation Buffer**: Stores chat history
- **Context Preservation**: Maintains context across interactions
- **Memory Clearing**: Option to reset conversation state

For detailed information about the LangChain implementation, see [LANGCHAIN_GUIDE.md](LANGCHAIN_GUIDE.md).

## Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Tests
```bash
# Chatbot tests
pytest tests/test_chatbot.py

# With coverage
pytest --cov=src tests/
```

### Manual Testing
```bash
# Test chatbot functionality
python test_chatbot.py

# Test API endpoints
curl "http://localhost:8000/health"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | System health check |
| `/chat` | POST | Send message to chatbot |
| `/system/info` | GET | Get system information |
| `/suggestions` | GET | Get suggested queries |
| `/tools` | GET | List available tools |
| `/tools/{tool_name}` | POST | Call specific tool directly |
| `/chat/clear` | POST | Clear chat history |

## Database Schema

The project uses PostgreSQL with the following main tables:

- **users**: HackerNews user information
- **stories**: Story posts with metadata
- **comments**: User comments on stories
- **jobs**: Job posting information

See `src/database/models.py` for complete schema details.

## Deployment

### Render Deployment
The project includes `render.yaml` for easy deployment on Render:

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically on push to main branch

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=your_openai_api_key
HACKERNEWS_API_URL=https://hacker-news.firebaseio.com/v0
```

## Development

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/
```

### Adding New Tools
1. Create a new tool class in `src/ai/tools.py`
2. Inherit from `BaseTool`
3. Define input schema with Pydantic
4. Implement `_run` method
5. Add to `HackerNewsTools` class
6. Write tests in `tests/test_chatbot.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License

## Support

For questions about the LangChain implementation or general usage, please refer to:
- [LANGCHAIN_GUIDE.md](LANGCHAIN_GUIDE.md) - Comprehensive LangChain guide
- [LangChain Documentation](https://python.langchain.com/) - Official LangChain docs
- [OpenAI API Documentation](https://platform.openai.com/docs) - OpenAI API reference
