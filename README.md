# Mimiod

Mimiod is a project for creating MongoDB databases from natural language. It is designed to take a flexible natural language input and create a well-designed MongoDB database schema and sample data that is representative of the input.

Example inputs could include:
- Blog post about a business use case
- Product description
- Anonymized info about a a real database
- SQL database schema

## Flow 

The Mimiod workflow should follow this process.

Before you being create a new directory for the project within the `projects` directory of this repository. E.g. `projects/my_project/`

Within the directory, create the following files:

1. Map the input to a technical design (create `tech_design.md`).
   - More info in [steps/1_tech_design.md](./steps/1_tech_design.md)
2. Generate the MongoDB schema and indexes (create `db_schema.py`). 
   - More info in [steps/2_db_architecture.md](./steps/2_db_architecture.md)
3. Generate sample data (create `seed_db.py`)
   - More info in [steps/3_seed_db.md](./steps/3_seed_db.md)
4. Run seed an iterate.
   - More info in [steps/4_run_iterate.md](./steps/4_run_iterate.md)
5. Document the database (create `README.md`)
   - More info in [steps/5_document.md](./steps/5_document.md)

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

More information on each step can be found in the [`steps`](steps) directory.

More information on each step can be found in the [`steps`](steps) directory.
