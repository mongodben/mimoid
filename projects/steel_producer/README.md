# MetaSteel Industries - Global Product Quality System (GPQS) Database

A comprehensive MongoDB database system for steel production quality management, inspired by ArcelorMittal's global quality control initiative. This system manages quality checkpoints, defect tracking, production monitoring, and compliance across multiple steel manufacturing facilities worldwide.

## Overview

The Global Product Quality System (GPQS) is designed to centralize and manage quality data from steel production facilities around the world. It handles high-volume sensor data, defect detection, laboratory test results, and customer specifications while maintaining full traceability from raw materials to finished products.

### Key Features

- **Multi-Facility Support**: Manages data from integrated mills, mini-mills, finishing plants, and research centers globally
- **High-Volume Time-Series Data**: Handles up to 50,000 quality checkpoints with real-time sensor readings
- **AI-Powered Defect Detection**: Integrates computer vision and deep learning for automated quality inspection
- **Complete Traceability**: Tracks materials from heat number through production to customer delivery
- **Compliance Management**: Maintains customer specifications and regulatory requirements
- **Performance Analytics**: Pre-computed quality metrics and cross-facility benchmarking

## Database Architecture

### Collections Overview

| Collection | Documents | Purpose |
|------------|-----------|---------|
| `facilities` | 8 | Global steel production facilities |
| `production_lines` | 40 | Manufacturing lines with equipment configs |
| `products` | 25 | Steel product catalog and specifications |
| `production_batches` | 500 | Manufacturing batches with traceability |
| `quality_checkpoints` | 50,000 | Time-series sensor measurements |
| `defects` | 2,500 | Quality issues and corrective actions |
| `test_results` | 5,000 | Laboratory test results and certificates |
| `customer_specifications` | 15 | Customer quality requirements |

### Data Relationships

```
Facility (1:N) → Production Lines (1:N) → Production Batches
    ↓                    ↓                        ↓
Products (1:N) → Production Batches (1:N) → Quality Checkpoints
                        ↓                        ↓
                    Defects ←→ Quality Checkpoints
                        ↓
                  Test Results
```

## Quick Start

### Prerequisites

- MongoDB 4.4+ (local installation or MongoDB Atlas)
- Python 3.8+
- UV package manager (recommended) or pip

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd projects/steel_producer/
   ```

2. **Set up environment variables:**
   ```bash
   # Optional: Set custom MongoDB connection
   export MONGODB_URI="mongodb://localhost:27017"
   
   # Optional: Enable debug logging
   export DEBUG=true
   ```

3. **Install dependencies (if running independently):**
   ```bash
   pip install pymongo faker pydantic bson
   ```

### Running the Database Setup

#### Basic Setup
```bash
# Run with default settings
uv run python main.py
```

#### Custom Configuration
```bash
# Custom MongoDB connection
MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/" uv run python main.py

# Custom record counts
CUSTOM_RECORD_COUNTS="facilities=5,products=10,batches=100" uv run python main.py

# Enable debug logging
DEBUG=true uv run python main.py
```

The setup process will:
1. ✅ Test MongoDB connection and system resources
2. 🗑️ Clear existing data (if any)
3. 📊 Generate realistic sample data across all collections
4. 🗂️ Create performance-optimized indexes
5. 🔍 Validate data integrity and relationships
6. 📋 Provide detailed completion report

**Expected Output:**
```
🔥 MetaSteel Industries - Global Product Quality System
============================================================
Starting database setup process...

🔍 Running pre-flight checks...
  • Testing MongoDB connection... ✅
  • Checking system resources... ✅
  • Checking database state... ✅ (Clean database)

🌱 Seeding database with sample data...
  • Total records to generate: 58,088
  • Seeding completed in 1.7 seconds
  • Average: 35,155 records/second

