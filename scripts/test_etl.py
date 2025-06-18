#!/usr/bin/env python3
"""
Test script to verify ETL pipeline components work correctly
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from data.extractor import HackerNewsExtractor
        from data.transformer import DataTransformer
        from data.loader import DataLoader
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
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_database_connection():
    """Test database connection"""
    try:
        from database.connection import get_database_connection
        conn = get_database_connection()
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running ETL pipeline tests...\n")
    
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