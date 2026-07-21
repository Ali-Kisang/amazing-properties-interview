
"""
Database setup script for PostgreSQL, MySQL, and MongoDB
"""
import os
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

def setup_postgresql():
    """Set up PostgreSQL database"""
    try:
        import psycopg2
        from config.database import DatabaseConfig
        
        conn = psycopg2.connect(
            host=DatabaseConfig.PG_HOST,
            port=DatabaseConfig.PG_PORT,
            user=DatabaseConfig.PG_USER,
            password=DatabaseConfig.PG_PASSWORD,
            database='postgres' 
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DatabaseConfig.PG_DATABASE}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DatabaseConfig.PG_DATABASE}")
            logger.info(f" PostgreSQL database '{DatabaseConfig.PG_DATABASE}' created")
        else:
            logger.info(f" PostgreSQL database '{DatabaseConfig.PG_DATABASE}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        logger.warning(" psycopg2 not installed. PostgreSQL setup skipped.")
        return False
    except Exception as e:
        logger.error(f"Failed PostgreSQL setup failed: {e}")
        return False

def setup_mysql():
    """Set up MySQL database"""
    try:
        import pymysql
        from config.database import DatabaseConfig
        
        conn = pymysql.connect(
            host=DatabaseConfig.MYSQL_HOST,
            port=DatabaseConfig.MYSQL_PORT,
            user=DatabaseConfig.MYSQL_USER,
            password=DatabaseConfig.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DatabaseConfig.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        logger.info(f" MySQL database '{DatabaseConfig.MYSQL_DATABASE}' ready")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        logger.warning(" pymysql not installed. MySQL setup skipped.")
        return False
    except Exception as e:
        logger.error(f"Failed MySQL setup failed: {e}")
        return False

def setup_mongodb():
    """Set up MongoDB"""
    try:
        from pymongo import MongoClient
        from config.database import DatabaseConfig
        
        client = MongoClient(
            host=DatabaseConfig.MONGO_HOST,
            port=DatabaseConfig.MONGO_PORT
        )
        db = client[DatabaseConfig.MONGO_DATABASE]
        # Create a collection by inserting a dummy document and deleting it
        collection = db['listings']
        collection.insert_one({'_temp': True})
        collection.delete_one({'_temp': True})
        logger.info(f" MongoDB database '{DatabaseConfig.MONGO_DATABASE}' ready")
        
        client.close()
        return True
        
    except ImportError:
        logger.warning(" pymongo not installed. MongoDB setup skipped.")
        return False
    except Exception as e:
        logger.error(f"Failed MongoDB setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print(" DATABASE SETUP")
    print("=" * 60)
    
    # Check which databases are enabled
    enable_pg = os.getenv('ENABLE_POSTGRESQL', 'false').lower() == 'true'
    enable_mysql = os.getenv('ENABLE_MYSQL', 'false').lower() == 'true'
    enable_mongo = os.getenv('ENABLE_MONGODB', 'false').lower() == 'true'
    
    results = []
    
    if enable_pg:
        print("\n Setting up PostgreSQL...")
        results.append(("PostgreSQL", setup_postgresql()))
    
    if enable_mysql:
        print("\n Setting up MySQL...")
        results.append(("MySQL", setup_mysql()))
    
    if enable_mongo:
        print("\n Setting up MongoDB...")
        results.append(("MongoDB", setup_mongodb()))
    
    if not any([enable_pg, enable_mysql, enable_mongo]):
        print("\n No databases enabled. Set ENABLE_POSTGRESQL, ENABLE_MYSQL, or ENABLE_MONGODB to true in .env")
    
    print("\n" + "=" * 60)
    print(" SETUP SUMMARY")
    print("=" * 60)
    for name, success in results:
        status = "Success" if success else "Failed"
        print(f"{status} {name}: {'Ready' if success else 'Failed'}")
    print("=" * 60)

if __name__ == "__main__":
    main()