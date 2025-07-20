"""Tests for database seeder base class"""

import pytest
from mimiod import DatabaseSeeder, BaseMongoDbSchema, BaseCollectionSchema


class TestDatabaseSeeder:
    def test_abstract_class(self):
        """Test that DatabaseSeeder cannot be instantiated directly"""
        with pytest.raises(TypeError):
            DatabaseSeeder("mongodb://localhost", BaseMongoDbSchema(collections={}, database_name="test"))
    
    def test_concrete_implementation(self):
        """Test that a concrete implementation can be created"""
        
        class ConcreteDatabaseSeeder(DatabaseSeeder):
            def seed_all_collections(self, num_records=None):
                return "seeded"
            
            def create_indexes(self):
                return "indexes_created"
            
            def clear_database(self):
                return "cleared"
            
            def validate_seed_data(self):
                return "validated"
        
        schema = BaseMongoDbSchema(collections={}, database_name="test")
        seeder = ConcreteDatabaseSeeder("mongodb://localhost", schema)
        
        assert seeder.connection_string == "mongodb://localhost"
        assert seeder.database_schema == schema
        assert seeder.seed_all_collections() == "seeded"
        assert seeder.create_indexes() == "indexes_created"
        assert seeder.clear_database() == "cleared"
        assert seeder.validate_seed_data() == "validated"