✅ Database setup completed successfully!
```

## Database Schema Details

### Core Entities

#### Facilities
Global steel production facilities with location, capacity, and certification information.
```javascript
{
  "_id": ObjectId,
  "facility_name": "MetaSteel Plant 1",
  "facility_code": "MSI-001",
  "facility_type": "integrated_mill",
  "country": "United States",
  "city": "Pittsburgh",
  "annual_capacity_tons": 8500000,
  "iso_certifications": ["ISO 9001", "ISO 14001"],
  "is_active": true
}
```

#### Production Lines
Manufacturing lines with equipment configurations and performance metrics.
```javascript
{
  "_id": ObjectId,
  "facility_id": ObjectId,
  "line_name": "Production Line 1",
  "line_code": "PL-001",
  "product_types": ["hot_rolled_coil", "cold_rolled_coil"],
  "max_width_mm": 1800,
  "production_speed_mpm": 12.5,
  "efficiency_percent": 92.3,
  "equipment_list": [...],
  "status": "operational"
}
```

#### Quality Checkpoints (Time-Series)
High-volume sensor measurements with real-time quality data.
```javascript
{
  "_id": ObjectId,
  "facility_id": ObjectId,
  "batch_id": ObjectId,
  "checkpoint_type": "temperature_measurement",
  "measurement_timestamp": ISODate,
  "sensor_readings": {
    "pyrometer_1": 1235.5,
    "pyrometer_2": 1240.2
  },
  "quality_score": 97.8,
  "pass_fail_status": "pass"
}
```

#### Defects
AI-powered defect detection with root cause analysis.
```javascript
{
  "_id": ObjectId,
  "defect_type": "surface_defect",
  "severity": "major",
  "detection_method": "automated_vision",
  "ai_confidence": 94.5,
  "probable_cause": "roll_wear",
  "economic_impact_usd": 2500,
  "material_disposition": "rework"
}
```

## Usage Examples

### MongoDB Connection
```bash
# Connect to the database
mongo mongodb://localhost:27017/metasteel_gpqs

