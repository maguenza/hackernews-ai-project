#!/bin/bash

# Setup script for local development environment variables

echo "Setting up environment variables for HackerNews AI project..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:password@host:port/database_name

# HackerNews API Configuration
HACKERNEWS_API_URL=https://hacker-news.firebaseio.com/v0

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env file with placeholder values"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "📝 Next steps:"
echo "1. Update the .env file with your actual values:"
echo "   - DATABASE_URL: Your Railway PostgreSQL connection string"
echo "   - OPENAI_API_KEY: Your OpenAI API key"
echo ""
echo "2. Source the environment variables:"
echo "   source .env"
echo ""
echo "3. Test the setup:"
echo "   python scripts/test_etl.py"
echo ""
echo "4. For GitHub Actions, add these as secrets in your repository settings" 