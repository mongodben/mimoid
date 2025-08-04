#!/usr/bin/env python
"""Test MongoDB connection and basic operations"""

import os
from pymongo import MongoClient
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test basic MongoDB operations"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    
    try:
        logger.info(f"Connecting to MongoDB at {mongodb_uri}...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        logger.info("Testing connection...")
        client.admin.command('ping')
        logger.info("✓ Connection successful")
        
        # Test database operations
        db = client['test_brazilian_edtech']
        collection = db['test_collection']
        
        # Insert a document
        logger.info("Testing insert...")
        doc = {'_id': ObjectId(), 'test': 'data', 'number': 42}
        collection.insert_one(doc)
        logger.info("✓ Insert successful")
        
        # Find the document
        logger.info("Testing find...")
        found = collection.find_one({'_id': doc['_id']})
        logger.info(f"✓ Find successful: {found}")
        
        # Clean up
        logger.info("Cleaning up...")
        collection.delete_one({'_id': doc['_id']})
        client.drop_database('test_brazilian_edtech')
        logger.info("✓ Cleanup successful")
        
        logger.info("\nAll tests passed! MongoDB is working correctly.")
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_connection()