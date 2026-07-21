#!/usr/bin/env python
"""
Test database connections
Run: python test_db_connection.py
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        print("📦 Testing PostgreSQL...")
        print(f"   Host: {os.getenv('PG_HOST', 'localhost')}:{os.getenv('PG_PORT', '5432')}")
        print(f"   Database: {os.getenv('PG_DATABASE', 'listings')}")
        print(f"   User: {os.getenv('PG_USER', 'postgres')}")
        
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST', 'localhost'),
            port=os.getenv('PG_PORT', '5432'),
            database=os.getenv('PG_DATABASE', 'listings'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"✅ PostgreSQL: Connected - {version[0][:50]}...")
        return True
    except ImportError:
        print("❌ PostgreSQL: psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL: Failed - {e}")
        return False

def test_mysql():
    """Test MySQL connection"""
    try:
        import pymysql
        print("\n📦 Testing MySQL...")
        print(f"   Host: {os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', '3306')}")
        print(f"   Database: {os.getenv('MYSQL_DATABASE', 'listings')}")
        print(f"   User: {os.getenv('MYSQL_USER', 'root')}")
        
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            database=os.getenv('MYSQL_DATABASE', 'listings'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'root'),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"✅ MySQL: Connected - {version[0][:50]}...")
        return True
    except ImportError:
        print("❌ MySQL: pymysql not installed. Run: pip install pymysql")
        return False
    except Exception as e:
        print(f"❌ MySQL: Failed - {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    try:
        from pymongo import MongoClient
        print("\n📦 Testing MongoDB...")
        print(f"   Host: {os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_PORT', '27017')}")
        print(f"   Database: {os.getenv('MONGO_DATABASE', 'listings')}")
        
        client = MongoClient(
            host=os.getenv('MONGO_HOST', 'localhost'),
            port=int(os.getenv('MONGO_PORT', '27017'))
        )
        # Ping to test connection
        client.admin.command('ping')
        db = client[os.getenv('MONGO_DATABASE', 'listings')]
        collections = db.list_collection_names()
        client.close()
        print(f"✅ MongoDB: Connected - Collections: {collections if collections else 'None yet'}")
        return True
    except ImportError:
        print("❌ MongoDB: pymongo not installed. Run: pip install pymongo")
        return False
    except Exception as e:
        print(f"❌ MongoDB: Failed - {e}")
        return False

def main():
    """Test all database connections"""
    print("=" * 60)
    print("🗄️ LOCAL DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Check which databases are enabled
    enable_pg = os.getenv('ENABLE_POSTGRESQL', 'false').lower() == 'true'
    enable_mysql = os.getenv('ENABLE_MYSQL', 'false').lower() == 'true'
    enable_mongo = os.getenv('ENABLE_MONGODB', 'false').lower() == 'true'
    
    print("\n📋 Current Configuration:")
    print(f"   PostgreSQL: {'ENABLED' if enable_pg else 'disabled'}")
    print(f"   MySQL:      {'ENABLED' if enable_mysql else 'disabled'}")
    print(f"   MongoDB:    {'ENABLED' if enable_mongo else 'disabled'}")
    
    if not any([enable_pg, enable_mysql, enable_mongo]):
        print("\n⚠️ No databases enabled!")
        print("Set ENABLE_POSTGRESQL=true, ENABLE_MYSQL=true, or ENABLE_MONGODB=true in .env")
        return
    
    results = []
    
    if enable_pg:
        results.append(("PostgreSQL", test_postgresql()))
    
    if enable_mysql:
        results.append(("MySQL", test_mysql()))
    
    if enable_mongo:
        results.append(("MongoDB", test_mongodb()))
    
    print("\n" + "=" * 60)
    print("📊 CONNECTION SUMMARY")
    print("=" * 60)
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {'Connected' if success else 'Failed'}")
    print("=" * 60)
    
    if all(success for _, success in results):
        print("\n🎉 All databases are connected and ready!")
        print("\nNext steps:")
        print("  1. Run the scraper: python main.py")
        print("  2. Data will be automatically stored in your databases")
    else:
        print("\n⚠️ Some databases failed to connect.")
        print("   Check:")
        print("   - Are the databases running?")
        print("   - Are the credentials correct in .env?")
        print("   - Are the drivers installed? (pip install psycopg2-binary pymysql pymongo)")

if __name__ == "__main__":
    main()