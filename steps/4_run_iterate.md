# Run Seed and Iterate

Execute the generated seed script and perform validation and iteration cycles to ensure the database is properly populated and functional.

## Output Files

This step should execute exported `seed_db.py` file and create any additional validation or iteration files as needed. 

Create a new file called `main.py` that imports and executes the `seed_db.py` file with any additional necessary logic. 

## Execution Steps

### 1. Pre-execution Validation

Before running the seed script, validate that all prerequisites are met:

1. **Database Connection**: Ensure MongoDB is running and accessible
   - Test connection to the database server
   - Verify database permissions for create/drop operations

2. **Schema Validation**: Validate the generated `db_schema.py`
   - Import and instantiate the `database_schema` without errors
   - Verify all Pydantic models are valid
   - Check that all required fields and constraints are properly defined

3. **Environment Setup**: Check required environment variables
   - `MONGODB_URI` or connection string
   - `OPENAI_API_KEY` (if using AI-generated content)
   - Any other required configuration

### 2. Execute `main.py` Script

Run the `main.py` script with proper error handling:

```bash
uv run python path/to/main.py
```

### 3. Validation and Quality Checks

After seeding, perform comprehensive validation:

1. **Data Integrity Checks**
   - Verify all collections were created
   - Check document counts match expected ranges
   - Validate referential integrity between collections
   - Ensure no orphaned references exist

2. **Schema Compliance**
   - Sample documents from each collection
   - Validate against Pydantic models
   - Check field types, constraints, and validation rules
   - Verify required fields are populated

3. **Index Verification**
   - Confirm all indexes were created successfully
   - Check index performance with sample queries
   - Verify unique constraints are enforced

**✨ Use Built-in Validation Method**
The `DatabaseSeeder` base class provides a comprehensive `validate_schema_and_indexes()` method that automatically performs steps 2 and 3 above. Use this method in your validation process:

```python
# In your main.py or validation script
pydantic_models = {
    "collection_name": PydanticModelClass,
    # ... map all your collections to their Pydantic models
}

validation_results = seeder.validate_schema_and_indexes(
    sample_size=10,  # Number of documents to sample per collection
    pydantic_models=pydantic_models
)

if not validation_results['validation_summary']['overall_success']:
    print("❌ Validation failed!")
    # Handle validation errors
else:
    print("✅ All validation checks passed!")
```

4. **Data Quality Assessment**
   - Check for realistic data distribution
   - Verify data variety and uniqueness
   - Ensure proper relationships between entities
   - Validate date ranges and temporal consistency

### 4. Iteration and Refinement

If validation fails or quality is insufficient, iterate:

#### Common Issues and Solutions

1. **Schema Validation Errors**
   - Fix Pydantic model definitions in `db_schema.py`
   - Update field types, constraints, or validation rules
   - Regenerate and retest the schema

2. **Seeding Failures**
   - Debug data generation logic in `seed_db.py`
   - Fix referential integrity issues
   - Adjust data generation parameters
   - Handle edge cases in data creation

3. **Data Quality Issues**
   - Improve faker patterns and distributions
   - Add more realistic data generation logic
   - Enhance relationship modeling
   - Increase data variety and realism

4. **Performance Issues**
   - Optimize index definitions
   - Adjust bulk insert strategies
   - Review query patterns and index usage
   - Consider collection design changes

#### Iteration Process

1. **Identify Issues**: Use validation output to pinpoint problems
2. **Root Cause Analysis**: Determine if issue is in schema, seeder, or configuration
3. **Fix and Test**: Make targeted changes and test locally
4. **Re-run Validation**: Execute full validation suite again
5. **Document Changes**: Track what was changed and why

### 5. Success Criteria

The seed and iteration process is complete when:

- [ ] All collections are created with expected document counts
- [ ] All documents validate against their Pydantic schemas
- [ ] All indexes are created and functioning
- [ ] Referential integrity is maintained across collections
- [ ] Data quality meets realism and variety requirements
- [ ] No schema validation errors occur
- [ ] Sample queries execute efficiently

### 6. Output Documentation

Create a final validation report that includes:

1. **Database Summary**
   - Database name and collection list
   - Document counts per collection
   - Index summary and performance metrics

2. **Data Quality Report**
   - Sample documents from each collection
   - Validation results and any warnings
   - Data distribution analysis

3. **Performance Metrics**
   - Seeding duration and throughput
   - Index creation times
   - Sample query performance

### 7. Cleanup and Finalization

After successful validation:

1. **Optional**: Create a database backup/dump for reuse
2. **Document**: Update README with usage instructions
3. **Export**: Provide connection details and sample queries
4. **Clean**: Remove any temporary files or test data

## Error Handling

Handle common error scenarios gracefully:

- **Connection failures**: Provide clear MongoDB setup instructions
- **Permission errors**: Guide on database user permissions
- **Memory issues**: Suggest reducing seed data volume
- **Timeout errors**: Implement retry logic and progress indicators
- **Validation failures**: Provide detailed error messages and suggestions

## Example Validation Script

```python
def validate_database_health(seeder, pydantic_models):
    """
    Comprehensive database health check after seeding using built-in validation
    """
    
    # Use the built-in comprehensive validation method
    validation_results = seeder.validate_schema_and_indexes(
        sample_size=10,
        pydantic_models=pydantic_models
    )
    
    # Extract key metrics for reporting
    summary = validation_results['validation_summary']
    
    print("🔍 Database Health Check Results:")
    print(f"  • Overall Success: {'✅' if summary['overall_success'] else '❌'}")
    print(f"  • Collections: {summary['total_collections']}")
    print(f"  • Schema Validation: {summary['schema_validation_passed']}/{summary['total_collections']} passed")
    print(f"  • Index Validation: {summary['index_validation_passed']}/{summary['total_collections']} passed")
    print(f"  • Documents Sampled: {summary['total_documents_sampled']}")
    print(f"  • Validation Errors: {summary['total_validation_errors']}")
    
    # Show detailed results for collections with issues
    for collection_name, result in validation_results['collection_results'].items():
        if not result['schema_validation']['passed'] or not result['index_validation']['passed']:
            print(f"\n❌ Issues found in '{collection_name}':")
            
            if not result['schema_validation']['passed']:
                print(f"  Schema Errors ({len(result['schema_validation']['errors'])}):")
                for error in result['schema_validation']['errors'][:3]:  # Show first 3
                    print(f"    • {error}")
            
            if not result['index_validation']['passed']:
                print(f"  Index Errors ({len(result['index_validation']['errors'])}):")
                for error in result['index_validation']['errors']:
                    print(f"    • {error}")
    
    return validation_results

# Usage in main.py
if __name__ == "__main__":
    # Import your models
    from db_schema import Facility, Product, User  # etc.
    
    pydantic_models = {
        "facilities": Facility,
        "products": Product, 
        "users": User,
        # ... map all collections
    }
    
    # Run comprehensive validation
    results = validate_database_health(seeder, pydantic_models)
    
    if results['validation_summary']['overall_success']:
        print("✅ Database validation passed!")
    else:
        print("❌ Database validation failed!")
        exit(1)
```

This comprehensive approach ensures reliable database generation with proper validation and iteration capabilities.