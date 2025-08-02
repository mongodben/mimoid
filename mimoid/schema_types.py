"""Base schema types and classes for MongoDB database schema definitions"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Union, Optional
from enum import Enum
from bson import ObjectId


class IndexDirection(int, Enum):
    ASCENDING = 1
    DESCENDING = -1


class IndexDefinition(BaseModel):
    """Definition for a MongoDB index"""
    name: str
    keys: Dict[str, Union[IndexDirection, int, str]]  # field_name -> direction
    unique: bool = False
    sparse: bool = False
    background: bool = True


class BaseCollectionSchema(BaseModel):
    """Base schema definition for a MongoDB collection"""
    json_schema: Dict[str, Any] = Field(..., description="JSON schema definition")  # Renamed from schema to avoid shadowing
    indexes: List[IndexDefinition]
    description: str = ""


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