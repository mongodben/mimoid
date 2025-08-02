"""
DocuSign MongoDB Database Execution Script

This script orchestrates the creation and seeding of the DocuSign MongoDB database,
including pre-checks, index creation, data seeding, validation, and reporting.
"""

import os
import sys
import logging
import time
from datetime import datetime
from typing import Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db_schema import DocuSignMongoDbSchema
from seed_db import DocuSignDatabaseSeeder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'docusign_db_seed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocuSignDatabaseManager:
    """Manages DocuSign database creation and seeding"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017"
        )
        self.schema = DocuSignMongoDbSchema()
        self.client = None
        self.db = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            # Log connection info (hide password)
            safe_uri = self.connection_string
            if '@' in safe_uri and 'mongodb' in safe_uri:
                # Hide password in connection string for logging
                parts = safe_uri.split('@')
                creds_part = parts[0].split('://')[-1]
                if ':' in creds_part:
                    user = creds_part.split(':')[0]
                    safe_uri = f"mongodb+srv://{user}:****@{parts[1]}"
            
            logger.info(f"Connecting to MongoDB at {safe_uri}...")
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.schema.database_name]
            logger.info(f"Successfully connected to database: {self.schema.database_name}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        logger.info("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required")
            return False
        
        # Check MongoDB connection
        if not self.connect():
            return False
        
        # Check if database already exists
        if self.schema.database_name in self.client.list_database_names():
            logger.warning(f"Database '{self.schema.database_name}' already exists")
            # In non-interactive mode, drop and recreate
            logger.info(f"Dropping existing database '{self.schema.database_name}'...")
            self.client.drop_database(self.schema.database_name)
        
        return True
    
    def create_indexes(self) -> bool:
        """Create collection indexes"""
        logger.info("Creating indexes...")
        
        try:
            for collection_name, collection_schema in self.schema.collections.items():
                logger.info(f"Creating indexes for collection: {collection_name}")
                
                # Get collection
                mongo_collection = self.db[collection_name]
                
                # Create indexes
                for index in collection_schema.indexes:
                    try:
                        # Convert keys dictionary to list of tuples
                        index_spec = []
                        for field, direction in index.keys.items():
                            if isinstance(direction, str):
                                # Text index
                                index_spec.append((field, direction))
                            else:
                                # Regular index with direction
                                index_spec.append((field, direction))
                        
                        index_options = {}
                        
                        if index.unique:
                            index_options['unique'] = True
                        if index.sparse:
                            index_options['sparse'] = True
                        if index.name:
                            index_options['name'] = index.name
                        
                        mongo_collection.create_index(index_spec, **index_options)
                        logger.debug(f"Created index: {index_spec}")
                        
                    except OperationFailure as e:
                        if "already exists" in str(e):
                            logger.debug(f"Index already exists: {index_spec}")
                        else:
                            logger.error(f"Failed to create index {index_spec}: {e}")
                            return False
            
            logger.info("All indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def seed_database(self) -> Dict[str, int]:
        """Seed the database with sample data"""
        logger.info("Starting database seeding...")
        
        try:
            # Initialize collections in schema
            for collection_name in self.schema.collections:
                collection = self.db[collection_name]
            
            # Create seeder and seed data
            seeder = DocuSignDatabaseSeeder(self.connection_string, self.schema)
            result = seeder.seed_all()
            
            logger.info("Database seeding completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            raise
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate seeded data"""
        logger.info("Validating seeded data...")
        
        validation_results = {
            "collections": {},
            "relationships": {},
            "data_quality": {},
            "issues": []
        }
        
        try:
            # Validate collection counts
            for collection_name in self.schema.collections:
                count = self.db[collection_name].count_documents({})
                validation_results["collections"][collection_name] = count
                
                if count == 0 and collection_name not in ["audit_events"]:
                    validation_results["issues"].append(
                        f"Collection '{collection_name}' is empty"
                    )
            
            # Validate relationships
            logger.info("Validating relationships...")
            
            # Check envelope-document relationships
            orphan_docs = self.db.documents.count_documents({
                "envelope_id": {"$nin": list(self.db.envelopes.distinct("_id"))}
            })
            if orphan_docs > 0:
                validation_results["issues"].append(
                    f"Found {orphan_docs} orphaned documents"
                )
            
            # Check envelope-recipient relationships
            orphan_recipients = self.db.recipients.count_documents({
                "envelope_id": {"$nin": list(self.db.envelopes.distinct("_id"))}
            })
            if orphan_recipients > 0:
                validation_results["issues"].append(
                    f"Found {orphan_recipients} orphaned recipients"
                )
            
            # Check user-account relationships
            orphan_users = self.db.users.count_documents({
                "account_id": {"$nin": list(self.db.accounts.distinct("_id"))}
            })
            if orphan_users > 0:
                validation_results["issues"].append(
                    f"Found {orphan_users} orphaned users"
                )
            
            validation_results["relationships"] = {
                "orphan_documents": orphan_docs,
                "orphan_recipients": orphan_recipients,
                "orphan_users": orphan_users
            }
            
            # Data quality checks
            logger.info("Checking data quality...")
            
            # Check envelope status distribution
            status_dist = list(self.db.envelopes.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            validation_results["data_quality"]["envelope_status_distribution"] = status_dist
            
            # Check average recipients per envelope
            avg_recipients = list(self.db.envelopes.aggregate([
                {"$group": {"_id": None, "avg_recipients": {"$avg": "$recipient_count"}}}
            ]))
            if avg_recipients:
                validation_results["data_quality"]["avg_recipients_per_envelope"] = avg_recipients[0]["avg_recipients"]
            
            # Check template usage
            template_usage = self.db.envelopes.count_documents({"template_id": {"$ne": None}})
            total_envelopes = self.db.envelopes.count_documents({})
            if total_envelopes > 0:
                validation_results["data_quality"]["template_usage_percentage"] = (template_usage / total_envelopes) * 100
            
            logger.info(f"Validation completed. Found {len(validation_results['issues'])} issues")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            validation_results["issues"].append(f"Validation error: {str(e)}")
            return validation_results
    
    def generate_report(self, seed_result: Dict[str, int], validation_result: Dict[str, Any]):
        """Generate summary report"""
        logger.info("Generating summary report...")
        
        print("\n" + "="*60)
        print("DocuSign MongoDB Database Seeding Report")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {self.schema.database_name}")
        
        # Show connection info (hide password)
        safe_uri = self.connection_string
        if '@' in safe_uri and 'mongodb' in safe_uri:
            parts = safe_uri.split('@')
            creds_part = parts[0].split('://')[-1]
            if ':' in creds_part:
                user = creds_part.split(':')[0]
                safe_uri = f"mongodb+srv://{user}:****@{parts[1]}"
        print(f"Connection: {safe_uri}")
        print("\n")
        
        print("Collection Summary:")
        print("-"*40)
        for collection, count in seed_result.items():
            print(f"{collection:20} {count:>10,} documents")
        print(f"{'Total':20} {sum(seed_result.values()):>10,} documents")
        print("\n")
        
        print("Data Quality Metrics:")
        print("-"*40)
        if "envelope_status_distribution" in validation_result["data_quality"]:
            print("Envelope Status Distribution:")
            for status in validation_result["data_quality"]["envelope_status_distribution"]:
                percentage = (status["count"] / seed_result.get("envelopes", 1)) * 100
                print(f"  {status['_id']:20} {status['count']:>6,} ({percentage:>5.1f}%)")
        
        if "avg_recipients_per_envelope" in validation_result["data_quality"]:
            print(f"\nAverage Recipients per Envelope: {validation_result['data_quality']['avg_recipients_per_envelope']:.1f}")
        
        if "template_usage_percentage" in validation_result["data_quality"]:
            print(f"Template Usage: {validation_result['data_quality']['template_usage_percentage']:.1f}%")
        
        print("\n")
        
        if validation_result["issues"]:
            print("Issues Found:")
            print("-"*40)
            for issue in validation_result["issues"]:
                print(f"⚠️  {issue}")
        else:
            print("✅ No issues found - all validations passed!")
        
        print("\n")
        print("Next Steps:")
        print("-"*40)
        print("1. Review the generated data in MongoDB")
        print("2. Run application tests against the seeded database")
        print("3. Adjust seeding parameters if needed")
        print("4. Check the log file for detailed information")
        print("\n" + "="*60)
    
    def cleanup(self):
        """Clean up resources"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    def run(self):
        """Main execution flow"""
        start_time = time.time()
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites check failed")
                return False
            
            # Create indexes
            if not self.create_indexes():
                logger.error("Index creation failed")
                return False
            
            # Seed database
            seed_result = self.seed_database()
            
            # Validate data
            validation_result = self.validate_data()
            
            # Generate report
            self.generate_report(seed_result, validation_result)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Total execution time: {elapsed_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return False
        finally:
            self.cleanup()


def main():
    """Entry point"""
    manager = DocuSignDatabaseManager()
    success = manager.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()