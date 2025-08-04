"""Base schema types and classes for MongoDB database schema definitions"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Union, Optional, Tuple, Type
from enum import Enum
from bson import ObjectId


class IndexDirection(Enum):
    ASCENDING = 1
    DESCENDING = -1
    TEXT = "text"
    GEO2D = "2d"
    GEO2DSPHERE = "2dsphere"
    HASHED = "hashed"
    
    @property
    def value(self):
        """Return the actual value for MongoDB"""
        return self._value_


class IndexDefinition(BaseModel):
    """Definition for a MongoDB index"""
    name: Optional[str] = None
    keys: Union[Dict[str, Union[IndexDirection, int, str]], List[Tuple[str, Union[IndexDirection, int, str]]]]  # field_name -> direction
    unique: bool = False
    sparse: bool = False
    background: bool = True
    ttl_seconds: Optional[int] = None
    
    @field_validator('keys')
    def validate_keys(cls, v):
        """Convert list of tuples to dict if needed"""
        if isinstance(v, list):
            return dict(v)
        return v
    
    @field_validator('name', mode='before')
    def generate_name(cls, v, info):
        """Generate a name if not provided"""
        if v is None and 'keys' in info.data:
            keys = info.data['keys']
            if isinstance(keys, list):
                keys = dict(keys)
            if isinstance(keys, dict):
                # Generate name from keys
                parts = []
                for field, direction in keys.items():
                    if isinstance(direction, IndexDirection):
                        dir_name = direction.name.lower()
                    elif isinstance(direction, (int, str)):
                        dir_name = str(direction).replace('-1', 'desc').replace('1', 'asc')
                    else:
                        dir_name = str(direction)
                    parts.append(f"{field}_{dir_name}")
                return "_".join(parts[:3]) + ("_idx" if len(parts) <= 3 else "_compound_idx")
        return v


class BaseCollectionSchema(BaseModel):
    """Base schema definition for a MongoDB collection"""
    collection_name: str
    document_schema: Optional[Type[BaseModel]] = None
    json_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema definition")  # Made optional
    indexes: List[IndexDefinition] = []
    description: str = ""
    
    def model_post_init(self, __context: Any) -> None:
        """Generate json_schema from document_schema if not provided"""
        if self.json_schema is None and self.document_schema is not None:
            # Generate JSON schema from Pydantic model
            pydantic_schema = self.document_schema.model_json_schema()
            # Convert to MongoDB-compatible JSON schema
            self.json_schema = {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": pydantic_schema.get("properties", {})
                }
            }


class BaseMongoDbSchema(BaseModel):
    """Base MongoDB database schema definition"""
    collections: Dict[str, BaseCollectionSchema]  # collection_name -> schema
    database_name: str
    description: str = ""


# MongoDB ObjectId type for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_plain_validator_function(
            cls.validate,
        )
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string", "format": "objectid"}


class BaseMongoDbDocumentSchema(BaseModel):
    model_config = {
        'validate_by_name': True,
        'arbitrary_types_allowed': True,
    }
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id", description="MongoDB ObjectId")