# Or with MongoDB Compass
mongodb://localhost:27017
```

### Common Queries

#### 1. Facility Overview
```javascript
// View all active facilities
db.facilities.find(
  { "is_active": true },
  { 
    "facility_name": 1, 
    "country": 1, 
    "annual_capacity_tons": 1 
  }
).pretty()
```

#### 2. Production Performance Analysis
```javascript
// Average quality scores by facility
db.production_batches.aggregate([
  {
    $group: {
      _id: "$facility_id",
      avg_quality: { $avg: "$overall_quality_score" },
      batch_count: { $sum: 1 }
    }
  },
  { $sort: { avg_quality: -1 } }
])
```

#### 3. Defect Analysis
```javascript
// Defect distribution by type and severity
db.defects.aggregate([
  {
    $group: {
      _id: {
        type: "$defect_type",
        severity: "$severity"
      },
      count: { $sum: 1 },
      avg_economic_impact: { $avg: "$economic_impact_usd" }
    }
  },
  { $sort: { count: -1 } }
])
```

#### 4. Quality Trend Analysis
```javascript
// Quality checkpoints over time
db.quality_checkpoints.aggregate([
  {
    $match: {
      "measurement_timestamp": {
        $gte: ISODate("2024-01-01"),
        $lte: ISODate("2024-12-31")
      }
    }
  },
  {
    $group: {
      _id: {
        $dateToString: { format: "%Y-%m", date: "$measurement_timestamp" }
      },
      avg_quality: { $avg: "$quality_score" },
      checkpoint_count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])
```

#### 5. Product Quality Compliance
```javascript
// Test results compliance rate
db.test_results.aggregate([
  {
    $group: {
      _id: "$test_method",
      total_tests: { $sum: 1 },
      passed_tests: {
        $sum: { $cond: [{ $eq: ["$pass_fail_status", "pass"] }, 1, 0] }
      }
    }
  },
  {
    $project: {
      test_method: "$_id",
      compliance_rate: { 
        $multiply: [{ $divide: ["$passed_tests", "$total_tests"] }, 100] 
      }
    }
  }
])
```

#### 6. Customer Specifications
```javascript
// Active customer requirements
db.customer_specifications.find(
  { 
    "is_active": true,
    "effective_date": { $lte: new Date() }
  },
  {
    "customer_name": 1,
    "product_family": 1,
    "quality_level": 1,
    "required_tests": 1
  }
).pretty()
```

## Data Patterns and Design Decisions

### 1. Time-Series Optimization
Quality checkpoints use MongoDB's time-series collection patterns:
- **High-volume writes**: Optimized for 50K+ daily measurements
- **Time-based queries**: Efficient range queries by timestamp
- **Batch processing**: Bulk insertions for better performance

### 2. Referential Integrity
Maintains data relationships while allowing independent scaling:
- **Facility → Lines**: One facility has multiple production lines
- **Batch → Checkpoints**: Each batch has hundreds of quality measurements
- **Product → Specifications**: Products linked to customer requirements

### 3. Computed Values
Pre-calculated metrics for dashboard performance:
- **Quality scores**: Aggregated from checkpoint measurements
- **Defect rates**: Computed per facility and product type
- **Efficiency metrics**: Rolling averages for production lines

### 4. Flexible Schema
Handles varying steel grades and customer requirements:
- **Chemical composition**: Dynamic element percentages
- **Customer specifications**: Flexible requirement structures
- **Process parameters**: Adaptable to different production methods

## Performance Characteristics

### Data Volume Capacity
- **Daily checkpoints**: 50,000+ measurements
- **Annual capacity**: ~18M quality records
- **Batch processing**: 1,000 documents per insert operation
- **Query performance**: Sub-second response for most operations

### Index Strategy
Optimized indexes for common access patterns:
- **Time-series queries**: Timestamp + facility/line combinations
- **Traceability**: Batch number and heat number lookups
- **Quality analysis**: Defect type and severity combinations
- **Compliance**: Customer specification and test method indexes

### Storage Estimates
Based on sample data generation:
- **Total documents**: ~58,000
- **Database size**: ~45 MB (sample dataset)
- **Production estimate**: ~2-5 GB annually per facility

## Integration Points

### External Systems
The GPQS database integrates with:
- **ERP Systems**: Production planning and inventory management
- **LIMS**: Laboratory Information Management Systems
- **Vision Systems**: Automated defect detection cameras
- **Process Control**: Real-time production parameter systems
- **Customer Portals**: Quality reporting and certification delivery

### API Patterns
Common integration patterns:
```javascript
// Real-time checkpoint insertion
db.quality_checkpoints.insertMany(sensorBatch)

// Defect notification workflow
db.defects.find({ 
  "customer_notification_required": true,
  "resolution_timestamp": null 
})

// Batch quality summary
db.production_batches.aggregate([...qualitySummaryPipeline])
```

## Quality Control Features

### 1. Automated Defect Detection
- **Computer Vision**: Surface defect identification
- **AI Confidence Scoring**: Machine learning reliability metrics
- **Image Analysis**: Defect size and severity assessment

### 2. Statistical Process Control
- **Control Charts**: Real-time quality trend monitoring
- **Specification Limits**: Automated pass/fail determination
- **Correlation Analysis**: Process parameter impact on quality

### 3. Traceability System
- **Heat Number Tracking**: From melting to delivery
- **Batch Genealogy**: Complete production history
- **Material Flow**: Raw material to finished product mapping

### 4. Compliance Management
- **Customer Specifications**: Automated requirement checking
- **Test Certificates**: Laboratory result documentation
- **Audit Trails**: Complete quality decision history

## Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Test MongoDB connection
mongo mongodb://localhost:27017/metasteel_gpqs --eval "db.runCommand('ping')"
```

#### Memory Issues
```bash
# Reduce record counts for testing
CUSTOM_RECORD_COUNTS="facilities=2,products=5,batches=50" uv run python main.py
```

#### Performance Optimization
```javascript
// Check index usage
db.quality_checkpoints.explain("executionStats").find({
  "facility_id": ObjectId("..."),
  "measurement_timestamp": { $gte: ISODate("2024-01-01") }
})
```

### Data Validation
The system includes comprehensive validation:
- **Schema compliance**: Pydantic model validation
- **Referential integrity**: Foreign key relationship checks
- **Data distribution**: Quality score and defect rate verification
- **Index performance**: Query execution time monitoring

## Development and Extension

### Adding New Collections
1. **Define Pydantic model** in `db_schema.py`
2. **Add collection schema** with indexes
3. **Implement seeder method** in `seed_db.py`
4. **Update validation logic** for relationships

### Custom Data Patterns
```python
# Example: Adding equipment sensors
class EquipmentSensor(BaseMongoDbDocumentSchema):
    equipment_id: str
    sensor_type: SensorType
    reading_value: float
    calibration_date: datetime
    # ... additional fields
```

### Performance Tuning
```python
# Batch size optimization
CHECKPOINT_BATCH_SIZE = 1000  # Adjust based on memory
BULK_INSERT_TIMEOUT = 30000   # 30 second timeout
```

## License and Compliance

This database schema is designed for educational and development purposes, modeling real-world steel production quality systems. It includes realistic data patterns for:

- **Quality management standards** (ISO 9001, ISO 14001)
- **Steel industry specifications** (ASTM, EN, JIS standards)
- **Traceability requirements** (Heat numbers, batch tracking)
- **Customer compliance** (Automotive, construction, energy sectors)

## Support and Documentation

### Additional Resources
- **MongoDB Documentation**: [docs.mongodb.com](https://docs.mongodb.com)
- **Steel Industry Standards**: ASTM, EN, JIS specifications
- **Quality Management**: ISO 9001 implementation guides

### Sample Data Sources
The realistic sample data is generated using:
- **Faker library**: Realistic names, addresses, dates
- **Industry standards**: Actual steel grades and specifications
- **Statistical distributions**: Realistic quality score patterns
- **Process parameters**: Typical steel production values

---

*This database represents a comprehensive quality management system for global steel production, designed to handle high-volume sensor data, automated defect detection, and complete production traceability from raw materials to customer delivery.*