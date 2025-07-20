"""Tests for schema types and base classes"""

import pytest
from bson import ObjectId

from mimiod import (
    IndexDirection,
    IndexDefinition,
    BaseCollectionSchema,
    BaseMongoDbSchema,
    PyObjectId,
    BaseMongoDbDocumentSchema,
)


class TestIndexDirection:
    def test_enum_values(self):
        assert IndexDirection.ASCENDING == "1"
        assert IndexDirection.DESCENDING == "-1"
        assert IndexDirection.TEXT == "text"
        assert IndexDirection.HASHED == "hashed"


class TestIndexDefinition:
    def test_basic_index(self):
        index = IndexDefinition(
            name="test_index", keys={"field1": IndexDirection.ASCENDING}
        )
        assert index.name == "test_index"
        assert index.keys == {"field1": "1"}
        assert index.unique is False
        assert index.background is True

    def test_compound_index(self):
        index = IndexDefinition(
            name="compound_index",
            keys={
                "field1": IndexDirection.ASCENDING,
                "field2": IndexDirection.DESCENDING,
            },
            unique=True,
        )
        assert index.unique is True
        assert len(index.keys) == 2


class TestPyObjectId:
    def test_create_from_string(self):
        oid_str = "507f1f77bcf86cd799439011"
        py_oid = PyObjectId.validate(oid_str)
        assert isinstance(py_oid, ObjectId)
        assert str(py_oid) == oid_str

    def test_create_from_objectid(self):
        original_oid = ObjectId()
        py_oid = PyObjectId.validate(original_oid)
        assert py_oid == original_oid

    def test_invalid_objectid(self):
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            PyObjectId.validate("invalid_id")


class TestBaseMongoDbDocumentSchema:
    def test_document_with_id(self):
        class TestDoc(BaseMongoDbDocumentSchema):
            name: str
            value: int

        doc = TestDoc(name="test", value=42)
        assert doc.name == "test"
        assert doc.value == 42
        assert isinstance(doc.id, ObjectId)

    def test_document_with_custom_id(self):
        class TestDoc(BaseMongoDbDocumentSchema):
            name: str

        custom_id = ObjectId()
        doc = TestDoc(_id=custom_id, name="test")
        assert doc.id == custom_id


class TestBaseCollectionSchema:
    def test_collection_schema(self):
        schema = BaseCollectionSchema(
            json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            indexes=[
                IndexDefinition(
                    name="name_index", keys={"name": IndexDirection.ASCENDING}
                )
            ],
            description="Test collection",
        )
        assert schema.description == "Test collection"
        assert len(schema.indexes) == 1
        assert schema.indexes[0].name == "name_index"


class TestBaseMongoDbSchema:
    def test_database_schema(self):
        collection_schema = BaseCollectionSchema(
            json_schema={"type": "object"}, indexes=[], description="Test collection"
        )

        db_schema = BaseMongoDbSchema(
            collections={"test_collection": collection_schema},
            database_name="test_db",
            description="Test database",
        )

        assert db_schema.database_name == "test_db"
        assert "test_collection" in db_schema.collections
        assert db_schema.collections["test_collection"] == collection_schema
