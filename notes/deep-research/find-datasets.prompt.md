# Deep Research Prompt: Finding Datasets for Mimoid

## Context for Research Agent

You are researching data sources for **Mimoid**, a MongoDB database generation tool that uses AI agents to create complete database systems from natural language descriptions. Here's what you need to know about the project:

### What Mimoid Does
Mimoid is a 6-step workflow system that:
1. **Technical Design** - Analyzes business requirements and creates database architecture plans
2. **Database Architecture** - Generates MongoDB schema with Pydantic models and indexes
3. **Seed Database** - Creates realistic sample data with proper relationships
4. **Run and Iterate** - Executes seeding with validation and error handling
5. **Document Database** - Generates comprehensive documentation
6. **API Server Generation** - Creates FastAPI servers with OpenAPI specifications

### Current Project Scope
Mimoid currently has these example projects:
- **1Password Events API** - Security event monitoring and audit trails
- **Amadeus Flight API** - Travel booking and flight search systems
- **Digital Banking** - Loan applications, credit scoring, financial services
- **EdTech Platform** - Educational content, student progress, course management
- **Food Delivery** - Restaurant management, order processing, delivery tracking
- **MarTech** - Marketing campaigns, customer analytics, engagement tracking
- **Steel Producer** - Industrial manufacturing, inventory, quality control

### What We Need From You

Research and identify **high-quality datasets and APIs** that would make excellent source material for creating new Mimoid database projects. Focus on finding data sources that have these characteristics:

## Research Criteria

### Essential Requirements
1. **Rich Relational Data** - Multiple interconnected entities with foreign key relationships
2. **Real Business Logic** - Reflects actual operational workflows and constraints
3. **Temporal Patterns** - Time-series data, historical tracking, state changes
4. **Realistic Scale** - Large enough datasets to demonstrate performance considerations
5. **Public Accessibility** - Available via API, open data, or downloadable datasets

### Preferred Characteristics
- **Multiple data formats** (JSON, CSV, API endpoints)
- **Geographic components** for location-based queries
- **User-generated content** with natural variation and quality differences
- **Hierarchical structures** (categories, organizations, taxonomies)
- **Event streams** (transactions, logs, user interactions)
- **Compliance considerations** (regulatory requirements, audit trails)

### Industries of Interest
Please prioritize these sectors (but don't limit yourself to them):

**High Priority:**
- **Healthcare & Medical** - Patient records, clinical trials, medical devices
- **Supply Chain & Logistics** - Shipping, warehousing, procurement, tracking
- **Financial Services** - Trading, payments, lending, risk management
- **Real Estate** - Property management, transactions, market analysis
- **Manufacturing** - Production planning, quality control, maintenance
- **Energy & Utilities** - Grid management, consumption tracking, renewable energy

**Medium Priority:**
- **Media & Entertainment** - Content management, streaming, social platforms
- **Government & Civic** - Public services, regulations, civic engagement
- **Transportation** - Fleet management, route optimization, vehicle tracking
- **Agriculture** - Crop management, livestock, supply chain
- **Sports & Recreation** - Player statistics, team management, fan engagement
- **Insurance** - Claims processing, risk assessment, policy management

## Research Tasks

### 1. Dataset Discovery
For each promising data source you find, provide:

- **Source Name & URL**
- **Data Description** - What business domain it covers
- **Data Volume** - Approximate number of records/entities
- **Update Frequency** - Real-time, daily, historical snapshot
- **Access Method** - API, bulk download, web scraping
- **Licensing** - Usage rights and restrictions
- **Data Quality Assessment** - Completeness, accuracy, relationships

### 2. Relationship Mapping
For each dataset, identify:
- **Primary entities** and their key attributes
- **Relationships between entities** (one-to-many, many-to-many)
- **Potential MongoDB collections** that could be created
- **Index strategies** for common query patterns
- **Aggregation opportunities** for business intelligence

### 3. Business Value Assessment
Evaluate each dataset's potential for:
- **Teaching database design patterns** (embedded vs referenced documents)
- **Demonstrating query optimization** (compound indexes, aggregation pipelines)
- **Showcasing real-world constraints** (validation rules, business logic)
- **API generation potential** (interesting endpoints, filtering needs)

## Specific Research Areas

### Look for datasets that demonstrate:

**Complex Business Workflows:**
- Multi-step approval processes
- State machines and status tracking
- Role-based access patterns
- Audit trails and change history

**Performance Challenges:**
- High-volume transaction processing
- Time-series data with retention policies
- Geographic queries and spatial indexing
- Full-text search requirements

**Data Integration Scenarios:**
- Multiple related systems and data sources
- ETL pipeline requirements
- Data quality and validation challenges
- Schema evolution over time

## Output Format

For each dataset you recommend, provide this structured information:

```markdown
## [Dataset Name]

**Source:** [URL]  
**Domain:** [Business area]  
**Access:** [API/Download/Other]  
**License:** [Usage rights]

### Data Overview
- **Primary Entities:** [List main data types]
- **Record Count:** [Approximate volume]
- **Update Frequency:** [How often data changes]
- **Time Range:** [Historical coverage]

### Relationship Structure
- **Entity A** → **Entity B** (relationship type)
- [Map out key relationships]

### MongoDB Potential
- **Collections:** [Suggested collection structure]
- **Indexes:** [Recommended indexing strategy]
- **Queries:** [Common access patterns]

### Business Value
- **Use Cases:** [Real-world applications]
- **Complexity:** [Technical challenges it demonstrates]
- **Learning Value:** [What developers would learn]

### Implementation Notes
- **Data Quality:** [Known issues or considerations]
- **API Limitations:** [Rate limits, authentication]
- **Schema Challenges:** [Interesting design decisions]
```

## Research Targets

### Primary Focus Areas
1. **Find 10-15 high-quality datasets** across different industries
2. **Prioritize business complexity** over data volume
3. **Identify unique relationship patterns** not covered by existing projects
4. **Look for modern business models** (SaaS, marketplaces, platforms)

### Secondary Opportunities  
- **Industry-specific compliance** requirements (HIPAA, SOX, GDPR)
- **IoT and sensor networks** with streaming data patterns
- **Social platforms** with network effects and viral mechanics
- **Marketplaces** with multi-sided business models

## Success Criteria

Your research will be successful if it identifies datasets that:
1. **Enable creation of 5+ new diverse Mimoid projects**
2. **Demonstrate advanced MongoDB features** (aggregation, indexing, sharding)
3. **Showcase realistic business logic** and operational constraints
4. **Provide educational value** for database design learning
5. **Cover use cases not addressed** by current example projects

## Important Notes

- **Focus on publicly accessible data** - avoid datasets requiring special permissions
- **Verify data freshness** - prioritize actively maintained sources
- **Consider ethical implications** - ensure appropriate use of personal/sensitive data
- **Document any usage restrictions** - API limits, commercial use policies
- **Provide fallback options** - multiple sources per industry in case of access issues

This research will directly influence the next generation of Mimoid example projects and help developers learn modern database design patterns through realistic, hands-on examples.