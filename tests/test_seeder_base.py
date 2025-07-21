"""Tests for database seeder base class"""

import pytest
import logging
from unittest.mock import Mock, MagicMock, patch
from pydantic import BaseModel, Field, ValidationError
from mimoid import (
    DatabaseSeeder,
    BaseMongoDbSchema,
    BaseCollectionSchema,
    IndexDefinition,
    IndexDirection,
)


class TestDatabaseSeeder:
    def test_abstract_class(self):
        """Test that DatabaseSeeder cannot be instantiated directly"""
        with pytest.raises(TypeError):
            DatabaseSeeder(
                "mongodb://localhost",
                BaseMongoDbSchema(collections={}, database_name="test"),
            )

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


class TestValidateSchemaAndIndexes:
    """Test cases for the validate_schema_and_indexes method"""

    @pytest.fixture
    def sample_pydantic_models(self):
        """Create sample Pydantic models for testing"""

        class TestUser(BaseModel):
            name: str = Field(..., max_length=100)
            email: str = Field(..., max_length=200)
            age: int = Field(..., ge=0, le=120)
            active: bool = Field(default=True)

        class TestProduct(BaseModel):
            product_name: str = Field(..., max_length=150)
            price: float = Field(..., ge=0)
            category: str = Field(..., max_length=50)

        return {"users": TestUser, "products": TestProduct}

    @pytest.fixture
    def sample_schema(self):
        """Create a sample database schema for testing"""
        users_collection = BaseCollectionSchema(
            json_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "maxLength": 100},
                    "email": {"type": "string", "maxLength": 200},
                    "age": {"type": "number", "minimum": 0, "maximum": 120},
                    "active": {"type": "boolean"},
                },
            },
            indexes=[
                IndexDefinition(
                    name="email_unique",
                    keys={"email": IndexDirection.ASCENDING},
                    unique=True,
                ),
                IndexDefinition(
                    name="age_active_index",
                    keys={
                        "age": IndexDirection.ASCENDING,
                        "active": IndexDirection.DESCENDING,
                    },
                    unique=False,
                ),
            ],
        )

        products_collection = BaseCollectionSchema(
            json_schema={
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "maxLength": 150},
                    "price": {"type": "number", "minimum": 0},
                    "category": {"type": "string", "maxLength": 50},
                },
            },
            indexes=[
                IndexDefinition(
                    name="product_name_category",
                    keys={
                        "product_name": IndexDirection.ASCENDING,
                        "category": IndexDirection.ASCENDING,
                    },
                    unique=False,
                )
            ],
        )

        return BaseMongoDbSchema(
            collections={"users": users_collection, "products": products_collection},
            database_name="test_db",
        )

    @pytest.fixture
    def concrete_seeder(self, sample_schema):
        """Create a concrete implementation of DatabaseSeeder for testing"""

        class TestSeeder(DatabaseSeeder):
            def seed_all_collections(self, num_records=None):
                return "seeded"

            def create_indexes(self):
                return "indexes_created"

            def clear_database(self):
                return "cleared"

            def validate_seed_data(self):
                return "validated"

        return TestSeeder("mongodb://localhost:27017", sample_schema)

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_schema_and_indexes_success(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test successful validation of schema and indexes"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        # Mock collections
        mock_users_collection = MagicMock()
        mock_products_collection = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "users": mock_users_collection,
            "products": mock_products_collection,
        }[name]

        # Mock document counts
        mock_users_collection.count_documents.return_value = 5
        mock_products_collection.count_documents.return_value = 3

        # Mock sample documents (valid documents)
        mock_users_collection.find.return_value = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "active": True,
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 25,
                "active": False,
            },
        ]
        mock_products_collection.find.return_value = [
            {"product_name": "Widget A", "price": 19.99, "category": "widgets"},
            {"product_name": "Gadget B", "price": 49.99, "category": "gadgets"},
        ]

        # Mock indexes (correct indexes exist)
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "email_unique",
                "key": {"email": 1},
                "unique": True,
                "sparse": False,
            },
            {
                "name": "age_active_index",
                "key": {"age": 1, "active": -1},
                "unique": False,
                "sparse": False,
            },
        ]
        mock_products_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "product_name_category",
                "key": {"product_name": 1, "category": 1},
                "unique": False,
                "sparse": False,
            },
        ]

        # Run validation
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=10, pydantic_models=sample_pydantic_models
        )

        # Verify results
        assert result["validation_summary"]["overall_success"] is True
        assert result["validation_summary"]["total_collections"] == 2
        assert result["validation_summary"]["schema_validation_passed"] == 2
        assert result["validation_summary"]["index_validation_passed"] == 2
        assert result["validation_summary"]["total_documents_sampled"] == 4
        assert result["validation_summary"]["total_validation_errors"] == 0

        # Check individual collection results
        assert (
            result["collection_results"]["users"]["schema_validation"]["passed"] is True
        )
        assert (
            result["collection_results"]["users"]["index_validation"]["passed"] is True
        )
        assert (
            result["collection_results"]["products"]["schema_validation"]["passed"]
            is True
        )
        assert (
            result["collection_results"]["products"]["index_validation"]["passed"]
            is True
        )

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_schema_validation_failure(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test schema validation failure with invalid documents"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        mock_users_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_users_collection

        # Mock document count and invalid documents
        mock_users_collection.count_documents.return_value = 2
        mock_users_collection.find.return_value = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "active": True,
            },  # Valid
            {
                "name": "",
                "email": "invalid",
                "age": -5,
                "active": "not_boolean",
            },  # Invalid
        ]

        # Mock indexes (correct)
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "email_unique",
                "key": {"email": 1},
                "unique": True,
                "sparse": False,
            },
            {
                "name": "age_active_index",
                "key": {"age": 1, "active": -1},
                "unique": False,
                "sparse": False,
            },
        ]

        # Run validation
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=10, pydantic_models={"users": sample_pydantic_models["users"]}
        )

        # Verify results
        assert result["validation_summary"]["overall_success"] is False
        assert (
            result["collection_results"]["users"]["schema_validation"]["passed"]
            is False
        )
        assert (
            result["collection_results"]["users"]["schema_validation"][
                "valid_documents"
            ]
            == 1
        )
        assert (
            result["collection_results"]["users"]["schema_validation"][
                "invalid_documents"
            ]
            == 1
        )
        assert (
            len(result["collection_results"]["users"]["schema_validation"]["errors"])
            > 0
        )

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_missing_indexes(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test index validation failure with missing indexes"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        mock_users_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_users_collection

        # Mock document count and valid documents
        mock_users_collection.count_documents.return_value = 1
        mock_users_collection.find.return_value = [
            {"name": "John Doe", "email": "john@example.com", "age": 30, "active": True}
        ]

        # Mock missing indexes (only _id exists)
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}}
        ]

        # Run validation
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=10, pydantic_models={"users": sample_pydantic_models["users"]}
        )

        # Verify results
        assert result["validation_summary"]["overall_success"] is False
        assert (
            result["collection_results"]["users"]["index_validation"]["passed"] is False
        )
        assert (
            len(
                result["collection_results"]["users"]["index_validation"][
                    "missing_indexes"
                ]
            )
            == 2
        )
        assert (
            "email_unique"
            in result["collection_results"]["users"]["index_validation"][
                "missing_indexes"
            ]
        )
        assert (
            "age_active_index"
            in result["collection_results"]["users"]["index_validation"][
                "missing_indexes"
            ]
        )

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_index_property_mismatch(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test index validation failure with incorrect index properties"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        mock_users_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_users_collection

        # Mock document count and valid documents
        mock_users_collection.count_documents.return_value = 1
        mock_users_collection.find.return_value = [
            {"name": "John Doe", "email": "john@example.com", "age": 30, "active": True}
        ]

        # Mock indexes with incorrect properties (email_unique should be unique but isn't)
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "email_unique",
                "key": {"email": 1},
                "unique": False,
                "sparse": False,
            },  # Should be unique=True
            {
                "name": "age_active_index",
                "key": {"age": 1, "active": -1},
                "unique": False,
                "sparse": False,
            },
        ]

        # Run validation
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=10, pydantic_models={"users": sample_pydantic_models["users"]}
        )

        # Verify results
        assert result["validation_summary"]["overall_success"] is False
        assert (
            result["collection_results"]["users"]["index_validation"]["passed"] is False
        )
        assert any(
            "unique mismatch" in error
            for error in result["collection_results"]["users"]["index_validation"][
                "errors"
            ]
        )

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_large_collection_sampling(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test that large collections are properly sampled"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        mock_users_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_users_collection

        # Mock large collection (more documents than sample size)
        mock_users_collection.count_documents.return_value = 1000

        # Mock aggregate sampling
        mock_users_collection.aggregate.return_value = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "active": True,
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 25,
                "active": False,
            },
        ]

        # Mock indexes
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "email_unique",
                "key": {"email": 1},
                "unique": True,
                "sparse": False,
            },
            {
                "name": "age_active_index",
                "key": {"age": 1, "active": -1},
                "unique": False,
                "sparse": False,
            },
        ]

        # Run validation with small sample size
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=2, pydantic_models={"users": sample_pydantic_models["users"]}
        )

        # Verify that aggregation was called for sampling
        mock_users_collection.aggregate.assert_called_once_with(
            [{"$sample": {"size": 2}}]
        )

        # Verify results
        assert result["collection_results"]["users"]["document_count"] == 1000
        assert result["collection_results"]["users"]["documents_sampled"] == 2
        assert result["validation_summary"]["total_documents_sampled"] == 2

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_without_pydantic_models(self, mock_mongo_client, concrete_seeder):
        """Test validation when no Pydantic models are provided (index validation only)"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        mock_users_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_users_collection

        mock_users_collection.count_documents.return_value = 5

        # Mock correct indexes
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "email_unique",
                "key": {"email": 1},
                "unique": True,
                "sparse": False,
            },
            {
                "name": "age_active_index",
                "key": {"age": 1, "active": -1},
                "unique": False,
                "sparse": False,
            },
        ]

        # Run validation without Pydantic models
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=10, pydantic_models=None
        )

        # Verify results - schema validation should be skipped
        assert result["collection_results"]["users"]["documents_sampled"] == 0
        assert (
            result["collection_results"]["users"]["schema_validation"]["passed"] is True
        )  # Default true when not tested
        assert (
            result["collection_results"]["users"]["index_validation"]["passed"] is True
        )
        assert (
            result["validation_summary"]["schema_validation_passed"] == 2
        )  # Both collections pass by default

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_connection_failure(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test validation behavior when MongoDB connection fails"""
        # Mock connection failure
        mock_mongo_client.side_effect = Exception("Connection failed")

        # Run validation and expect exception
        with pytest.raises(Exception, match="Validation failed with exception"):
            concrete_seeder.validate_schema_and_indexes(
                sample_size=10, pydantic_models=sample_pydantic_models
            )

    @patch("mimoid.seeder_base.MongoClient")
    def test_validate_extra_indexes_noted(
        self, mock_mongo_client, concrete_seeder, sample_pydantic_models
    ):
        """Test that extra indexes are noted but don't fail validation"""
        # Mock MongoDB client and database
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db

        # Mock both collections
        mock_users_collection = MagicMock()
        mock_products_collection = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "users": mock_users_collection,
            "products": mock_products_collection,
        }[name]

        # Mock users collection
        mock_users_collection.count_documents.return_value = 1
        mock_users_collection.find.return_value = [
            {"name": "John Doe", "email": "john@example.com", "age": 30, "active": True}
        ]

        # Mock indexes with extra ones for users
        mock_users_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "email_unique",
                "key": {"email": 1},
                "unique": True,
                "sparse": False,
            },
            {
                "name": "age_active_index",
                "key": {"age": 1, "active": -1},
                "unique": False,
                "sparse": False,
            },
            {
                "name": "extra_name_index",
                "key": {"name": 1},
                "unique": False,
                "sparse": False,
            },  # Extra
        ]

        # Mock products collection
        mock_products_collection.count_documents.return_value = 1
        mock_products_collection.find.return_value = [
            {"product_name": "Widget A", "price": 19.99, "category": "widgets"}
        ]

        # Mock correct indexes for products
        mock_products_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {
                "name": "product_name_category",
                "key": {"product_name": 1, "category": 1},
                "unique": False,
                "sparse": False,
            },
        ]

        # Run validation
        result = concrete_seeder.validate_schema_and_indexes(
            sample_size=10, pydantic_models=sample_pydantic_models
        )

        # Verify results - extra indexes don't fail validation
        assert result["validation_summary"]["overall_success"] is True
        assert (
            result["collection_results"]["users"]["index_validation"]["passed"] is True
        )
        assert (
            result["collection_results"]["products"]["index_validation"]["passed"]
            is True
        )
        assert (
            "extra_name_index"
            in result["collection_results"]["users"]["index_validation"][
                "extra_indexes"
            ]
        )
