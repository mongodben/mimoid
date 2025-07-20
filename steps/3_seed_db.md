# Seed Database

Generate sample data for the MongoDB database using the `database_schema` exported from step 2 in the `db_schema.py` file.

The seed script should create realistic sample data that follows the schema definitions and respects all constraints, relationships, and indexes.

## Output

Output the resulting script from this step to a new file called `seed_db.py`.

## Requirements

1. Import the `database_schema` from the step 2 output `db_schema.py` file.
2. Use data generation libraries to create realistic sample data
3. Respect all schema constraints and validations
4. Create proper relationships between collections (e.g., articles reference valid users)
5. Generate enough data to be useful for testing and development

## Available Libraries

The following libraries are available for use in the seed script:

- `faker`: For generating realistic sample data
- `openai`: For generating sample data using LLM. 
  - Only use this if `faker` isn't sufficient, as it's much slower and more expensive.
  - Relevant environment variables:
    - `OPENAI_API_KEY`: OpenAI API key
    - `OPENAI_ENDPOINT`: OpenAI-AI compatible endpoint
    - `OPENAI_MODEL`: OpenAI model to use
- `pymongo`: For interacting with MongoDB
- `pydantic`: For validating and serializing data
- `bson`: For working with MongoDB's binary data format
- Python standard library


## Data Generation Strategy

1. **Generate Base Collections First**: Generate collections that other collections depend on
   - e.g. users before articles.
2. **Maintain Referential Integrity**: Ensure that foreign key references point to valid documents.
   - e.g. articles reference valid users.
3. **Create Realistic Data Distributions**: 
   - E.g.: Some users should have multiple articles, some articles should have many tags, others few.
   - Vary creation dates to simulate realistic usage patterns.
4. **Respect Schema Constraints**: Follow field validation rules, use proper data types and formats, generate valid data that matches the Pydantic model constraints.
   - Follow field validation rules (min/max lengths, regex patterns)
   - Use proper data types and formats
   - Generate valid email addresses, usernames, etc.
5. **Validation and Quality Checks**: After seeding, the script should validate:
   - Schema Compliance: All documents match their Pydantic models
   - Referential Integrity: All foreign key references are valid
   - Index Creation: All indexes are created successfully
   - Data Distribution: Reasonable distribution of data across fields

## `DatabaseSeeder` Class

The `DatabaseSeeder` class should be a Python class that implements the data generation strategy.

```python
# create abstract base class for DatabaseSeeder
from abc import ABC, abstractmethod
from typing import Dict, Optional

# Import from step 2 schema
from database_schema import BaseMongoDbSchema

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
```

## Example Implementation Structure

