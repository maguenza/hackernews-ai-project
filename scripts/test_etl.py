#!/usr/bin/env python3
"""
Test script to verify ETL pipeline components work correctly
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded environment variables from .env file")

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from src.data.extractor import HackerNewsExtractor
        from src.data.transformer import DataTransformer
        from src.data.loader import DataLoader
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test that required environment variables are set"""
    required_vars = ['DATABASE_URL', 'HACKERNEWS_API_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Set these environment variables:")
        print("   export DATABASE_URL='your_railway_postgres_url'")
        print("   export HACKERNEWS_API_URL='https://hacker-news.firebaseio.com/v0'")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_database_connection():
    """Test database connection"""
    try:
        from src.database.connection import get_db_connection
        from sqlalchemy import text
        
        with get_db_connection() as db:
            # Test a simple query using text() wrapper
            result = db.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ Database connection successful")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running ETL pipeline tests...\n")
    
    # Load .env file first
    load_env_file()
    print()
    
    tests = [
        test_imports,
        test_environment,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! ETL pipeline should work in GitHub Actions.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before running in GitHub Actions.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 