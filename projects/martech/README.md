# DataTech Platform - MarTech Customer Data Platform

A comprehensive MongoDB database designed for MarTech customer data platforms, supporting flexible customer profiles, multi-channel tracking, campaign management, and social CRM capabilities.

## Overview

This database was generated using the Mimoid workflow from a MarTech company case study. It provides a flexible, scalable foundation for customer data platforms that need to handle:

- **Dynamic customer profiles** with custom fields and attributes
- **Multi-channel event tracking** across web, mobile, email, and social platforms  
- **Campaign management** and performance tracking
- **Customer segmentation** for targeted marketing
- **Social CRM** integration across multiple platforms
- **Data source management** and quality monitoring

## Database Schema

### Collections

| Collection | Purpose | Key Features |
|-----------|---------|--------------|
| **customers** | Core customer profiles | Flexible custom fields, computed LTV/engagement scores, consent management |
| **events** | Behavioral tracking | Multi-channel events, session tracking, campaign attribution |
| **campaigns** | Marketing campaigns | Multi-type campaigns, performance metrics, targeting criteria |
| **segments** | Customer groupings | Dynamic segmentation, criteria-based filtering |
| **social_members** | Social platform data | Multi-platform profiles, engagement metrics |
| **data_sources** | Integration monitoring | Connection health, data quality tracking |

### Key Design Patterns

- **Flexible Schema**: Customer custom fields support varying business requirements
- **Event-Driven Architecture**: Comprehensive behavioral tracking with proper indexing
- **Computed Values**: Pre-calculated engagement scores and lifetime values
- **Referential Integrity**: Proper relationships maintained across collections
- **Performance Optimized**: Strategic indexes for common query patterns

## Sample Data

The database contains realistic sample data including:

- **1,000 customers** with diverse profiles and custom attributes
- **50,000 events** across multiple event types and time periods
- **25 campaigns** with performance metrics and targeting data
- **15 segments** for customer categorization
- **300 social profiles** across major platforms
- **8 data sources** with quality monitoring

### Event Distribution

- Page views (40%)
- Email interactions (30%)
- Purchases (5%)
- Form submissions (10%)
- Campaign interactions (8%)
- Social activities (4%)
- Authentication events (3%)

## Getting Started

### Prerequisites

- MongoDB 4.4+ running locally or accessible via connection string
- Python 3.11+
- Required dependencies (installed via the parent mimoid project)

### Running the Database Setup

```bash
# Navigate to the project directory
cd projects/martech

# Run the main setup script
python main.py
```

The setup process will:
1. Validate MongoDB connection and schema
2. Seed all collections with sample data
3. Create optimized indexes
4. Run validation checks
5. Generate a summary report

### Connection Details

- **Database Name**: `martech`
- **Default Connection**: `mongodb://localhost:27017`
- **Override via Environment**: Set `MONGODB_URI` environment variable

## Key Queries

### Customer Lookup
```javascript
// Find customer by email
db.customers.findOne({email: "customer@example.com"})

// Search customers by engagement score
db.customers.find({engagement_score: {$gte: 70}}).sort({lifetime_value: -1})

// Find customers with specific tags
db.customers.find({tags: {$in: ["vip", "high-value"]}})
```

### Event Analysis
```javascript
// Customer activity timeline
db.events.find({customer_id: ObjectId("...")}).sort({timestamp: -1})

// Campaign performance events
db.events.find({campaign_id: ObjectId("..."), event_type: "email_click"})

// Recent high-value purchases
db.events.find({
  event_type: "purchase",
  "properties.amount": {$gte: 100}
}).sort({timestamp: -1})
```

### Campaign Insights
```javascript
// Active campaigns with metrics
db.campaigns.find({status: "active"}, {name: 1, metrics: 1})

// Campaign ROI analysis
db.campaigns.find({"metrics.revenue": {$exists: true}}).sort({"metrics.revenue": -1})
```

### Segmentation
```javascript
// Dynamic segment recalculation
db.customers.find({
  engagement_score: {$gte: 60},
  last_activity_date: {$gte: new Date("2024-01-01")}
}).count()

// High-value customer segment
db.customers.find({
  lifetime_value: {$gte: 1000},
  tags: {$in: ["customer", "vip"]}
})
```

## Performance Considerations

### Indexes

The database includes optimized indexes for:
- Customer email and phone lookups (unique)
- Event queries by customer and timestamp
- Campaign performance analysis
- Text search on customer names
- Social platform user lookups
- Segment calculation queries

### Scaling Recommendations

- **Events Collection**: Consider time-based sharding for high-volume deployments
- **Customer Collection**: Index custom fields based on actual query patterns
- **Campaign Analytics**: Implement aggregation pipelines for complex reporting
- **Data Archival**: Set up TTL indexes for old event data if needed

## Data Quality

### Validation Features

- **Schema Validation**: Pydantic models enforce data types and constraints
- **Referential Integrity**: Foreign key relationships are validated
- **Data Source Tracking**: All records track their origin for audit purposes
- **Quality Scores**: Data sources include quality metrics and error tracking

### Privacy & Compliance

- **Consent Management**: Customer preferences and consent flags
- **Data Retention**: Configurable data lifecycle management
- **Anonymization Ready**: Schema supports PII tokenization if needed

## Use Cases

This database supports typical MarTech platform scenarios:

1. **Customer 360**: Unified view of customer across all touchpoints
2. **Behavioral Segmentation**: Dynamic customer grouping based on actions
3. **Campaign Attribution**: Track marketing effectiveness across channels
4. **Social CRM**: Integrate social media interactions with customer profiles
5. **Predictive Analytics**: Use engagement scores and behavior for predictions
6. **Data Integration**: Monitor and manage multiple data sources

## Development

### Schema Evolution

The flexible design supports schema changes:
- Add new custom fields without migration
- Extend event properties for new event types
- Update campaign types and metrics as needed

### Testing Queries

Sample customers include varied profiles for testing:
- Different engagement levels (0-100)
- Various lifetime values ($0-$5000+)
- Multiple industries and company sizes
- Diverse tag combinations

## Support

For questions about this database or the Mimoid workflow:
- Review the technical design document (`tech_design.md`)
- Check the schema definitions (`db_schema.py`)
- Examine the seeding logic (`seed_db.py`)

---

*Generated using Mimoid - MongoDB database generation from natural language*