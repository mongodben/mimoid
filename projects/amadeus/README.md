# Amadeus Flight Booking Database

A comprehensive MongoDB database system designed for flight search and booking operations, based on the Amadeus Flight Offers Search API v2.2.0 specification. This database supports high-volume flight booking platforms, travel agencies, and online travel retailers with realistic aviation data and booking workflows.

## 🌍 Overview

This database captures the complete ecosystem of modern flight booking, including:

- **Global Reference Data**: Airlines, aircraft, airports, and geographic information
- **Search Intelligence**: Flight search requests with pattern analysis
- **Dynamic Pricing**: Multi-currency flight offers with complex fare structures  
- **Booking Management**: Complete reservation lifecycle from search to ticketing
- **Operational Analytics**: Performance metrics and business intelligence

## ✈️ Database Schema

### Core Collections

#### Airlines (`airlines`)
Global airline directory with operational characteristics:
- IATA/ICAO codes and naming
- Alliance memberships and hub airports
- Fleet composition and route networks
- Service classifications (FSC, LCC, Regional)
- EU blacklist compliance status

#### Aircraft (`aircraft`)
Comprehensive aircraft specifications:
- IATA aircraft type codes
- Manufacturer and model information
- Passenger capacity by cabin class
- Performance characteristics (range, speed, fuel consumption)
- Environmental data (CO2 emissions, noise levels)

#### Airports (`airports`)
Worldwide airport directory:
- IATA/ICAO airport codes
- Geographic coordinates and timezone data
- Operational details (terminals, runways, passenger volume)
- Service amenities and ground transport options
- Hub relationships with airlines

#### Countries (`countries`)
Geographic reference data:
- ISO country codes and regional classifications
- Currency associations and language information
- Visa requirements and travel restrictions
- Major aviation hubs by country

#### Currencies (`currencies`)
Multi-currency support system:
- ISO 4217 currency codes and symbols
- Real-time exchange rates (USD base)
- Formatting preferences by region
- Major vs. minor currency classifications

### Transaction Collections

#### Search Requests (`search_requests`)
Flight search analytics and patterns:
- Origin/destination pairs with travel dates
- Passenger demographics and preferences
- Search performance metrics and response times
- Session tracking and user behavior analysis

#### Flight Offers (`flight_offers`)
Available flights with comprehensive pricing:
- Multi-segment itineraries with timing details
- Fare structures with taxes and fees breakdown
- Traveler-specific pricing by age category
- Booking conditions and fare restrictions
- Airline validation and operating carriers

#### Bookings (`bookings`)
Complete reservation management:
- PNR and confirmation number tracking
- Traveler manifest with contact information
- Payment processing and ticketing status
- Special service requests (meals, seats, assistance)
- Modification history and cancellation tracking

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB 4.4+ (local or Atlas)
- Required Python packages (installed via Mimoid)

### Installation & Setup

1. **Clone and Navigate**:
   ```bash
   cd projects/amadeus
   ```

2. **Environment Configuration**:
   ```bash
   # Copy environment template
   cp ../../../.env.example ../../../.env
   
   # Configure MongoDB connection
   export MONGODB_URI="mongodb://localhost:27017"
   # OR for MongoDB Atlas:
   # export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net"
   ```

3. **Database Creation**:
   ```bash
   # Execute the complete setup
   python main.py
   ```

### Quick Start Example

```python
from pymongo import MongoClient
import os

# Connect to database
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client["amadeus_flight_booking"]

# Find cheapest flights JFK -> LHR
cheap_flights = db.flight_offers.find({
    "itineraries.segments.departure.iataCode": "JFK",
    "itineraries.segments.arrival.iataCode": "LHR"
}).sort("total_price", 1).limit(5)

for flight in cheap_flights:
    print(f"${flight['total_price']:.2f} - {flight['validating_airline_codes'][0]}")
```

## 📊 Sample Data Overview

The database includes realistic aviation data with:

### Reference Data
- **100 Airlines**: Mix of major carriers (American, Lufthansa, Emirates) and regional airlines
- **50 Aircraft Types**: From regional jets to wide-body aircraft (A380, 777, A350)
- **200 Airports**: Global coverage including major hubs (JFK, LHR, DXB, SIN) 
- **50 Countries**: Complete geographic coverage with currency associations
- **20 Currencies**: Major world currencies with current exchange rates

