#!/usr/bin/env python3
"""
Main execution script for MetaSteel Industries - Global Product Quality System Database

This script initializes and seeds the steel production quality database with realistic sample data.
It handles pre-checks, seeding, validation, and reporting for the complete database setup.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
except ImportError:
    print("💡 Install python-dotenv to automatically load .env file: pip install python-dotenv")

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except ImportError:
    print("❌ Error: pymongo is required. Install with: pip install pymongo")
    sys.exit(1)

try:
    from seed_db import seed_database, SteelProductionSeeder
    from db_schema import database_schema
except ImportError as e:
    print(f"❌ Error importing project modules: {e}")
    print("Make sure you're running from the correct directory with all required files.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'steel_db_seed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


class DatabaseSetupManager:
    """Manages the complete database setup process"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.client = None
        self.db = None
        self.seeder = None
        
    def run_complete_setup(self, record_counts: Optional[Dict[str, int]] = None):
        """Run the complete database setup process"""
        try:
            print("🔥 MetaSteel Industries - Global Product Quality System")
            print("=" * 60)
            print("Starting database setup process...")
            print()
            
            # Step 1: Pre-flight checks
            self._run_preflight_checks()
            
            # Step 2: Initialize seeder
            self._initialize_seeder()
            
            # Step 3: Seed database
            self._seed_database(record_counts)
            
            # Step 4: Post-seeding validation
            self._run_post_validation()
            
            # Step 5: Generate report
            self._generate_completion_report()
            
            print("✅ Database setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            print(f"❌ Setup failed: {e}")
            if logger.level == logging.DEBUG:
                traceback.print_exc()
            return False
            
        finally:
            if self.client:
                self.client.close()
                
    def _run_preflight_checks(self):
        """Run pre-flight checks before seeding"""
        print("🔍 Running pre-flight checks...")
        
        # Check MongoDB connection
        print("  • Testing MongoDB connection...", end=" ")
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Force connection attempt
            self.client.admin.command('ping')
            self.db = self.client[database_schema.database_name]
            print("✅")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print("❌")
            raise Exception(f"Cannot connect to MongoDB: {e}")
            
        # Check available disk space (if possible)
        print("  • Checking system resources...", end=" ")
        try:
            import shutil
            disk_space = shutil.disk_usage("/")
            free_space_gb = disk_space.free / (1024**3)
            if free_space_gb < 2:  # Need at least 2GB free
                print("⚠️")
                logger.warning(f"Low disk space: {free_space_gb:.1f}GB free")
            else:
                print("✅")
        except Exception:
            print("⚠️ (Could not check disk space)")
            
        # Check database state
        print("  • Checking database state...", end=" ")
        existing_collections = self.db.list_collection_names()
        if existing_collections:
            print(f"⚠️ ({len(existing_collections)} existing collections)")
            logger.info(f"Found existing collections: {existing_collections}")
        else:
            print("✅ (Clean database)")
            
        print("  Pre-flight checks completed\n")
        
    def _initialize_seeder(self):
        """Initialize the database seeder"""
        print("🛠️  Initializing database seeder...")
        
        try:
            self.seeder = SteelProductionSeeder(self.connection_string)
            print("  • Seeder initialized successfully ✅")
            print(f"  • Target database: {database_schema.database_name}")
            print(f"  • Collections to create: {len(database_schema.collections)}")
            print()
            
        except Exception as e:
            raise Exception(f"Failed to initialize seeder: {e}")
            
    def _seed_database(self, record_counts: Optional[Dict[str, int]] = None):
        """Seed the database with sample data"""
        print("🌱 Seeding database with sample data...")
        
        if record_counts is None:
            record_counts = {
                'facilities': 8,
                'production_lines': 40,
                'products': 25,
                'production_batches': 500,
                'quality_checkpoints': 50000,
                'defects': 2500,
                'test_results': 5000,
                'customer_specifications': 15
            }
            
        total_records = sum(record_counts.values())
        print(f"  • Total records to generate: {total_records:,}")
        print("  • Record distribution:")
        for collection, count in record_counts.items():
            print(f"    - {collection}: {count:,}")
        print()
        
        start_time = datetime.now()
        
        # Clear existing data
        print("  🗑️  Clearing existing data...")
        self.seeder.clear_database()
        
        # Seed all collections
        print("  📊 Generating sample data...")
        self.seeder.seed_all_collections(record_counts)
        
        # Create indexes
        print("  🗂️  Creating database indexes...")
        self.seeder.create_indexes()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"  • Seeding completed in {duration.total_seconds():.1f} seconds")
        print(f"  • Average: {total_records / duration.total_seconds():.0f} records/second")
        print()
        
    def _run_post_validation(self):
        """Run post-seeding validation"""
        print("🔍 Running post-seeding validation...")
        
        try:
            self.seeder.validate_seed_data()
            print("  • Data validation passed ✅")
            
        except Exception as e:
            print(f"  • Data validation failed ❌: {e}")
            raise
            
        # Additional validation checks
        print("  • Running additional checks...")
        
        # Check for reasonable data distribution
        batch_count = self.db.production_batches.count_documents({})
        checkpoint_count = self.db.quality_checkpoints.count_documents({})
        if batch_count > 0:
            checkpoints_per_batch = checkpoint_count / batch_count
            print(f"    - Checkpoints per batch: {checkpoints_per_batch:.1f}")
            
        # Check quality scores distribution
        pipeline = [
            {"$group": {"_id": None, "avg_quality": {"$avg": "$overall_quality_score"}}},
            {"$project": {"_id": 0, "avg_quality": 1}}
        ]
        result = list(self.db.production_batches.aggregate(pipeline))
        if result:
            avg_quality = result[0]['avg_quality']
            print(f"    - Average batch quality score: {avg_quality:.1f}")
            
        print("  • Additional checks completed ✅")
        print()
        
    def _generate_completion_report(self):
        """Generate a completion report"""
        print("📋 Database Setup Report")
        print("-" * 40)
        
        # Collection statistics
        print("Collection Statistics:")
        total_documents = 0
        for collection_name in sorted(database_schema.collections.keys()):
            count = self.db[collection_name].count_documents({})
            total_documents += count
            print(f"  • {collection_name:<25} {count:>8,} documents")
            
        print(f"  {'Total':<25} {total_documents:>8,} documents")
        print()
        
        # Database size estimation
        try:
            db_stats = self.db.command("dbstats")
            data_size_mb = db_stats.get('dataSize', 0) / (1024 * 1024)
            storage_size_mb = db_stats.get('storageSize', 0) / (1024 * 1024)
            
            print(f"Database Size:")
            print(f"  • Data size:     {data_size_mb:>8.1f} MB")
            print(f"  • Storage size:  {storage_size_mb:>8.1f} MB")
            print()
        except Exception:
            print("Database size: Unable to determine")
            print()
            
        # Index statistics  
        print("Indexes Created:")
        total_indexes = 0
        for collection_name in sorted(database_schema.collections.keys()):
            indexes = list(self.db[collection_name].list_indexes())
            collection_indexes = len(indexes)
            total_indexes += collection_indexes
            print(f"  • {collection_name:<25} {collection_indexes:>3} indexes")
            
        print(f"  {'Total':<25} {total_indexes:>3} indexes")
        print()
        
        # Sample data preview
        print("Sample Data Preview:")
        
        # Show a sample facility
        facility = self.db.facilities.find_one()
        if facility:
            print(f"  • Sample Facility: {facility.get('facility_name')} ({facility.get('facility_code')})")
            print(f"    Location: {facility.get('city')}, {facility.get('country')}")
            print(f"    Capacity: {facility.get('annual_capacity_tons'):,} tons/year")
            
        # Show a sample product
        product = self.db.products.find_one()
        if product:
            print(f"  • Sample Product: {product.get('product_name')} ({product.get('product_code')})")
            print(f"    Grade: {product.get('grade')}, Type: {product.get('product_type')}")
            
        # Show recent batch
        recent_batch = self.db.production_batches.find_one(sort=[("production_start", -1)])
        if recent_batch:
            print(f"  • Recent Batch: {recent_batch.get('batch_number')}")
            print(f"    Quality Grade: {recent_batch.get('quality_grade')}")
            print(f"    Quantity: {recent_batch.get('actual_quantity_tons'):.1f} tons")
        print()
        
        # Connection information
        print("Connection Information:")
        print(f"  • Database: {database_schema.database_name}")
        print(f"  • Connection: {self.connection_string}")
        print()
        
        # Next steps
        print("Next Steps:")
        print("  1. Connect to MongoDB to explore the data:")
        print(f"     mongo {self.connection_string}/{database_schema.database_name}")
        print()
        print("  2. Query examples:")
        print("     • View facilities: db.facilities.find().pretty()")
        print("     • Check quality metrics: db.production_batches.find({}, {batch_number:1, quality_grade:1, overall_quality_score:1})")
        print("     • Analyze defects: db.defects.aggregate([{$group: {_id: '$defect_type', count: {$sum: 1}}}])")
        print()
        print("  3. Use the data for testing, development, or analysis")
        print()


def main():
    """Main entry point"""
    # Configuration
    connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Custom record counts (can be overridden via environment)
    record_counts = None
    if os.getenv("CUSTOM_RECORD_COUNTS"):
        # Example: CUSTOM_RECORD_COUNTS="facilities=5,products=10,batches=100"
        try:
            pairs = os.getenv("CUSTOM_RECORD_COUNTS").split(",")
            record_counts = {}
            for pair in pairs:
                key, value = pair.split("=")
                record_counts[key.strip()] = int(value.strip())
        except Exception as e:
            print(f"⚠️  Invalid CUSTOM_RECORD_COUNTS format: {e}")
            print("Using default record counts...")
    
    # Enable debug logging if requested
    if os.getenv("DEBUG", "").lower() in ["true", "1", "yes"]:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 Debug logging enabled")
        print()
    
    # Run setup
    manager = DatabaseSetupManager(connection_string)
    success = manager.run_complete_setup(record_counts)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()