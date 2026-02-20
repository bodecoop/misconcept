#!/usr/bin/env python3
"""
Simple test script to verify the lecture management API structure
Run this to test basic functionality without full FastAPI dependencies
"""

import os
import sys

def test_structure():
    """Test that the file structure is correct"""
    print("🔍 Testing project structure...")

    # Check if main files exist
    required_files = [
        'app/main.py',
        'app/routers/lectures.py',
        'app/database.py',
        'app/config.py'
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")

    # Check if uploads directory exists
    if os.path.exists('uploads'):
        print("✅ uploads/ directory exists")
    else:
        print("❌ uploads/ directory missing")

    print("\n📋 API Endpoints:")
    print("   Classes:")
    print("     POST /classes/ - Create a new class")
    print("     GET  /classes/ - Get all classes")
    print("     GET  /classes/{id} - Get specific class")
    print("   Lectures:")
    print("     POST /lectures/upload - Upload lecture with files")
    print("     GET  /lectures/ - Get all lectures")
    print("     GET  /lectures/{id} - Get specific lecture")

def test_database_connection():
    """Test database connection if possible"""
    print("\n🗄️  Testing database connection...")
    try:
        # Try to import database module
        sys.path.append('.')
        from app.database import get_connection
        print("✅ Database module imports successfully")

        # Try to get a connection
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM dual")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful")
            else:
                print("❌ Database query failed")

    except ImportError as e:
        print(f"❌ Cannot import database module: {e}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_structure()
    test_database_connection()

    print("\n🚀 To run the full API:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Create database schema: Run create_new_schema.sql in your Oracle database")
    print("3. Start server: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("4. Create a class: curl -X POST 'http://localhost:8000/classes/' -H 'Content-Type: application/json' -d '{\"class_name\": \"Computer Science 101\"}'")
    print("5. Test upload: curl -X POST 'http://localhost:8000/lectures/upload' -F 'class_id=1' -F 'lecture_title=Intro' -F 'lecture_date=2024-01-01'")
    print("6. Test get lectures: curl http://localhost:8000/lectures/")