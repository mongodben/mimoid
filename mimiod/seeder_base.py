"""Abstract base class for database seeder"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from .schema_types import BaseMongoDbSchema


class DatabaseSeeder(ABC):
    """Abstract base class for database seeder"""
    
    def __init__(self, connection_string: str, database_schema: BaseMongoDbSchema):
        """Initialize seeder with connection string and database schema"""
        self.connection_string = connection_string
        self.database_schema = database_schema
    
    @abstractmethod
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        pass
    
    @abstractmethod
    def create_indexes(self):
        """Create indexes as defined in the schema"""
        pass
    
    @abstractmethod
    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        pass
    
    @abstractmethod
    def validate_seed_data(self):
        """Validate the seeded data meets quality standards"""
        pass