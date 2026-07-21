# config/database.py
"""
Database configuration for PostgreSQL, MySQL, and MongoDB
"""
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from loguru import logger

load_dotenv()

class DatabaseConfig:
    """Database configuration settings"""
    
    # PostgreSQL
    PG_HOST = os.getenv('PG_HOST', 'localhost')
    PG_PORT = int(os.getenv('PG_PORT', 5432))
    PG_DATABASE = os.getenv('PG_DATABASE', 'listings')
    PG_USER = os.getenv('PG_USER', 'postgres')
    PG_PASSWORD = os.getenv('PG_PASSWORD', 'postgres')
    
    # MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'listings')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    
    # MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'listings')
    
    @classmethod
    def get_pg_connection_string(cls):
        """Get PostgreSQL connection string"""
        return f"postgresql://{cls.PG_USER}:{cls.PG_PASSWORD}@{cls.PG_HOST}:{cls.PG_PORT}/{cls.PG_DATABASE}"
    
    @classmethod
    def get_mysql_connection_string(cls):
        """Get MySQL connection string"""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"
    
    @classmethod
    def get_mongo_connection_string(cls):
        """Get MongoDB connection string"""
        return f"mongodb://{cls.MONGO_HOST}:{cls.MONGO_PORT}/"