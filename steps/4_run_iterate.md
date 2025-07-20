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
def validate_database_health(db_schema, connection_string):
    """
    Comprehensive database health check after seeding
    """
    client = MongoClient(connection_string)
    db = client[db_schema.database_name]
    
    results = {
        'collections_created': [],
        'document_counts': {},
        'schema_validation': {},
        'index_validation': {},
        'referential_integrity': {}
    }
    
    # Check each collection
    for collection_name, schema in db_schema.collections.items():
        collection = db[collection_name]
        
        # Check existence and count
        if collection_name in db.list_collection_names():
            results['collections_created'].append(collection_name)
            results['document_counts'][collection_name] = collection.count_documents({})
        
        # Validate sample documents
        sample_docs = list(collection.find().limit(10))
        # ... validation logic ...
    
    return results
```

This comprehensive approach ensures reliable database generation with proper validation and iteration capabilities.