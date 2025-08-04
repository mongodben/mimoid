#!/usr/bin/env python
"""Test institution generation speed"""

import time
import logging
from seed_db import BrazilianEdtechSeeder
from db_schema import BrazilianEdtechSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generation():
    """Test institution generation without database insertion"""
    schema = BrazilianEdtechSchema()
    seeder = BrazilianEdtechSeeder("mongodb://localhost:27017", schema)
    
    # Override the seed_institutions method to not insert
    original_method = seeder.seed_institutions
    
    def mock_seed_institutions(count):
        logger.info(f"Generating {count} institutions (no DB insert)...")
        start_time = time.time()
        
        # Call the original method but intercept the DB call
        seeder.db.institutions.insert_many = lambda x: logger.info(f"Would insert {len(x)} institutions")
        original_method(count)
        
        elapsed = time.time() - start_time
        logger.info(f"Generation took {elapsed:.2f} seconds")
    
    seeder.seed_institutions = mock_seed_institutions
    
    # Test with different counts
    for count in [1, 10, 50]:
        logger.info(f"\nTesting with {count} institutions:")
        seeder.seed_institutions(count)

if __name__ == "__main__":
    test_generation()