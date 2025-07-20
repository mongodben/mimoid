# Architect Database Schema

Architect the database schema following the [technical design](./1_tech_design.md) that was ouput to the `tech_design.md` file. 

## Output `db_schema.py`

Write the output to a file called `db_schema.py` that contains the following:

The schema should be defined as a set of Pydantic models, one for each collection and index definitions.

All the required data should be output to a single `MongoDbDataSchema` Pydantic model.

The file should import the following types and export a single `MongoDbDataSchema` Pydantic model.

The export must be named `database_schema`.

Imported types:
```python
from pydantic import BaseModel
from typing import Dict, List, Any, Union
from enum import Enum

class IndexDirection(str, Enum):
    ASCENDING = "1"
    DESCENDING = "-1"
    TEXT = "text"
    HASHED = "hashed"

class IndexDefinition(BaseModel):
    """Definition for a MongoDB index"""
    name: str
    keys: Dict[str, Union[IndexDirection, str]]  # field_name -> direction
    unique: bool = False
    sparse: bool = False
    background: bool = True

class BaseCollectionSchema(BaseModel):
    """Base schema definition for a MongoDB collection"""
    schema: Dict[str, Any]  # JSON schema definition
    indexes: List[IndexDefinition]
    description: str = ""

class BaseMongoDbSchema(BaseModel):
    """Base MongoDB database schema definition"""
    collections: Dict[str, BaseCollectionSchema]  # collection_name -> schema
    database_name: str
    description: str = ""

# MongoDB ObjectId type for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class BaseMongoDbDocumentSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id", description="MongoDB ObjectId")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

```

Example export:

```python
from datetime import datetime
from typing import Optional
from pydantic import Field, EmailStr
from bson import ObjectId

# Define Pydantic models for document schemas
class Article(BaseMongoDbDocumentSchema):
    title: str = Field(..., min_length=1, max_length=200, description="The title of the article")
    content: str = Field(..., min_length=1, description="The main content/body of the article")
    author_id: PyObjectId = Field(..., description="Reference to the user who authored this article")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the article was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the article was last updated")
    tags: List[str] = Field(default=[], max_items=20, description="List of tags associated with the article")
    is_published: bool = Field(default=False, description="Whether the article is published")

class User(BaseMongoDbDocumentSchema):
    username: str = Field(..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$", description="Unique username for the user")
    email: EmailStr = Field(..., description="User's email address")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the user account was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the user was last updated")
    is_active: bool = Field(default=True, description="Whether the user account is active")

# Define specific collection schemas
class ArticleCollectionSchema(BaseCollectionSchema):
    schema: Dict[str, Any] = Article.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="title_text_index",
            keys={"title": IndexDirection.TEXT, "content": IndexDirection.TEXT}
        ),
        IndexDefinition(
            name="author_created_index", 
            keys={"author_id": IndexDirection.ASCENDING, "created_at": IndexDirection.DESCENDING}
        )
    ]
    description: str = "Articles collection for blog posts"

class UserCollectionSchema(BaseCollectionSchema):
    schema: Dict[str, Any] = User.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="username_unique",
            keys={"username": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="email_unique",
            keys={"email": IndexDirection.ASCENDING},
            unique=True
        )
    ]
    description: str = "Users collection for blog authors"

# Export the complete schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "articles": ArticleCollectionSchema(),
        "users": UserCollectionSchema()
    }
    database_name: str = "blog_db"
    description: str = "Complete blog application database schema"

# Create the final export instance
# Remember to name the variable `database_schema`
database_schema = MongoDbDataSchema()
```
