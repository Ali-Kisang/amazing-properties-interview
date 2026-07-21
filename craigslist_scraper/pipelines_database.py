"""
Database storage pipelines for PostgreSQL, MySQL, and MongoDB
"""
from scrapy.exceptions import DropItem
from loguru import logger
from config.database import DatabaseConfig
from datetime import datetime
import json

class PostgreSQLPipeline:
    """Store items in PostgreSQL"""

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.table_name = 'listings'
        self.config = DatabaseConfig()

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        """Connect to PostgreSQL when spider opens"""
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=self.config.PG_HOST,
                port=self.config.PG_PORT,
                database=self.config.PG_DATABASE,
                user=self.config.PG_USER,
                password=self.config.PG_PASSWORD
            )
            self.cursor = self.connection.cursor()

            # Create table if it doesn't exist
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    unique_id VARCHAR(32) UNIQUE,
                    title TEXT,
                    price INTEGER,
                    address TEXT,
                    bedrooms INTEGER,
                    bathrooms FLOAT,
                    square_feet INTEGER,
                    listing_url TEXT,
                    description TEXT,
                    posted_date TIMESTAMP,
                    city VARCHAR(50),
                    listing_id VARCHAR(50),
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # In case the table already existed from a previous run without
            # this column, add it if missing so ON CONFLICT UPDATE doesn't fail.
            self.cursor.execute(f"""
                ALTER TABLE {self.table_name}
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            self.connection.commit()
            logger.info(f" PostgreSQL connected. Table '{self.table_name}' ready.")

        except ImportError:
            logger.warning(" psycopg2 not installed. PostgreSQL storage disabled.")
            logger.info("Install with: pip install psycopg2-binary")
        except Exception as e:
            logger.error(f" PostgreSQL connection failed: {e}")

    def process_item(self, item, spider):
        """Insert item into PostgreSQL"""
        if self.connection is None or self.cursor is None:
            return item

        try:
            # Convert posted_date to timestamp if present
            posted_date = item.get('posted_date')
            if posted_date:
                try:
                    from dateutil.parser import parse
                    posted_date = parse(posted_date)
                except Exception:
                    posted_date = None

            # Insert or update
            self.cursor.execute(f"""
                INSERT INTO {self.table_name} (
                    unique_id, title, price, address, bedrooms, bathrooms,
                    square_feet, listing_url, description, posted_date, city, listing_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (unique_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    price = EXCLUDED.price,
                    address = EXCLUDED.address,
                    bedrooms = EXCLUDED.bedrooms,
                    bathrooms = EXCLUDED.bathrooms,
                    square_feet = EXCLUDED.square_feet,
                    description = EXCLUDED.description,
                    posted_date = EXCLUDED.posted_date,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                item.get('unique_id'),
                item.get('title'),
                item.get('price'),
                item.get('address'),
                item.get('bedrooms'),
                item.get('bathrooms'),
                item.get('square_feet'),
                item.get('listing_url'),
                item.get('description'),
                posted_date,
                item.get('city'),
                item.get('listing_id')
            ))
            self.connection.commit()

        except Exception as e:
            logger.error(f" PostgreSQL insert failed: {e}")
            self.connection.rollback()

        return item

    def close_spider(self, spider):
        """Close PostgreSQL connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info(" PostgreSQL connection closed.")


class MySQLPipeline:
    """Store items in MySQL"""

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.table_name = 'listings'
        self.config = DatabaseConfig()

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        """Connect to MySQL when spider opens"""
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=self.config.MYSQL_HOST,
                port=self.config.MYSQL_PORT,
                database=self.config.MYSQL_DATABASE,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                charset='utf8mb4'
            )
            self.cursor = self.connection.cursor()

            # Create table if it doesn't exist
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    unique_id VARCHAR(32) UNIQUE,
                    title TEXT,
                    price INT,
                    address TEXT,
                    bedrooms INT,
                    bathrooms DECIMAL(3,1),
                    square_feet INT,
                    listing_url TEXT,
                    description TEXT,
                    posted_date DATETIME,
                    city VARCHAR(50),
                    listing_id VARCHAR(50),
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_unique_id (unique_id),
                    INDEX idx_city (city)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            self.connection.commit()
            logger.info(f" MySQL connected. Table '{self.table_name}' ready.")

        except ImportError:
            logger.warning(" pymysql not installed. MySQL storage disabled.")
            logger.info("Install with: pip install pymysql")
        except Exception as e:
            logger.error(f" MySQL connection failed: {e}")

    def process_item(self, item, spider):
        """Insert item into MySQL"""
        if self.connection is None or self.cursor is None:
            return item

        try:
            # Convert posted_date
            posted_date = item.get('posted_date')
            if posted_date:
                try:
                    from dateutil.parser import parse
                    posted_date = parse(posted_date).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    posted_date = None

            # Insert or update
            self.cursor.execute(f"""
                INSERT INTO {self.table_name} (
                    unique_id, title, price, address, bedrooms, bathrooms,
                    square_feet, listing_url, description, posted_date, city, listing_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    price = VALUES(price),
                    address = VALUES(address),
                    bedrooms = VALUES(bedrooms),
                    bathrooms = VALUES(bathrooms),
                    square_feet = VALUES(square_feet),
                    description = VALUES(description),
                    posted_date = VALUES(posted_date),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                item.get('unique_id'),
                item.get('title'),
                item.get('price'),
                item.get('address'),
                item.get('bedrooms'),
                item.get('bathrooms'),
                item.get('square_feet'),
                item.get('listing_url'),
                item.get('description'),
                posted_date,
                item.get('city'),
                item.get('listing_id')
            ))
            self.connection.commit()

        except Exception as e:
            logger.error(f" MySQL insert failed: {e}")
            self.connection.rollback()

        return item

    def close_spider(self, spider):
        """Close MySQL connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info(" MySQL connection closed.")


class MongoDBPipeline:
    """Store items in MongoDB"""

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.config = DatabaseConfig()

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        """Connect to MongoDB when spider opens"""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(
                host=self.config.MONGO_HOST,
                port=self.config.MONGO_PORT
            )
            self.db = self.client[self.config.MONGO_DATABASE]
            self.collection = self.db['listings']

            # Create index on unique_id for deduplication
            self.collection.create_index('unique_id', unique=True)
            self.collection.create_index('city')
            self.collection.create_index('price')

            logger.info(f" MongoDB connected. Database: '{self.config.MONGO_DATABASE}', Collection: 'listings'")

        except ImportError:
            logger.warning(" pymongo not installed. MongoDB storage disabled.")
            logger.info("Install with: pip install pymongo")
        except Exception as e:
            logger.error(f" MongoDB connection failed: {e}")

    def process_item(self, item, spider):
        """Insert item into MongoDB"""
        if self.collection is None:
            return item

        try:
            # Convert to dict and clean
            item_dict = dict(item)

            # Handle posted_date
            if item_dict.get('posted_date'):
                try:
                    from dateutil.parser import parse
                    item_dict['posted_date'] = parse(item_dict['posted_date'])
                except Exception:
                    pass

            # Add timestamps
            item_dict['scraped_at'] = datetime.now()

            # Upsert (update if exists, insert if not)
            self.collection.update_one(
                {'unique_id': item_dict.get('unique_id')},
                {'$set': item_dict},
                upsert=True
            )

        except Exception as e:
            logger.error(f" MongoDB insert failed: {e}")

        return item

    def close_spider(self, spider):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info(" MongoDB connection closed.")


class ETLPipeline:
    """
    ETL Pipeline - demonstrates Extract, Transform, Load workflow

    This pipeline shows how data flows through the system:
    - Extract: Data comes from the spider
    - Transform: Data is cleaned and validated
    - Load: Data is loaded to database(s)
    """

    def __init__(self):
        self.stats = {
            'extracted': 0,
            'transformed': 0,
            'loaded': 0,
            'errors': 0
        }
        self.start_time = datetime.now()

    def open_spider(self, spider):
        logger.info("=" * 60)
        logger.info(" ETL PIPELINE STARTED")
        logger.info("=" * 60)
        logger.info(" Extract: Receiving data from spider")
        logger.info(" Transform: Cleaning and validating")
        logger.info(" Load: Storing to database(s)")
        logger.info("=" * 60)

    def process_item(self, item, spider):
        """Process item through ETL pipeline"""
        self.stats['extracted'] += 1
        self.stats['transformed'] += 1

        return item

    def close_spider(self, spider):
        """Log ETL statistics"""
        duration = (datetime.now() - self.start_time).total_seconds()

        logger.info("=" * 60)
        logger.info(" ETL PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f" Items Extracted: {self.stats['extracted']}")
        logger.info(f" Items Transformed: {self.stats['transformed']}")
        logger.info(f" Items Loaded: {self.stats['loaded']}")
        logger.info(f" Errors: {self.stats['errors']}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info("=" * 60)