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
│   │   └── chatbot.py        # Chatbot implementation
│   └── api/
│       ├── __init__.py
│       └── routes.py         # API endpoints
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
└── render.yaml              # Render deployment configuration
```

## Workflow

1. **Data Extraction**
   - Connect to HackerNews API
   - Extract stories, comments, and user data
   - Implement rate limiting and error handling
   - Store raw data in PostgreSQL

2. **Data Transformation**
   - Clean and normalize data
   - Create derived tables for analysis
   - Implement data quality checks
   - Schedule regular updates

3. **AI Integration**
   - Set up LangChain framework
   - Configure language model
   - Create prompt templates
   - Implement conversation memory

4. **Chatbot Implementation**
   - Build user interface
   - Handle user queries
   - Process natural language
   - Generate responses

5. **Deployment**
   - Configure Render deployment
   - Set up environment variables
   - Implement CI/CD pipeline
   - Monitor application health

## Key Components

### Data Extraction (`src/data/extractor.py`)
- HackerNews API client
- Rate limiting implementation
- Error handling
- Data validation

### Database Models (`src/database/models.py`)
- Story model
- Comment model
- User model
- Analysis tables

### LangChain Setup (`src/ai/langchain_setup.py`)
- Model configuration
- Prompt templates
- Memory management
- Chain construction

### Chatbot (`src/ai/chatbot.py`)
- User interaction handling
- Query processing
- Response generation
- Conversation management

### API Routes (`src/api/routes.py`)
- Health check endpoint
- Data query endpoints
- Chatbot interaction endpoints
- Analytics endpoints

## Testing Strategy

1. **Unit Tests**
   - Data extraction tests
   - Database operation tests
   - AI model tests
   - API endpoint tests

2. **Integration Tests**
   - End-to-end workflow tests
   - Database integration tests
   - API integration tests

3. **Performance Tests**
   - Load testing
   - Response time testing
   - Database query optimization

## Deployment

### Render Configuration
- Web service configuration
- PostgreSQL database setup
- Environment variables
- Build and deploy commands

### Environment Variables
```
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=your_api_key
HACKERNEWS_API_URL=https://hacker-news.firebaseio.com/v0
```

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run tests: `pytest tests/`
5. Start the application: `python src/main.py`

## Dependencies

- Python 3.9+
- PostgreSQL 13+
- LangChain
- FastAPI
- SQLAlchemy
- Pytest
- Docker

## License

MIT License
