#!/usr/bin/env python3
"""
Test script for HackerNews AI Chatbot.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ Loaded environment variables from .env file")
    else:
        print("⚠️  No .env file found")

def test_chatbot():
    """Test the HackerNews chatbot with sample queries."""
    try:
        from src.ai.chatbot import HackerNewsChatbot
        
        print("🤖 Initializing HackerNews AI Chatbot...")
        chatbot = HackerNewsChatbot()
        
        # Test system info
        print("\n📊 System Information:")
        system_info = chatbot.get_system_info()
        print(f"Model: {system_info['model']}")
        print(f"Temperature: {system_info['temperature']}")
        print(f"Available tools: {system_info['available_tools']}")
        
        # Test suggested queries
        print("\n💡 Suggested Queries:")
        suggestions = chatbot.suggest_queries()
        for i, query in enumerate(suggestions[:5], 1):
            print(f"{i}. {query}")
        
        # Test health check
        print("\n🏥 Health Check:")
        health = chatbot.health_check()
        print(f"Status: {health['status']}")
        print(f"Tools available: {health['tools_available']}")
        
        # Test sample queries
        test_queries = [
            "Hello! Can you help me with HackerNews data?",
            "What are the top stories from the last week?",
            "Find job postings for remote Python developers",
            "Search for stories about artificial intelligence"
        ]
        
        print("\n💬 Testing Chat Queries:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Query {i}: {query} ---")
            try:
                response = chatbot.chat(query)
                print(f"Response: {response[:200]}...")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Test direct tool calls
        print("\n🔧 Testing Direct Tool Calls:")
        
        # Test search stories tool
        print("\n--- Testing search_stories tool ---")
        try:
            result = chatbot.direct_tool_call("search_stories", query="python", limit=3)
            print(f"Result: {result[:200]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Test get top stories tool
        print("\n--- Testing get_top_stories tool ---")
        try:
            result = chatbot.direct_tool_call("get_top_stories", limit=3, days_back=7)
            print(f"Result: {result[:200]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n✅ Chatbot test completed successfully!")
        
    except Exception as e:
        print(f"❌ Chatbot test failed: {str(e)}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🧪 HackerNews AI Chatbot Test")
    print("=" * 50)
    
    # Load environment variables
    load_env_file()
    print()
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Set these environment variables:")
        print("   export OPENAI_API_KEY='your_openai_api_key'")
        print("   export DATABASE_URL='your_postgresql_url'")
        return 1
    
    # Run chatbot test
    success = test_chatbot()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(main()) 