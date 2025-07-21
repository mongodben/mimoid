# NeoLend Bank - Digital Lending Platform

A comprehensive MongoDB database designed for digital lending platforms specializing in microfinance for unbanked and underserved populations. Features AI-powered alternative credit scoring using both structured and unstructured data sources.

## Overview

This database was generated using the Mimoid workflow from a digital banking case study. It provides a complete foundation for microfinance platforms that need to:

- **Process alternative credit data** from social media, device behavior, and network analysis
- **Handle rapid loan approvals** with AI-powered decision making (24-hour turnaround)
- **Manage high-volume microloan operations** with amounts from $50-$1500
- **Track collections and compliance** for regulatory requirements
- **Support flexible data schemas** for evolving alternative data sources

## Database Schema

### Collections

| Collection | Purpose | Key Features |
|-----------|---------|--------------|
| **customers** | Customer profiles with alternative data | Flexible schema for social/behavioral data, AI credit scores, consent management |
| **loan_applications** | Loan application processing | Complete application data, device fingerprinting, AI scoring results |
| **loans** | Active and historical loans | Payment tracking, risk assessment, collections status |
| **payments** | Payment transactions | Multiple payment methods, mobile money integration |
| **credit_scores** | AI-generated credit assessments | Alternative data weighting, model versioning, confidence levels |
| **collection_cases** | Overdue loan management | Contact attempts, recovery strategies, agent assignment |
| **compliance_records** | Regulatory compliance tracking | Multi-regulation support, audit trails, reporting automation |

### Key Design Features

- **Alternative Credit Scoring**: Combines traditional data with social media, device behavior, and network analysis
- **Flexible Data Schema**: Handles varying unstructured data sources without schema migrations
- **High-Volume Processing**: Optimized for thousands of daily loan applications and payments
- **Mobile-First Architecture**: Indonesian payment methods (GoPay, OVO, DANA) and mobile money
- **Regulatory Compliance**: Built-in compliance tracking for multiple financial regulations
- **Collections Management**: Automated collections workflow with agent assignment

## Sample Data

The database contains realistic sample data including:

- **2,500 customers** with alternative credit profiles and behavioral data
- **4,000 loan applications** with AI-powered approval decisions
- **2,800 approved loans** across various terms and amounts
- **15,000 payment transactions** using diverse payment methods
- **5,000 credit score events** with AI model versioning
- **300 collection cases** for overdue loan management
- **800 compliance records** covering multiple regulations

### Alternative Data Sources

- **Social Media Analysis**: Facebook profile age, friends count, business-related posts
- **Behavioral Patterns**: App usage, form completion times, financial app installations
- **Device Intelligence**: Device value, age, model, installed apps count
- **Network Analysis**: Contact patterns, call duration, loan relationships

## Getting Started

### Prerequisites

- MongoDB 4.4+ running locally or accessible via connection string
- Python 3.11+
- Required dependencies (installed via the parent mimoid project)

### Running the Database Setup

```bash
# Navigate to the project directory
cd projects/digital_bank

# Run the main setup script
python main.py
```

The setup process will:
1. Validate MongoDB connection and schema
2. Seed all collections with realistic sample data
3. Create optimized indexes for loan processing
4. Run comprehensive validation checks
5. Generate a detailed summary report with AI scoring metrics

### Connection Details

- **Database Name**: `neolend_bank`
- **Default Connection**: `mongodb://localhost:27017`
- **Override via Environment**: Set `MONGODB_URI` environment variable

## Key Queries

### Customer and Credit Analysis
```javascript
// Find customers by credit score range
db.customers.find({
  current_credit_score: {$gte: 600, $lte: 750},
  risk_level: "medium"
}).sort({current_credit_score: -1})

// Customers with alternative data sources
db.customers.find({
  "social_media_data.facebook_friends_count": {$gt: 500},
  "device_data.device_value_usd": {$gt: 300}
})

// High-confidence credit scores using alternative data
db.credit_scores.find({
  confidence_level: {$gt: 0.8},
  alternative_data_weight: {$gt: 0.5}
}).sort({score: -1})
```

### Loan Application Processing
```javascript
// Recent applications awaiting review
db.loan_applications.find({
  status: "submitted",
  submitted_at: {$gte: new Date("2024-01-01")}
}).sort({submitted_at: -1})

// Approved loans by AI decision factors
db.loan_applications.find({
  status: "approved",
  "decision_factors.factor": "Alternative Data",
  "decision_factors.weight": {$gt: 0.2}
})

// Application approval rates by credit score range
db.loan_applications.aggregate([
  {$match: {credit_score: {$exists: true}}},
  {$bucket: {
    groupBy: "$credit_score",
    boundaries: [300, 500, 650, 750, 850],
    default: "Other",
    output: {
      total: {$sum: 1},
      approved: {$sum: {$cond: [{$eq: ["$status", "approved"]}, 1, 0]}}
    }
  }}
])
```