### Transaction Data
- **10,000 Search Requests**: Realistic search patterns with seasonal variations
- **50,000 Flight Offers**: Dynamic pricing across routes and travel classes
- **5,000 Bookings**: Complete booking lifecycle from reservation to ticketing

### Data Characteristics
- **Realistic Pricing**: Market-based fare structures with taxes and fees
- **Geographic Distribution**: Weighted toward popular international routes
- **Temporal Patterns**: Seasonal demand variations and advance purchase patterns
- **Multi-Currency Support**: Local currency pricing for major markets

## 🔍 Query Examples

### 1. Popular Route Analysis
```javascript
db.search_requests.aggregate([
  {
    $group: {
      _id: { origin: "$origin_code", destination: "$destination_code" },
      search_count: { $sum: 1 },
      avg_passengers: { $avg: { $add: ["$adults", "$children", "$infants"] }}
    }
  },
  { $sort: { search_count: -1 }},
  { $limit: 10 }
])
```

### 2. Airline Revenue Analysis
```javascript
db.bookings.aggregate([
  {
    $group: {
      _id: "$validating_carrier",
      total_bookings: { $sum: 1 },
      total_revenue: { $sum: "$total_amount_paid" },
      avg_booking_value: { $avg: "$total_amount_paid" }
    }
  },
  { $sort: { total_revenue: -1 }},
  { $limit: 15 }
])
```

### 3. Aircraft Utilization by Route Type
```javascript
db.flight_offers.aggregate([
  {
    $lookup: {
      from: "aircraft",
      localField: "itineraries.segments.aircraft.code",
      foreignField: "iata_code",
      as: "aircraft_info"
    }
  },
  {
    $group: {
      _id: "$aircraft_info.manufacturer",
      flight_count: { $sum: 1 },
      avg_price: { $avg: "$total_price" },
      routes_served: { $addToSet: {
        origin: { $arrayElemAt: ["$itineraries.segments.departure.iataCode", 0] },
        destination: { $arrayElemAt: ["$itineraries.segments.arrival.iataCode", -1] }
      }}
    }
  },
  { $sort: { flight_count: -1 }}
])
```

### 4. Booking Conversion Funnel
```javascript
// Search to booking conversion analysis
db.search_requests.aggregate([
  {
    $lookup: {
      from: "flight_offers",
      localField: "_id",
      foreignField: "search_request_id",
      as: "offers"
    }
  },
  {
    $lookup: {
      from: "bookings",
      localField: "_id", 
      foreignField: "search_request_id",
      as: "bookings"
    }
  },
  {
    $group: {
      _id: null,
      total_searches: { $sum: 1 },
      searches_with_offers: { $sum: { $cond: [{ $gt: [{ $size: "$offers" }, 0] }, 1, 0] }},
      searches_with_bookings: { $sum: { $cond: [{ $gt: [{ $size: "$bookings" }, 0] }, 1, 0] }}
    }
  },
  {
    $project: {
      total_searches: 1,
      offer_rate: { $divide: ["$searches_with_offers", "$total_searches"] },
      conversion_rate: { $divide: ["$searches_with_bookings", "$total_searches"] }
    }
  }
])
```

### 5. Dynamic Pricing Analysis
```javascript
db.flight_offers.aggregate([
  {
    $match: {
      "itineraries.segments.departure.iataCode": "JFK",
      "itineraries.segments.arrival.iataCode": "LHR"
    }
  },
  {
    $group: {
      _id: "$validating_airline_codes",
      min_price: { $min: "$total_price" },
      max_price: { $max: "$total_price" },
      avg_price: { $avg: "$total_price" },
      offer_count: { $sum: 1 }
    }
  },
  { $sort: { avg_price: 1 }}
])
```

## 🔧 Advanced Usage

### Custom Search Filters
```python
from datetime import datetime, timedelta

# Find flights with specific criteria
search_criteria = {
    "itineraries.segments.departure.iataCode": "SYD",
    "itineraries.segments.arrival.iataCode": "BKK", 
    "total_price": {"$lt": 800},
    "currency_code": "USD",
    "refundable": True,
    "included_checked_bags_only": True
}

flights = db.flight_offers.find(search_criteria).sort("total_price", 1)
```

### Booking Management
```python
# Track booking lifecycle
booking_pipeline = [
    {"$match": {"status": "booked"}},
    {"$group": {
        "_id": "$payment_status",
        "count": {"$sum": 1},
        "total_value": {"$sum": "$total_amount_paid"}
    }},
    {"$sort": {"total_value": -1}}
]

booking_stats = db.bookings.aggregate(booking_pipeline)
```

