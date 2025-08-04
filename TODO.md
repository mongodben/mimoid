# TODO

- [ ] Create Docker environment for Mimoid to run.
  - Must support Running Claude Code (which is an NPM package)
  - Support Python with the required dependencies and `uv` as runner
  - Support setting up Claude Code with Anthropic key
  - Must support writing out the generated files to the `projects` directory, and then onto the host machine.
- [ ] Support Atlas Features, like Atlas Search/Vector Search.
  - Franktly this is probably already 'supported' b/c it can just write the code, but I think that I should create a new agent for this.
- [ ] API Server Generation Agent: Generate a FastAPI server with OpenAPI spec from the schema.
- [ ] Additional reference documentation for MongoDB database design.
  - Add some optional reference documentation that the model can refer to when architecting the DB. Refer to relevant bits of the reference documentation in the prompt files. 
- [ ] Evaluation of generated results for each step.
  - I have no idea how to evaluate this beast. \*waves hands\* LLM-as-a-judge...