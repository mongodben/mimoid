"""
Script to create indexes for Brazilian Edtech Database without seeding data
"""

import os
import sys
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Add parent directory to path for mimoid imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db_schema import BrazilianEdtechSchema
from seed_db import BrazilianEdtechSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_mongodb_connection(uri: str) -> bool:
    """Check if MongoDB is accessible"""
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error connecting to MongoDB: {e}")
        return False


def main():
    """Create indexes for the Brazilian Edtech database"""
    # Load environment variables from .env file
    load_dotenv()
    
    start_time = datetime.now()
    
    logger.info("Starting Brazilian Edtech Database Index Creation")
    logger.info(f"Timestamp: {start_time}")
    
    # Get MongoDB URI from environment
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    logger.info(f"MongoDB URI: {mongodb_uri.split('@')[-1] if '@' in mongodb_uri else mongodb_uri}")
    
    # Pre-checks
    logger.info("\nRunning pre-checks...")
    if not check_mongodb_connection(mongodb_uri):
        logger.error("Cannot proceed without MongoDB connection")
        sys.exit(1)
    
    try:
        # Initialize schema
        logger.info("\nInitializing database schema...")
        schema = BrazilianEdtechSchema()
        
        # Initialize seeder (we'll only use its create_indexes method)
        logger.info("Initializing database seeder...")
        seeder = BrazilianEdtechSeeder(mongodb_uri, schema)
        
        # Create indexes
        logger.info("\nCreating indexes...")
        seeder.create_indexes()
        
        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n✓ Index creation completed successfully!")
        logger.info(f"Total execution time: {duration:.2f} seconds")
        
    except Exception as e:
        logger.error(f"\n✗ Error during index creation: {e}")
        logger.exception("Full error trace:")
        sys.exit(1)


if __name__ == "__main__":
    main()