```python
from faker import Faker
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Optional, List

# Import the abstract base class and schema from step 2
from database_schema import database_schema, BaseMongoDbSchema
from seed_db_base import DatabaseSeeder as BaseDatabaseSeeder

class ConcreteDatabaseSeeder(BaseDatabaseSeeder):
    def __init__(self, connection_string: str, database_schema: BaseMongoDbSchema):
        super().__init__(connection_string, database_schema)
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        self.fake = Faker()
        
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        if num_records is None:
            num_records = {
                'users': 50,
                'articles': 200
            }
            
        # Seed in dependency order
        user_ids = self.seed_users(num_records['users'])
        self.seed_articles(num_records['articles'], user_ids)
        
    def seed_users(self, count: int) -> List[ObjectId]:
        """Generate and insert user documents"""
        users = []
        for _ in range(count):
            user = {
                '_id': ObjectId(),
                'username': self.fake.user_name(),
                'email': self.fake.email(),
                'created_at': self.fake.date_time_between(start_date='-2y', end_date='now'),
                'updated_at': None,
                'is_active': random.choice([True, True, True, False])  # 75% active
            }
            users.append(user)
            
        self.db.users.insert_many(users)
        return [user['_id'] for user in users]
        
    def seed_articles(self, count: int, user_ids: List[ObjectId]):
        """Generate and insert article documents"""
        articles = []
        for _ in range(count):
            created_date = self.fake.date_time_between(start_date='-1y', end_date='now')
            article = {
                '_id': ObjectId(),
                'title': self.fake.sentence(nb_words=6).rstrip('.'),
                'content': self.fake.text(max_nb_chars=2000),
                'author_id': random.choice(user_ids),
                'created_at': created_date,
                'updated_at': self.fake.date_time_between(start_date=created_date, end_date='now') if random.random() < 0.3 else None,
                'tags': random.sample(['tech', 'lifestyle', 'travel', 'food', 'sports', 'music', 'art', 'science'], k=random.randint(1, 4)),
                'is_published': random.choice([True, True, False])  # 66% published
            }
            articles.append(article)
            
        self.db.articles.insert_many(articles)
        
    def create_indexes(self):
        """Create indexes as defined in the schema"""
        for collection_name, collection_schema in self.database_schema.collections.items():
            collection = self.db[collection_name]
            for index_def in collection_schema.indexes:
                index_keys = [(field, direction) for field, direction in index_def.keys.items()]
                collection.create_index(
                    index_keys,
                    name=index_def.name,
                    unique=index_def.unique,
                    sparse=index_def.sparse,
                    background=index_def.background
                )
                
    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        for collection_name in self.database_schema.collections.keys():
            self.db[collection_name].drop()
            
    def validate_seed_data(self):
        """Validate the seeded data meets quality standards"""
        # Check referential integrity
        articles_with_invalid_authors = self.db.articles.count_documents({
            'author_id': {'$nin': [user['_id'] for user in self.db.users.find({}, {'_id': 1})]}
        })
        
        if articles_with_invalid_authors > 0:
            raise ValueError(f"Found {articles_with_invalid_authors} articles with invalid author references")
            
        # Check schema compliance
        for collection_name, collection_schema in self.database_schema.collections.items():
            # Validate a sample of documents against the Pydantic model
            sample_docs = list(self.db[collection_name].find().limit(10))
            for doc in sample_docs:
                # This would validate against the Pydantic model
                # model_class.parse_obj(doc)
                pass
                
        print("Data validation passed!")

# Usage
if __name__ == "__main__":
    seeder = ConcreteDatabaseSeeder("mongodb://localhost:27017", database_schema)
    
    # Clear existing data (optional)
    seeder.clear_database()
    
    # Seed with sample data
    seeder.seed_all_collections({
        'users': 100,
        'articles': 500
    })
    
    # Create indexes
    seeder.create_indexes()
    
    # Validate the seeded data
    seeder.validate_seed_data()
    
    print("Database seeded successfully!")
```

## Advanced Data Generation Techniques

### 1. Weighted Random Choices
```python
# Some users are more prolific writers
author_weights = [1 if i < len(user_ids) * 0.8 else 5 for i in range(len(user_ids))]
author_id = random.choices(user_ids, weights=author_weights)[0]
```

### 2. Time-based Correlations
```python
# Articles created closer to now are more likely to be published
days_ago = (datetime.now() - created_date).days
publish_probability = max(0.3, 1.0 - (days_ago / 365))
is_published = random.random() < publish_probability
```

### 3. Content-aware Tag Generation
```python
# Generate tags based on article content
content_keywords = ['tech', 'travel', 'food']  # Extract from content
tags = random.sample(content_keywords + ['general', 'blog'], k=random.randint(1, 3))
```

```python
def validate_seed_data(self):
    """Validate the seeded data meets quality standards"""
    # Check referential integrity
    articles_with_invalid_authors = self.db.articles.count_documents({
        'author_id': {'$nin': [user['_id'] for user in self.db.users.find({}, {'_id': 1})]}
    })
    
    if articles_with_invalid_authors > 0:
        raise ValueError(f"Found {articles_with_invalid_authors} articles with invalid author references")
        
    # Check schema compliance
    for collection_name, collection_schema in self.schema.collections.items():
        # Validate a sample of documents against the Pydantic model
        sample_docs = list(self.db[collection_name].find().limit(10))
        for doc in sample_docs:
            # This would validate against the Pydantic model
            # model_class.parse_obj(doc)
            pass
            
    print("Data validation passed!")
```

## Output Requirements

The final seed script should:

1. **Be executable** as a standalone Python script
2. **Accept configuration** for number of records to generate
3. **Provide progress feedback** during generation
4. **Handle errors gracefully** with proper logging
5. **Be idempotent** - safe to run multiple times
6. **Export a `seed_database()` function** that can be imported and used programmatically