#!/usr/bin/env python3
"""
Clean duplicate entries from Cogna Educação Brazilian EdTech Platform
This script identifies and removes duplicate entries that prevent unique indexes
"""

import os
import sys
from pathlib import Path
import traceback
from collections import defaultdict

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Add the mimoid package to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pymongo import MongoClient
from db_schema import database_schema

def find_and_remove_duplicates():
    """Find and remove duplicate entries that violate unique constraints"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client[database_schema.database_name]
    
    print(f"🧹 Cleaning duplicates in database: {database_schema.database_name}")
    print(f"📡 MongoDB URI: {mongo_uri}")
    print()
    
    # Define the problematic unique fields we need to clean
    duplicate_issues = {
        "students": ["email"],
        "applications": ["protocol_number"], 
        "staff": ["email"]
    }
    
    total_removed = 0
    
    for collection_name, fields in duplicate_issues.items():
        print(f"🔍 Processing collection: {collection_name}")
        collection = db[collection_name]
        
        for field in fields:
            print(f"  Checking field: {field}")
            
            # Find duplicates using aggregation
            pipeline = [
                {"$group": {
                    "_id": f"${field}",
                    "count": {"$sum": 1},
                    "docs": {"$push": "$_id"}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            duplicates = list(collection.aggregate(pipeline))
            
            if not duplicates:
                print(f"    ✅ No duplicates found for {field}")
                continue
                
            print(f"    ⚠️  Found {len(duplicates)} duplicate values for {field}")
            
            # Remove duplicates, keeping only the first occurrence
            removed_count = 0
            for dup in duplicates:
                duplicate_value = dup["_id"]
                doc_ids = dup["docs"]
                
                # Keep the first document, remove the rest
                ids_to_remove = doc_ids[1:]  # Skip first document
                
                if ids_to_remove:
                    result = collection.delete_many({"_id": {"$in": ids_to_remove}})
                    removed_count += result.deleted_count
                    print(f"    🗑️  Removed {result.deleted_count} duplicates for {field}='{duplicate_value}'")
            
            total_removed += removed_count
            print(f"    ✅ Total removed for {field}: {removed_count}")
        
        print()
    
    client.close()
    print(f"🎉 Duplicate cleanup completed! Total documents removed: {total_removed}")
    return total_removed

def recreate_unique_indexes():
    """Recreate the unique indexes that failed due to duplicates"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client[database_schema.database_name]
    
    print("🔧 Recreating unique indexes...")
    
    # Drop the non-unique indexes we created as workarounds
    indexes_to_fix = [
        ("students", "email_unique_non_unique", "email_unique", {"email": 1}),
        ("applications", "protocol_number_unique_non_unique", "protocol_number_unique", {"protocol_number": 1}),
        ("staff", "email_unique_non_unique", "email_unique", {"email": 1})
    ]
    
    success_count = 0
    
    for collection_name, old_index_name, new_index_name, index_spec in indexes_to_fix:
        collection = db[collection_name]
        
        try:
            # Drop the non-unique index
            collection.drop_index(old_index_name)
            print(f"  ✅ Dropped non-unique index: {old_index_name}")
        except Exception as e:
            print(f"  ⚠️  Could not drop {old_index_name}: {e}")
        
        try:
            # Create the unique index
            collection.create_index(
                list(index_spec.items()),
                name=new_index_name,
                unique=True,
                background=True
            )
            print(f"  ✅ Created unique index: {new_index_name}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to create unique index {new_index_name}: {e}")
    
    client.close()
    print(f"🎉 Recreated {success_count} unique indexes!")

if __name__ == "__main__":
    try:
        removed_count = find_and_remove_duplicates()
        
        if removed_count > 0:
            print("\n" + "="*50)
            recreate_unique_indexes()
        else:
            print("No duplicates found, no index recreation needed.")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        if os.getenv("DEBUG") == "true":
            traceback.print_exc()
        sys.exit(1)