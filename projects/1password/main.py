#!/usr/bin/env python3
"""
1Password Events Database Generator
Main execution script for generating and validating the 1Password events database
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
except ImportError:
    print("💡 Install python-dotenv to automatically load .env file: pip install python-dotenv")

from seed_db import OnePasswordSeeder

def check_mongodb_connection(connection_string: str) -> bool:
    """Check if MongoDB is accessible"""
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        client.close()
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def print_validation_results(results: Dict[str, Any]) -> None:
    """Print validation results in a formatted way"""
    print("\n" + "="*60)
    print("DATABASE VALIDATION RESULTS")
    print("="*60)
    
    print("\n📊 Collection Counts:")
    print("-" * 40)
    for collection_name, stats in results.items():
        if isinstance(stats, dict) and 'count' in stats:
            status = stats['status']
            count = stats['count']
            expected = stats.get('expected_min', 0)
            print(f"{status} {collection_name:20}: {count:,} documents (min: {expected:,})")
    
    if 'integrity_checks' in results:
        print("\n🔗 Referential Integrity:")
        print("-" * 40)
        integrity = results['integrity_checks']
        for check_name, count in integrity.items():
            check_display = check_name.replace('_', ' ').title()
            print(f"✓ {check_display:30}: {count:,}")

def print_database_info(seeder: OnePasswordSeeder) -> None:
    """Print database information and sample queries"""
    print("\n" + "="*60)
    print("DATABASE INFORMATION")
    print("="*60)
    
    print(f"\n📋 Database: {seeder.database_schema.database_name}")
    print(f"🔗 Connection: {seeder.connection_string}")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📚 Collections:")
    print("-" * 40)
    db, client = seeder.get_database()
    for collection_name in seeder.database_schema.collections:
        count = db[collection_name].count_documents({})
        print(f"  • {collection_name:20}: {count:,} documents")
    client.close()
    
    print("\n🔍 Sample Queries:")
    print("-" * 40)
    
    db, client = seeder.get_database()
    
    # Recent audit events
    recent_events = list(db.audit_events.find().sort("timestamp", -1).limit(3))
    if recent_events:
        print(f"  Recent audit events: {len(recent_events)} found")
        for event in recent_events:
            print(f"    - {event['action']} on {event['object_type']} at {event['timestamp']}")
    
    # Failed sign-in attempts
    failed_attempts = db.sign_in_attempts.count_documents({"category": {"$ne": "success"}})
    total_attempts = db.sign_in_attempts.count_documents({})
    if total_attempts > 0:
        failure_rate = (failed_attempts / total_attempts) * 100
        print(f"  Sign-in failure rate: {failure_rate:.1f}% ({failed_attempts:,}/{total_attempts:,})")
    
    # Most active users
    pipeline = [
        {"$group": {"_id": "$actor_uuid", "event_count": {"$sum": 1}}},
        {"$sort": {"event_count": -1}},
        {"$limit": 3}
    ]
    active_users = list(db.audit_events.aggregate(pipeline))
    if active_users:
        print(f"  Most active users: {len(active_users)} found")
        for user in active_users:
            user_info = db.users.find_one({"uuid": user["_id"]})
            name = user_info.get("name", "Unknown") if user_info else "Unknown"
            print(f"    - {name}: {user['event_count']:,} events")
    
    client.close()

def main():
    """Main execution function"""
    print("🔐 1Password Events Database Generator")
    print("="*50)
    
    # Get MongoDB connection string
    connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    print(f"📡 Connecting to MongoDB: {connection_string}")
    
    # Check MongoDB connection
    if not check_mongodb_connection(connection_string):
        print("❌ Cannot connect to MongoDB. Please ensure MongoDB is running.")
        print("   Set MONGODB_URI environment variable if using a different connection string.")
        sys.exit(1)
    
    print("✅ MongoDB connection successful")
    
    try:
        # Initialize seeder
        print("\n🌱 Initializing database seeder...")
        seeder = OnePasswordSeeder(connection_string)
        
        # Check if database already exists
        client = MongoClient(connection_string)
        existing_dbs = client.list_database_names()
        
        if seeder.database_schema.database_name in existing_dbs:
            print(f"⚠️  Database '{seeder.database_schema.database_name}' already exists")
            response = input("Do you want to drop and recreate it? (y/N): ").strip().lower()
            if response == 'y':
                client.drop_database(seeder.database_schema.database_name)
                print("🗑️  Existing database dropped")
            else:
                print("❌ Aborted. Database was not modified.")
                sys.exit(0)
        
        client.close()
        
        # Start seeding
        print(f"\n🚀 Starting database generation...")
        start_time = time.time()
        
        seeder.seed_all_collections()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Database generation completed in {duration:.2f} seconds")
        
        # Validate data
        print("\n🔍 Validating generated data...")
        validation_results = seeder.validate_data()
        print_validation_results(validation_results)
        
        # Print database info
        print_database_info(seeder)
        
        print("\n" + "="*60)
        print("🎉 SUCCESS: 1Password Events Database Generated!")
        print("="*60)
        print("\n💡 You can now:")
        print("   • Connect to the database using MongoDB tools")
        print("   • Run queries against the generated data")
        print("   • Use this data for testing and development")
        print("   • Analyze security patterns and trends")
        
        # Connection examples
        print(f"\n📝 Connection Examples:")
        print("-" * 30)
        print(f"MongoDB URI: {connection_string}")
        print(f"Database: {seeder.database_schema.database_name}")
        print("Collections: users, devices, vaults, items, audit_events, item_usages, sign_in_attempts")
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during database generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()