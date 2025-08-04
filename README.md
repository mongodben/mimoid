# Mimoid

Mimoid is a project for creating MongoDB databases from natural language. It is designed to take a flexible natural language input and create a well-designed MongoDB database schema and sample data that is representative of the input.

Example inputs could include:
- Blog post about a business use case
- Product description
- Anonymized info about a a real database
- SQL database schema

## Run Mimoid

The Mimoid workflow 

Mimoid is a prompt workflow with some shared Python utilities in the `mimoid` package. It is optimized to be run with Claude Code. There are a series of Claude Code agents with custom system prompts to run the Mimoid workflow.

Other agentic code editor tools like OpenAI Codex, Windsurf, or GitHub CoPilot may work as well.

I give Claude Code a prompt like the following:

```
Take this input file <some_input_file.md> and use the Mimoid workflow to create the DB. Out to <some_output_dir>.

<Can add additional instructions here, if relevant>
```
## Flow 

The Mimoid workflow should follow this process:

1. [User] Create a new directory for the project within the `projects` directory of this repository. E.g. `projects/my_project/`
2. [User] Include some input file/files in the project directory. E.g. `projects/my_project/input.md`
3. [LLM] proceeds through the Mimoid workflow as follows:
   - [LLM] Step 1: Technical Design
   - [LLM] Step 2: Database Architecture
   - [LLM] Step 3: Seed Database
   - [LLM] Step 4: Run and Iterate
   - [LLM] Step 5: Database Documentation

Detailed information on each of these steps can be found in the [.claude/agents](.claude/agents) directory. There is a separate agent for each step.

The LLM outputs the files to `projects/my_project/`


In the end the directory should contain the following files:

```
...other stuff in repo...
projects/my_project/
├── tech_design.md
├── db_schema.py
├── seed_db.py
├── main.py
└── README.md
```

More information on each step can be found in the [`.claude/agents`](.claude/agents) directory.

## Development

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
