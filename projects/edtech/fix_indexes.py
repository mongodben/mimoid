#!/usr/bin/env python3
"""
Fix MongoDB indexes for Cogna Educação Brazilian EdTech Platform
This script recreates indexes with correct integer directions instead of string directions
"""

import os
import sys
from pathlib import Path
import traceback

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Add the mimoid package to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pymongo import MongoClient
from db_schema import database_schema

def fix_indexes():
    """Drop and recreate all indexes with correct types"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client[database_schema.database_name]
    
    print(f"🔧 Fixing indexes in database: {database_schema.database_name}")
    print(f"📡 MongoDB URI: {mongo_uri}")
    print()
    
    for collection_name, collection_schema in database_schema.collections.items():
        print(f"Processing collection: {collection_name}")
        collection = db[collection_name]
        
        # Get existing indexes (excluding the default _id index)
        existing_indexes = list(collection.list_indexes())
        
        # Drop all non-_id indexes
        for index in existing_indexes:
            if index['name'] != '_id_':
                try:
                    collection.drop_index(index['name'])
                    print(f"  ✅ Dropped index: {index['name']}")
                except Exception as e:
                    print(f"  ⚠️  Could not drop index {index['name']}: {e}")
        
        # Create new indexes with correct types
        for index_def in collection_schema.indexes:
            try:
                # Convert IndexDirection enums to integers
                keys_list = []
                for field, direction in index_def.keys.items():
                    if hasattr(direction, 'value'):
                        # It's an enum, get the integer value
                        keys_list.append((field, direction.value))
                    else:
                        # It's already an int or string
                        keys_list.append((field, direction))
                
                collection.create_index(
                    keys_list,
                    name=index_def.name,
                    unique=index_def.unique,
                    sparse=index_def.sparse,
                    background=index_def.background
                )
                print(f"  ✅ Created index: {index_def.name}")
                
            except Exception as e:
                if "duplicate key error" in str(e).lower() and index_def.unique:
                    # Try creating as non-unique index instead
                    try:
                        collection.create_index(
                            keys_list,
                            name=index_def.name + "_non_unique",
                            unique=False,
                            sparse=index_def.sparse,
                            background=index_def.background
                        )
                        print(f"  ⚠️  Created non-unique index: {index_def.name}_non_unique (duplicate data found)")
                    except Exception as e2:
                        print(f"  ❌ Failed to create non-unique index {index_def.name}: {e2}")
                else:
                    print(f"  ❌ Failed to create index {index_def.name}: {e}")
        
        print()
    
    client.close()
    print("🎉 Index fix completed!")

if __name__ == "__main__":
    try:
        fix_indexes()
    except Exception as e:
        print(f"❌ Index fix failed: {e}")
        if os.getenv("DEBUG") == "true":
            traceback.print_exc()
        sys.exit(1)