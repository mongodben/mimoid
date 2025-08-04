"""
Main execution script for Brazilian Edtech Database
Handles pre-checks, seeding, validation, and reporting
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'seeding_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
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


def generate_summary_report(seeder: BrazilianEdtechSeeder):
    """Generate a summary report of the seeded data"""
    logger.info("\n" + "="*50)
    logger.info("DATABASE SEEDING SUMMARY")
    logger.info("="*50)
    
    db = seeder.db
    total_documents = 0
    
    # Collection statistics
    logger.info("\nCollection Statistics:")
    for collection_name in seeder.database_schema.collections.keys():
        count = db[collection_name].count_documents({})
        total_documents += count
        logger.info(f"  - {collection_name}: {count:,} documents")
    
    logger.info(f"\nTotal Documents: {total_documents:,}")
    
    # Sample data insights
    logger.info("\nSample Data Insights:")
    
    # User distribution
    user_counts = {}
    for role in ['student', 'staff', 'admin']:
        count = db.users.count_documents({'role': role})
        user_counts[role] = count
    logger.info(f"  - User Distribution: {user_counts}")
    
    # Application status distribution
    pipeline = [
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    status_dist = list(db.applications.aggregate(pipeline))
    if status_dist:
        logger.info("  - Application Status Distribution:")
        for item in status_dist:
            logger.info(f"    • {item['_id']}: {item['count']:,}")
    
    # Institution statistics
    institution_count = db.institutions.count_documents({})
    active_institutions = db.institutions.count_documents({'is_active': True})
    logger.info(f"  - Institutions: {institution_count} total ({active_institutions} active)")
    
    # Funding program statistics
    funding_count = db.funding_programs.count_documents({})
    active_funding = db.funding_programs.count_documents({'is_active': True})
    logger.info(f"  - Funding Programs: {funding_count} total ({active_funding} active)")
    
    logger.info("\n" + "="*50)


def main():
    """Main execution function"""
    # Load environment variables from .env file
    load_dotenv()
    
    start_time = datetime.now()
    
    logger.info("Starting Brazilian Edtech Database Setup")
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
        
        # Initialize seeder
        logger.info("Initializing database seeder...")
        seeder = BrazilianEdtechSeeder(mongodb_uri, schema)
        
        # Clear existing data
        logger.info("\nClearing existing data...")
        seeder.clear_database()
        
        # Seed collections
        logger.info("\nSeeding collections...")
        seeder.seed_all_collections()
        
        # Create indexes
        logger.info("\nCreating indexes...")
        seeder.create_indexes()
        
        # Validate data
        logger.info("\nValidating seeded data...")
        seeder.validate_seed_data()
        
        # Generate summary report
        generate_summary_report(seeder)
        
        # Calculate execution time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n✓ Database seeding completed successfully!")
        logger.info(f"Total execution time: {duration:.2f} seconds")
        
    except Exception as e:
        logger.error(f"\n✗ Error during database seeding: {e}")
        logger.exception("Full error trace:")
        sys.exit(1)


if __name__ == "__main__":
    main()