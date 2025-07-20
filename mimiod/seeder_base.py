"""Abstract base class for database seeder"""

import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any, Type
from pymongo import MongoClient
from pydantic import BaseModel, ValidationError
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
    
    def validate_schema_and_indexes(self, sample_size: int = 10, pydantic_models: Optional[Dict[str, Type[BaseModel]]] = None):
        """
        Validate that collections follow the defined schema and have proper indexes.
        
        Args:
            sample_size: Number of documents to sample per collection for validation
            pydantic_models: Dictionary mapping collection names to Pydantic model classes
                           Example: {"facilities": Facility, "products": Product}
        
        Returns:
            Dict[str, Any]: Validation results with detailed information about successes/failures
        
        Raises:
            Exception: If MongoDB connection fails or critical validation issues found
        """
        logger = logging.getLogger(__name__)
        logger.info("Starting schema and index validation...")
        
        results = {
            "validation_summary": {
                "total_collections": 0,
                "schema_validation_passed": 0,
                "index_validation_passed": 0,
                "total_documents_sampled": 0,
                "total_validation_errors": 0
            },
            "collection_results": {},
            "errors": []
        }
        
        try:
            # Connect to database
            client = MongoClient(self.connection_string)
            db = client[self.database_schema.database_name]
            
            # Validate each collection
            for collection_name, collection_schema in self.database_schema.collections.items():
                logger.info(f"Validating collection '{collection_name}'...")
                
                collection = db[collection_name]
                collection_result = {
                    "document_count": 0,
                    "documents_sampled": 0,
                    "schema_validation": {
                        "passed": True,
                        "errors": [],
                        "valid_documents": 0,
                        "invalid_documents": 0
                    },
                    "index_validation": {
                        "passed": True,
                        "errors": [],
                        "expected_indexes": len(collection_schema.indexes),
                        "found_indexes": 0,
                        "missing_indexes": [],
                        "extra_indexes": []
                    }
                }
                
                # Get document count
                collection_result["document_count"] = collection.count_documents({})
                
                # 1. SCHEMA VALIDATION - Sample documents and validate against Pydantic models
                if pydantic_models and collection_name in pydantic_models:
                    model_class = pydantic_models[collection_name]
                    
                    # Sample documents for validation
                    sample_count = min(sample_size, collection_result["document_count"])
                    if sample_count > 0:
                        # Get random sample of documents
                        if collection_result["document_count"] <= sample_size:
                            # Sample all documents if collection is small
                            sample_documents = list(collection.find({}))
                        else:
                            # Random sampling for larger collections
                            sample_documents = list(collection.aggregate([
                                {"$sample": {"size": sample_count}}
                            ]))
                        
                        collection_result["documents_sampled"] = len(sample_documents)
                        
                        # Validate each sampled document
                        for doc in sample_documents:
                            try:
                                # Convert MongoDB document to Pydantic model
                                model_class.model_validate(doc)
                                collection_result["schema_validation"]["valid_documents"] += 1
                            except ValidationError as e:
                                collection_result["schema_validation"]["invalid_documents"] += 1
                                collection_result["schema_validation"]["passed"] = False
                                error_msg = f"Document validation failed: {str(e)}"
                                collection_result["schema_validation"]["errors"].append(error_msg)
                                logger.warning(f"Schema validation error in {collection_name}: {error_msg}")
                            except Exception as e:
                                collection_result["schema_validation"]["invalid_documents"] += 1
                                collection_result["schema_validation"]["passed"] = False
                                error_msg = f"Unexpected validation error: {str(e)}"
                                collection_result["schema_validation"]["errors"].append(error_msg)
                                logger.error(f"Unexpected schema validation error in {collection_name}: {error_msg}")
                
                # 2. INDEX VALIDATION - Check that all expected indexes exist
                actual_indexes = list(collection.list_indexes())
                collection_result["index_validation"]["found_indexes"] = len(actual_indexes)
                
                # Create sets of expected and actual index names for comparison
                expected_index_names = {idx.name for idx in collection_schema.indexes}
                # Add default _id index to expected (MongoDB creates this automatically)
                expected_index_names.add("_id_")
                
                actual_index_names = {idx.get("name", "") for idx in actual_indexes}
                
                # Check for missing indexes
                missing_indexes = expected_index_names - actual_index_names
                if missing_indexes:
                    collection_result["index_validation"]["passed"] = False
                    collection_result["index_validation"]["missing_indexes"] = list(missing_indexes)
                    error_msg = f"Missing indexes: {missing_indexes}"
                    collection_result["index_validation"]["errors"].append(error_msg)
                    logger.warning(f"Index validation error in {collection_name}: {error_msg}")
                
                # Check for extra indexes (not necessarily an error, but worth noting)
                extra_indexes = actual_index_names - expected_index_names
                if extra_indexes:
                    collection_result["index_validation"]["extra_indexes"] = list(extra_indexes)
                    logger.info(f"Extra indexes found in {collection_name}: {extra_indexes}")
                
                # Detailed index validation - check index properties
                for expected_index in collection_schema.indexes:
                    matching_actual_index = None
                    for actual_index in actual_indexes:
                        if actual_index.get("name") == expected_index.name:
                            matching_actual_index = actual_index
                            break
                    
                    if matching_actual_index:
                        # Validate index properties
                        validation_errors = []
                        
                        # Check unique property
                        expected_unique = expected_index.unique
                        actual_unique = matching_actual_index.get("unique", False)
                        if expected_unique != actual_unique:
                            validation_errors.append(f"Index {expected_index.name}: unique mismatch (expected: {expected_unique}, actual: {actual_unique})")
                        
                        # Check sparse property
                        expected_sparse = expected_index.sparse
                        actual_sparse = matching_actual_index.get("sparse", False)
                        if expected_sparse != actual_sparse:
                            validation_errors.append(f"Index {expected_index.name}: sparse mismatch (expected: {expected_sparse}, actual: {actual_sparse})")
                        
                        # Check key structure
                        expected_key = {}
                        for field, direction in expected_index.keys.items():
                            if hasattr(direction, 'value'):
                                dir_value = direction.value
                                if dir_value == "1":
                                    dir_value = 1
                                elif dir_value == "-1":
                                    dir_value = -1
                            else:
                                dir_value = direction
                                if dir_value == "1":
                                    dir_value = 1
                                elif dir_value == "-1":
                                    dir_value = -1
                            expected_key[field] = dir_value
                        
                        actual_key = matching_actual_index.get("key", {})
                        if expected_key != actual_key:
                            validation_errors.append(f"Index {expected_index.name}: key structure mismatch (expected: {expected_key}, actual: {actual_key})")
                        
                        if validation_errors:
                            collection_result["index_validation"]["passed"] = False
                            collection_result["index_validation"]["errors"].extend(validation_errors)
                            for error in validation_errors:
                                logger.warning(f"Index property validation error in {collection_name}: {error}")
                
                # Store collection results
                results["collection_results"][collection_name] = collection_result
                
                # Update summary
                results["validation_summary"]["total_collections"] += 1
                if collection_result["schema_validation"]["passed"]:
                    results["validation_summary"]["schema_validation_passed"] += 1
                if collection_result["index_validation"]["passed"]:
                    results["validation_summary"]["index_validation_passed"] += 1
                
                results["validation_summary"]["total_documents_sampled"] += collection_result["documents_sampled"]
                results["validation_summary"]["total_validation_errors"] += (
                    len(collection_result["schema_validation"]["errors"]) + 
                    len(collection_result["index_validation"]["errors"])
                )
                
                logger.info(f"Validation completed for collection '{collection_name}': "
                          f"Schema={'✅' if collection_result['schema_validation']['passed'] else '❌'}, "
                          f"Indexes={'✅' if collection_result['index_validation']['passed'] else '❌'}")
            
            client.close()
            
            # Generate summary
            summary = results["validation_summary"]
            logger.info("Schema and Index Validation Summary:")
            logger.info(f"  • Collections validated: {summary['total_collections']}")
            logger.info(f"  • Schema validation passed: {summary['schema_validation_passed']}/{summary['total_collections']}")
            logger.info(f"  • Index validation passed: {summary['index_validation_passed']}/{summary['total_collections']}")
            logger.info(f"  • Documents sampled: {summary['total_documents_sampled']}")
            logger.info(f"  • Total validation errors: {summary['total_validation_errors']}")
            
            # Determine overall success
            all_schema_passed = summary['schema_validation_passed'] == summary['total_collections']
            all_indexes_passed = summary['index_validation_passed'] == summary['total_collections']
            
            results["validation_summary"]["overall_success"] = all_schema_passed and all_indexes_passed
            
            if results["validation_summary"]["overall_success"]:
                logger.info("✅ All validation checks passed!")
            else:
                logger.warning("❌ Some validation checks failed!")
            
            return results
            
        except Exception as e:
            error_msg = f"Validation failed with exception: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
            raise Exception(error_msg) from e