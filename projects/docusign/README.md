# DocuSign MongoDB Database

A comprehensive MongoDB database schema and sample data generator for modeling DocuSign's electronic signature platform, based on the DocuSign REST API v2.1 OpenAPI specification.

## Overview

This project provides a complete MongoDB database implementation for DocuSign's core functionality including:
- Electronic signature workflows
- Document management
- Multi-party signing processes
- Template management
- Audit trails and compliance
- Account and user management
- Brand customization

## Database Schema

### Collections

1. **accounts** - DocuSign account information
   - Billing plans and usage limits
   - Account settings and features
   - Industry and company information

2. **users** - User accounts and permissions
   - Authentication and access control
   - User preferences and settings
   - Usage statistics

3. **envelopes** - Document containers for signature workflows
   - Lifecycle status tracking
   - Email notifications
   - Expiration and reminder settings

4. **documents** - Individual files within envelopes
   - PDF storage references
   - Form fields and tabs
   - Page-level metadata

5. **recipients** - People who interact with envelopes
   - Multiple recipient types (signers, viewers, etc.)
   - Authentication methods
   - Signing status and timestamps

6. **templates** - Reusable envelope configurations
   - Pre-defined documents and recipients
   - Role-based assignments
   - Usage tracking

7. **audit_events** - Comprehensive audit trail
   - All envelope and recipient events
   - Security and compliance tracking
   - Platform and device information

8. **brands** - Custom branding configurations
   - Colors and logos
   - Email customization
   - Signing page branding

9. **folders** - Organizational structure
   - System and custom folders
   - Sharing and permissions
   - Hierarchical organization

## Key Features

### Realistic Data Generation
- Industry-specific document types
- Weighted distributions for plans and statuses
- Temporal consistency in workflows
- Proper referential integrity

### Performance Optimization
- Strategic compound indexes for common queries
- Denormalized fields for performance
- Time-series optimized audit events
- Cursor-based pagination support

### Security Considerations
- Field-level encryption markers
- Authentication method tracking
- Audit trail for all actions
- Role-based access patterns

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   export MONGODB_URI="mongodb://localhost:27017"
   ```

## Usage

### Running the Database Seeder

```bash
cd projects/docusign
PYTHONPATH=/path/to/mimoid uv run python main.py
```

This will:
1. Connect to MongoDB
2. Create the database and indexes
3. Seed with realistic sample data
4. Validate the data
5. Generate a summary report

### Sample Output

```
Collection Summary:
----------------------------------------
accounts                     50 documents
users                       160 documents
brands                       22 documents
folders                     614 documents
templates                   281 documents
envelopes                 2,000 documents
documents                 4,130 documents
recipients                3,933 documents
audit_events             13,199 documents
Total                    24,389 documents
```

## Data Model Examples

### Envelope Document
```json
{
  "_id": ObjectId("..."),
  "envelope_id": "env_123456",
  "account_id": ObjectId("..."),
  "status": "completed",
  "email_subject": "Please sign: Service Agreement",
  "sender_user_id": ObjectId("..."),
  "created_date": ISODate("2024-01-15T10:30:00Z"),
  "sent_date": ISODate("2024-01-15T10:31:00Z"),
  "completed_date": ISODate("2024-01-15T14:45:00Z"),
  "recipient_count": 2,
  "signers_count": 2,
  "completed_signers": 2,
  "days_to_complete": 0
}
```

### Recipient Document
```json
{
  "_id": ObjectId("..."),
  "recipient_id": "rec_789012",
  "envelope_id": ObjectId("..."),
  "email": "john.doe@example.com",
  "name": "John Doe",
  "recipient_type": "signer",
  "routing_order": 1,
  "status": "completed",
  "authentication_methods": ["email", "sms"],
  "signed_date": ISODate("2024-01-15T12:30:00Z")
}
```

## Query Examples

### Find Active Envelopes for an Account
```javascript
db.envelopes.find({
  account_id: ObjectId("..."),
  status: { $in: ["sent", "delivered"] }
}).sort({ sent_date: -1 })
```

### Get Recipient Activity
```javascript
db.recipients.find({
  email: "user@example.com",
  status: "completed"
}).sort({ signed_date: -1 })
```

### Template Usage Analytics
```javascript
db.envelopes.aggregate([
  { $match: { template_id: { $ne: null } } },
  { $group: {
    _id: "$template_id",
    count: { $sum: 1 },
    avg_completion_days: { $avg: "$days_to_complete" }
  }},
  { $sort: { count: -1 } }
])
```

### Audit Trail for Envelope
```javascript
db.audit_events.find({
  envelope_id: ObjectId("...")
}).sort({ timestamp: 1 })
```

## Index Strategy

### Key Indexes

1. **Envelopes**
   - `(account_id, status, sent_date)` - Account dashboard queries
   - `(sender_user_id, status)` - User sent items
   - Text index on `email_subject` - Search functionality

2. **Recipients**
   - `(envelope_id, routing_order)` - Signing order
   - `(email, status, sent_date)` - Recipient history

3. **Audit Events**
   - `(envelope_id, timestamp)` - Envelope audit trail
   - `(event_type, timestamp)` - Event analytics

## Compliance and Security

### Audit Trail
- Every significant action is logged
- IP addresses and device information captured
- Authentication methods tracked
- Timestamps for all state changes

### Data Retention
- Configurable TTL indexes for expired envelopes
- Archive strategy for completed documents
- Compliance with 21 CFR Part 11 when enabled

## Performance Considerations

### Scaling Strategy
- Shard by `account_id` for horizontal scaling
- Time-series collections for audit events
- Separate hot/cold storage for documents

### Optimization Tips
- Use covered queries for dashboards
- Implement pagination with cursor-based approach
- Cache frequently accessed templates
- Use aggregation pipelines for reporting

## Development

### Running Tests
```bash
uv run pytest tests/
```

### Customizing Data Generation
Edit `seed_db.py` to modify:
- Number of records per collection
- Industry distributions
- Document types
- Workflow patterns

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check MongoDB is running
   - Verify connection string
   - Check network/firewall settings

2. **Validation Errors**
   - Review the log file for details
   - Check for missing required fields
   - Verify referential integrity

3. **Performance Issues**
   - Ensure indexes are created
   - Check query explain plans
   - Monitor collection sizes

## License

This project is part of the Mimoid MongoDB generation framework.