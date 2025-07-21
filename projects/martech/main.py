"""
Main execution script for DataTech Platform MarTech database
Runs seeding and validation with error handling and iteration support
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Add current directory and parent mimoid directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from seed_db import DataTechPlatformSeeder, seed_database
from db_schema import database_schema


def test_mongodb_connection(connection_string: str) -> bool:
    """Test MongoDB connection before proceeding"""
    try:
        print("Testing MongoDB connection...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        print("✅ MongoDB connection successful")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Unexpected connection error: {e}")
        return False


def validate_schema_import() -> bool:
    """Validate that the database schema can be imported and instantiated"""
    try:
        print("Validating database schema...")
        # Try to access schema properties
        db_name = database_schema.database_name
        collections = list(database_schema.collections.keys())
        print(
            f"✅ Schema validation passed - Database: {db_name}, Collections: {len(collections)}"
        )
        print(f"   Collections: {', '.join(collections)}")
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False


def run_pre_execution_checks(connection_string: str) -> bool:
    """Run all pre-execution validation checks"""
    print("=" * 60)
    print("DATATECH PLATFORM DATABASE SETUP")
    print("=" * 60)

    # Check 1: Schema validation
    if not validate_schema_import():
        return False

    # Check 2: Database connection
    if not test_mongodb_connection(connection_string):
        return False

    print("✅ All pre-execution checks passed!\n")
    return True


def generate_summary_report(connection_string: str):
    """Generate a summary report of the seeded database"""
    try:
        client = MongoClient(connection_string)
        db = client[database_schema.database_name]

        print("\n" + "=" * 50)
        print("DATABASE SUMMARY REPORT")
        print("=" * 50)
        print(f"Database: {database_schema.database_name}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)

        total_documents = 0
        for collection_name in database_schema.collections.keys():
            count = db[collection_name].count_documents({})
            total_documents += count
            print(f"{collection_name:20}: {count:,} documents")

        print("-" * 50)
        print(f"{'Total Documents':20}: {total_documents:,}")

        # Sample some data to show what was generated
        print("\n📊 Sample Data:")
        print("-" * 50)

        # Show sample customer
        sample_customer = db.customers.find_one(
            {},
            {
                "first_name": 1,
                "last_name": 1,
                "email": 1,
                "lifetime_value": 1,
                "engagement_score": 1,
                "tags": 1,
            },
        )
        if sample_customer:
            print(
                f"Sample Customer: {sample_customer.get('first_name')} {sample_customer.get('last_name')}"
            )
            print(f"  Email: {sample_customer.get('email')}")
            print(f"  LTV: ${sample_customer.get('lifetime_value', 0):.2f}")
            print(f"  Engagement: {sample_customer.get('engagement_score', 0):.1f}/100")
            print(f"  Tags: {', '.join(sample_customer.get('tags', []))}")

        # Show recent events
        recent_events = list(db.events.find({}).sort("timestamp", -1).limit(3))
        if recent_events:
            print(f"\n📈 Recent Events:")
            for event in recent_events:
                print(
                    f"  {event['event_type']} - {event['timestamp'].strftime('%Y-%m-%d %H:%M')}"
                )

        # Show campaign performance
        active_campaigns = list(
            db.campaigns.find({"status": "active"}, {"name": 1, "metrics": 1}).limit(3)
        )
        if active_campaigns:
            print(f"\n📢 Active Campaigns:")
            for campaign in active_campaigns:
                metrics = campaign.get("metrics", {})
                if metrics:
                    print(
                        f"  {campaign['name']} - Sent: {metrics.get('sent', 0):,}, Opened: {metrics.get('opened', 0):,}"
                    )

        print("\n🎉 Database ready for use!")

    except Exception as e:
        print(f"❌ Error generating summary report: {e}")


def main():
    """Main execution function"""
    # Configuration
    CONNECTION_STRING = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    # Custom record counts for this run
    RECORD_COUNTS = {
        "data_sources": 8,
        "customers": 1000,
        "campaigns": 25,
        "events": 50000,
        "segments": 15,
        "social_members": 300,
    }

    print("Starting DataTech Platform database setup...")

    # Step 1: Pre-execution validation
    if not run_pre_execution_checks(CONNECTION_STRING):
        print("\n❌ Pre-execution checks failed. Please fix issues and try again.")
        sys.exit(1)

    # Step 2: Execute seeding
    try:
        print("🚀 Starting database seeding process...")
        print(f"Target record counts: {RECORD_COUNTS}")
        print("-" * 50)

        success = seed_database(
            connection_string=CONNECTION_STRING, record_counts=RECORD_COUNTS
        )

        if not success:
            print("\n❌ Database seeding completed with validation errors")
            print("Check the output above for specific issues")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during seeding: {e}")
        print("Please check your MongoDB connection and schema configuration")
        sys.exit(1)

    # Step 3: Generate final report
    generate_summary_report(CONNECTION_STRING)

    print(f"\n💡 Connection string: {CONNECTION_STRING}")
    print(f"💡 Database name: {database_schema.database_name}")
    print("\n✨ Setup complete! Your MarTech database is ready to use.")


if __name__ == "__main__":
    main()