### Loan Portfolio Management
```javascript
// Active loans with payment issues
db.loans.find({
  status: "active",
  days_past_due: {$gt: 7},
  outstanding_balance: {$gt: 0}
}).sort({days_past_due: -1})

// Loan performance by risk level
db.loans.aggregate([
  {$group: {
    _id: "$current_risk_level",
    total_loans: {$sum: 1},
    avg_days_past_due: {$avg: "$days_past_due"},
    total_outstanding: {$sum: "$outstanding_balance"}
  }}
])

// Payment success rates by method
db.payments.aggregate([
  {$group: {
    _id: "$payment_method",
    total: {$sum: 1},
    completed: {$sum: {$cond: [{$eq: ["$status", "completed"]}, 1, 0]}}
  }},
  {$addFields: {success_rate: {$divide: ["$completed", "$total"]}}}
])
```

### Collections and Recovery
```javascript
// Active collection cases by agent
db.collection_cases.find({
  case_status: "open",
  assigned_agent: {$exists: true}
}).sort({current_debt: -1})

// Collection performance metrics
db.collection_cases.aggregate([
  {$match: {resolution_date: {$exists: true}}},
  {$group: {
    _id: "$resolution_type",
    cases: {$sum: 1},
    avg_recovery: {$avg: "$recovery_amount"},
    avg_days_to_resolve: {$avg: {$divide: [
      {$subtract: ["$resolution_date", "$opened_date"]},
      1000 * 60 * 60 * 24
    ]}}
  }}
])
```

## Performance Considerations

### Indexes

The database includes specialized indexes for:
- Customer phone number lookups (unique, primary identifier)
- Credit score time-series queries (customer + date)
- Loan status and due date management
- Payment processing by loan and customer
- Collection case management by status and agent
- Compliance reporting by regulation and period

### Alternative Credit Scoring Pipeline

1. **Data Collection**: Social media, device, behavioral, and network data
2. **Feature Engineering**: Normalize and weight alternative data sources
3. **AI Model Inference**: Multi-factor credit scoring with confidence levels
4. **Decision Engine**: Business rules overlay on AI recommendations
5. **Audit Trail**: Complete decision factors and model version tracking

### Mobile Payment Integration

Supports Indonesian digital payment ecosystem:
- **Digital Wallets**: GoPay, OVO, DANA integration
- **Mobile Money**: Direct carrier billing support
- **Cash Agents**: Physical payment collection points
- **Bank Transfers**: Traditional banking integration

## Use Cases

This database supports typical microfinance platform scenarios:

1. **Rapid Loan Approval**: 24-hour processing using AI credit scoring
2. **Alternative Credit Assessment**: Evaluate unbanked customers using non-traditional data
3. **High-Volume Processing**: Handle thousands of daily applications efficiently
4. **Mobile-First Experience**: Support smartphone-based lending in emerging markets
5. **Collections Automation**: Systematic approach to overdue loan recovery
6. **Regulatory Compliance**: Multi-jurisdiction regulatory reporting
7. **Risk Management**: Real-time fraud detection and portfolio monitoring

## Development

### Alternative Data Integration

The schema supports easy addition of new data sources:
```python
# Add new alternative data source
customer_update = {
    "$set": {
        "alternative_data.education_verification": {
            "institution": "University of Indonesia",
            "degree": "Bachelor's",
            "graduation_year": 2018,
            "verification_status": "verified"
        }
    }
}
```

### AI Model Evolution

Credit scoring models can be versioned and A/B tested:
```python
# Deploy new credit model version
credit_score = {
    "model_version": "v3.0.0",
    "model_features": {
        "social_graph_analysis": 0.15,  # New feature
        "transaction_velocity": 0.12,   # New feature
        "traditional_credit": 0.25,
        "alternative_behavioral": 0.48
    }
}
```

### Regulatory Adaptation

Easily add new compliance requirements:
```python
# Add new regulation tracking
compliance_record = {
    "regulation_name": "New Digital Lending Regulation 2024",
    "compliance_data": {
        "cooling_off_period_hours": 24,
        "max_interest_rate_percent": 25,
        "mandatory_disclosures": ["total_cost", "payment_schedule"]
    }
}
```

---

*Generated using Mimoid - MongoDB database generation from natural language*