### Geographic Analysis
```python
# Airport hub analysis
hub_analysis = db.airports.aggregate([
    {"$match": {"is_active": True}},
    {"$lookup": {
        "from": "airlines",
        "localField": "iata_code",
        "foreignField": "hub_airports",
        "as": "hub_airlines"
    }},
    {"$project": {
        "name": 1,
        "country_code": 1,
        "annual_passengers": 1,
        "hub_airline_count": {"$size": "$hub_airlines"}
    }},
    {"$sort": {"hub_airline_count": -1, "annual_passengers": -1}},
    {"$limit": 20}
])
```

## 📈 Performance Optimization

### Index Strategy
The database includes optimized indexes for common query patterns:

- **Route Searches**: Compound indexes on origin/destination codes
- **Price Queries**: Indexes on pricing fields with currency support
- **Date Ranges**: Temporal indexes for departure/arrival times
- **Text Search**: Full-text search on airline and airport names
- **Geospatial**: Location-based queries for nearby airports

### Query Performance Tips
1. **Use Compound Indexes**: Leverage route + date + price indexes
2. **Project Specific Fields**: Limit returned document size
3. **Batch Operations**: Use aggregation pipelines for complex analysis
4. **Cache Popular Routes**: Consider caching frequently searched routes
5. **Connection Pooling**: Implement proper connection management

## 🌐 Integration Examples

### REST API Integration
```python
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
db = MongoClient()["amadeus_flight_booking"]

@app.route('/flights/search')
def search_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')
    
    flights = db.flight_offers.find({
        "itineraries.segments.departure.iataCode": origin,
        "itineraries.segments.arrival.iataCode": destination
    }).sort("total_price", 1).limit(50)
    
    return jsonify(list(flights))
```

### Analytics Dashboard
```python
import pandas as pd

# Revenue analytics
revenue_data = db.bookings.aggregate([
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m", "date": "$booking_date"}},
        "monthly_revenue": {"$sum": "$total_amount_paid"},
        "booking_count": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
])

df = pd.DataFrame(list(revenue_data))
# Use with visualization libraries (Plotly, Matplotlib, etc.)
```

## 🛠️ Maintenance & Monitoring

### Health Checks
```javascript
// Database health monitoring
db.runCommand({collStats: "flight_offers"})
db.runCommand({serverStatus: 1})
```

### Data Cleanup
```javascript
// Remove expired offers
db.flight_offers.deleteMany({
  "expires_at": {"$lt": new Date()}
})

// Archive old bookings
db.bookings.updateMany(
  {"departure_date": {"$lt": new Date(Date.now() - 365*24*60*60*1000)}},
  {"$set": {"archived": true}}
)
```

## 📋 Business Intelligence Queries

### Market Analysis
- Route popularity and seasonal trends
- Airline market share by region
- Price elasticity and demand patterns
- Customer segmentation and preferences

### Operational Metrics
- Search-to-booking conversion rates
- Average booking values by market
- Aircraft utilization efficiency
- Revenue performance by airline/route

### Customer Insights
- Traveler behavior and booking patterns
- Price sensitivity analysis
- Service preference trends
- Geographic demand distribution

## 🔒 Security & Compliance

### Data Protection
- Sensitive traveler information handling
- Payment card data security (PCI DSS)
- GDPR compliance for EU travelers
- Data retention and purging policies

### Access Control
- Role-based database permissions
- API rate limiting and authentication
- Audit logging for financial transactions
- Encryption for sensitive data fields

## 🚀 Scaling Considerations

### Horizontal Scaling
- Shard by geographic region or airline
- Replica sets for read scaling
- Separate analytical workloads

### Performance Optimization
- Index optimization for query patterns
- Aggregation pipeline caching
- Connection pooling strategies
- Read/write concern tuning

## 📞 Support & Resources

### Documentation
- [MongoDB Best Practices](https://docs.mongodb.com/manual/administration/production-notes/)
- [Amadeus API Documentation](https://developers.amadeus.com/self-service)
- [Aviation Industry Standards](https://www.iata.org/en/services/statistics/)

### Community
- Aviation data modeling discussions
- MongoDB performance optimization
- Travel technology forums
- Open source contributions

---

**Database Version**: 1.0.0  
**MongoDB Compatibility**: 4.4+  
**Last Updated**: January 2025  
**Total Documents**: ~65,000 realistic records  

Ready to power your next flight booking platform! ✈️