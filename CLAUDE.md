# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mimoid is a MongoDB database generation tool that uses agentic LLM workflows to create well-designed database schemas and sample data from natural language inputs. The system takes business descriptions, use cases, or existing database information and generates complete MongoDB databases with realistic sample data.

## Core Architecture

### Base Framework (`mimoid/` package)
- **schema_types.py**: Core Pydantic models and MongoDB-specific types including `BaseMongoDbSchema`, `IndexDefinition`, `PyObjectId`, and document base classes
- **seeder_base.py**: Abstract `DatabaseSeeder` class that all concrete seeders must implement
- **__init__.py**: Exposes all base types for use in generated projects

### Workflow Structure (1 agent per step)
The system follows a 6-step workflow documented in individual markdown files:
1. **Technical Design**: Analyze input and create workload tables and relationship maps
   - Map the input to a technical design (create `tech_design.md`).
   - Use the `tech-design-generator` agent
2. **Database Architecture**: Generate Pydantic models and MongoDB schema definitions  
   - Generate the MongoDB schema and indexes (create `db_schema.py`). 
   - Use the `db-architecture-generator` agent
3. **Seed Database**: Create realistic sample data with proper referential integrity
   - Generate sample data (create `seed_db.py`)
   - Use the `seed-db-generator` agent
4. **Run and Iterate**: Execute seeding with validation and error handling
   - Use the `run-iterate-agent` agent
   - Run seed an iterate.
5. **Document Database**: Generate comprehensive documentation and usage examples
   - Document the database (create `README.md`)
   - Use the `database-documenter` agent
6. **API Server Generation**: Generate FastAPI server with OpenAPI specification
   - Generate REST API server (create `server.py`, `openapi.yml`, `test_api.py`)
   - Use the `api-server-generator` agent

Before you being create a new directory for the project within the `projects` directory of this repository. E.g. `projects/my_project/`


### Generated Projects (`projects/` directory)
Each generated database lives in its own subdirectory with standardized files:
- `tech_design.md` - Technical analysis and design decisions
- `db_schema.py` - Pydantic models and MongoDB schema using mimoid base types
- `seed_db.py` - Concrete DatabaseSeeder implementation with realistic data generation
- `main.py` - Execution script with pre-checks, seeding, validation, and reporting
- `README.md` - Complete database documentation with usage examples

In the end the directory should contain the following files:

```
...other stuff in repo...
projects/my_project/
├── tech_design.md
├── db_schema.py
├── seed_db.py
├── main.py
├── README.md
├── server.py
├── openapi.yml
└── test_api.py
```


## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies  
uv sync --extra dev

# Set up environment variables
cp .env.example .env
# Edit .env with your MongoDB connection string
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_schema_types.py

# Run with verbose output
uv run pytest tests/ -v
```

### Running Generated Databases
```bash
# Execute a generated database project
cd projects/project_name
uv run python main.py

# With custom MongoDB URI
MONGODB_URI="mongodb://custom:27017" uv run python main.py

# Example: Run the digital lending platform
cd projects/digital_bank
uv run python main.py
```

## Database Generation Workflow

### Creating New Database Projects
1. **Input Preparation**: Place business description, use case, or existing schema info in a markdown file
2. **Project Directory**: Create `projects/new_project_name/` directory
3. **Follow 6-Step Process**: Implement each step following the detailed instructions for each agent in the `.claude/agents` directory
4. **Import Requirements**: All generated files must import from mimoid package:
   ```python
   # For schema files (db_schema.py)
   from mimoid import (
       BaseMongoDbSchema, BaseCollectionSchema, BaseMongoDbDocumentSchema,
       IndexDefinition, IndexDirection, PyObjectId, DatabaseSeeder
   )
   
   # For API generation (server.py)
   from mimoid import (
       ApiGenerator, OpenApiGenerator, ApiValidator
   )
   ```

### Schema Design Patterns
- **Flexible Custom Fields**: Use `Dict[str, Any]` for dynamic customer attributes
- **Event-Driven Architecture**: Separate high-volume time-series data into dedicated collections
- **Computed Values**: Pre-calculate metrics like engagement scores and lifetime values
- **Referential Integrity**: Maintain proper relationships using PyObjectId references
- **Performance Optimization**: Strategic compound indexes for common query patterns

### Data Generation Best Practices
- **Realistic Distributions**: Use weighted random choices and statistical distributions
- **Temporal Consistency**: Generate time-series data with proper chronological relationships  
- **Bulk Operations**: Insert large datasets in batches (typically 1000 documents per batch)
- **Validation**: Implement comprehensive validation including referential integrity checks
- **Error Handling**: Graceful handling of MongoDB connection issues and duplicate key errors

## Environment Configuration

### Required Variables
- `MONGODB_URI`: MongoDB connection string

## Key Implementation Notes

### Pydantic V2 Compatibility
All schema definitions use Pydantic V2 with:
- `model_config` instead of `Config` class
- `@field_validator` instead of `@validator`
- Modern core schema validation for PyObjectId

### MongoDB Integration
- Uses `pymongo` for database operations
- Implements proper index creation with error handling for unique constraint violations
- Supports both local MongoDB and MongoDB Atlas connections
- Includes comprehensive validation of seeded data

### Faker Integration
Extensive use of Faker library for realistic data generation with custom patterns for:
- Business-specific data (industries, company sizes, job titles)
- Marketing data (campaign types, engagement metrics, event tracking)
- Social platform data (usernames, follower counts, engagement rates)
- Time-series data with proper temporal relationships
- Financial services data (loan applications, credit scores, payment methods)
- Alternative credit data (social media profiles, device information, behavioral patterns)
