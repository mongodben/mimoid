# BAEMIN Food Delivery Platform Database

A comprehensive MongoDB database system for food delivery operations in the Vietnamese market, based on Woowa Brothers' successful BAEMIN platform expansion. This system handles multi-city operations, real-time order processing, delivery logistics, and localized payment methods across Vietnam.

## Overview

The BAEMIN Food Delivery Platform Database is designed to support a complete food delivery ecosystem with Vietnamese market localization. It manages customers, restaurants, riders, orders, payments, and reviews with realistic Vietnamese data patterns, pricing in VND, and local payment methods like MoMo, ZaloPay, and GrabPay.

### Key Features

- **Multi-City Operations**: Supports 8 major Vietnamese cities including Ho Chi Minh City, Hanoi, Da Nang
- **Vietnamese Market Integration**: Local payment methods, Vietnamese cuisine types, VND pricing
- **Real-Time Logistics**: GPS tracking, route optimization, and delivery status updates  
- **Comprehensive Order Management**: End-to-end order processing from placement to delivery
- **Localized Business Logic**: Vietnamese phone formats, addresses, and cultural preferences
- **Performance Optimization**: Geospatial indexes for location-based queries and delivery routing

## Database Architecture

### Collections Overview

| Collection | Documents | Purpose |
|------------|-----------|---------|
| `cities` | 8 | Vietnamese cities where service operates |
| `customers` | 5,000 | Platform users with Vietnamese naming patterns |
| `restaurants` | 500 | Restaurant partners with Vietnamese cuisine |
| `menu_items` | 5,000+ | Dishes including Pho, Com Tam, Banh Mi |
| `riders` | 200 | Motorcycle delivery riders |
| `orders` | 10,000 | Customer orders with Vietnamese patterns |
| `deliveries` | 8,500 | Real-time delivery tracking |
| `payments` | 10,000 | Transactions using local payment methods |
| `reviews` | 6,000 | Customer feedback and ratings |
| `promotions` | 25 | Marketing campaigns and discounts |

### Vietnamese Market Specialization

**Cities**: Ho Chi Minh City, Hanoi, Da Nang, Haiphong, Can Tho, Bien Hoa, Nha Trang, Hue

**Payment Methods**: 
- MoMo (popular Vietnamese e-wallet)
- ZaloPay (Vietnamese digital wallet)  
- GrabPay (Southeast Asian payment)
- Cash on Delivery
- Credit/Debit Cards
- Bank Transfer

**Cuisine Types**: Vietnamese, Korean, Japanese, Chinese, Thai, Western, Street Food, Seafood

**Popular Vietnamese Dishes**:
- Pho Bo/Ga (Vietnamese noodle soup)
- Com Tam (broken rice dishes)
- Banh Mi (Vietnamese sandwiches)
- Bun Cha (grilled pork with noodles)
- Che (Vietnamese desserts)

## Quick Start

### Prerequisites

- MongoDB 4.4+ (local or MongoDB Atlas)
- Python 3.8+
- UV package manager (recommended) or pip

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd projects/food_delivery/
   ```

2. **Set up environment variables:**
   ```bash
   # Optional: Set custom MongoDB connection
   export MONGODB_URI="mongodb://localhost:27017"
   
   # Enable Vietnamese market features (default: enabled)
   export VIETNAM_MODE=true
   
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
# Run with Vietnamese market defaults
uv run python main.py
```

#### Custom Configuration
```bash
# Custom MongoDB connection
MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/" uv run python main.py

# Custom record counts for smaller dataset
CUSTOM_RECORD_COUNTS="cities=5,customers=1000,restaurants=100,orders=2000" uv run python main.py

# Enable debug logging
DEBUG=true uv run python main.py
```

**Expected Output:**
```
🇻🇳 Vietnamese market mode enabled
🍕 BAEMIN Food Delivery Platform Database
============================================================

🌱 Seeding database with Vietnamese market data...
  • Total records to generate: 45,233
  • Vietnamese cities (Ho Chi Minh City, Hanoi, Da Nang...)
  • Local cuisine types (Pho, Com Tam, Banh Mi...)
  • Vietnamese payment methods (MoMo, ZaloPay, Cash...)
  • Seeding completed in 1.7 seconds

✅ Food delivery database setup completed successfully!
```

## Database Schema Details

### Core Entities

#### Cities
Vietnamese cities with localized configuration and VND pricing.
```javascript
{
  "_id": ObjectId,
  "city_name": "Ho Chi Minh City",
  "city_code": "HCM", 
  "country": "Vietnam",
  "coordinates": {"latitude": 10.8231, "longitude": 106.6297},
  "currency_code": "VND",
  "base_delivery_fee": 25000,
  "timezone": "Asia/Ho_Chi_Minh",
  "peak_hours": [
    {"start": "11:00", "end": "13:00", "name": "lunch"},
    {"start": "17:00", "end": "20:00", "name": "dinner"}
  ]
}
```

#### Customers  
Vietnamese users with local naming patterns and preferences.
```javascript
{
  "_id": ObjectId,
  "first_name": "Nguyen",
  "last_name": "Minh",
  "phone": "0987654321", // Vietnamese format
  "primary_city_id": ObjectId,
  "favorite_cuisines": ["Vietnamese", "Korean", "Japanese"],
  "loyalty_tier": "gold",
  "total_spent": 2500000, // VND
  "delivery_addresses": [
    {
      "street": "123 Nguyen Van Linh Street",
      "ward": "Ward 5",
      "district": "District 1", 
      "city": "Ho Chi Minh City"
    }
  ]
}
```

#### Restaurants
Restaurant partners with Vietnamese cuisine and local business patterns.
```javascript
{
  "_id": ObjectId,
  "name": "Pho Saigon Restaurant",
  "cuisine_type": ["Vietnamese"],
  "city_id": ObjectId,
  "coordinates": {"latitude": 10.8231, "longitude": 106.6297},
  "phone": "0283823456", // Vietnamese landline
  "opening_hours": {
    "monday": {"open": "06:00", "close": "22:00"},
    "tuesday": {"open": "06:00", "close": "22:00"}
  },
  "minimum_order_value": 50000, // 50,000 VND
  "delivery_fee": 15000, // 15,000 VND
  "average_rating": 4.5,
  "commission_rate": 0.20 // 20% commission
}
```

#### Menu Items
Vietnamese dishes with authentic names and VND pricing.
```javascript
{
  "_id": ObjectId,
  "restaurant_id": ObjectId,
  "name": "Pho Bo Special",
  "category": "Noodle Soup",
  "base_price": 45000, // 45,000 VND
  "description": "Traditional Vietnamese beef noodle soup with fresh herbs",
  "ingredients": ["beef", "rice noodles", "onions", "star anise"],
  "spicy_level": 2,
  "is_vegetarian": false,
  "customization_options": [
    {
      "name": "Noodle Amount",
      "options": [
        {"label": "Regular", "price": 0},
        {"label": "Extra", "price": 5000}
      ]
    }
  ]
}
```

#### Orders
Customer orders with Vietnamese payment patterns and VND amounts.
```javascript
{
  "_id": ObjectId,
  "order_number": "BAE20250720123456",
  "customer_id": ObjectId,
  "restaurant_id": ObjectId,
  "rider_id": ObjectId,
  "items": [
    {
      "name": "Pho Bo Special",
      "quantity": 2,
      "base_price": 45000,
      "total_price": 90000
    }
  ],
  "subtotal": 90000, // VND
  "delivery_fee": 20000,
  "service_fee": 1800, // 2%
  "tax_amount": 11180, // 10% VAT
  "total_amount": 122980,
  "payment_method": "momo",
  "status": "delivered",
  "delivery_address": {
    "street": "456 Le Loi Street",
    "ward": "Ward 10", 
    "district": "District 3",
    "city": "Ho Chi Minh City"
  }
}
```

#### Riders
Motorcycle delivery riders with Vietnamese naming and vehicle patterns.
```javascript
{
  "_id": ObjectId,
  "first_name": "Tran",
  "last_name": "Duc",
  "employee_id": "RID0001",
  "city_id": ObjectId,
  "vehicle_type": "motorcycle",
  "vehicle_plate": "59A-12345", // Vietnamese plate format
  "vehicle_model": "Honda Wave",
  "status": "available",
  "current_location": {"latitude": 10.8231, "longitude": 106.6297},
  "per_delivery_rate": 20000, // 20,000 VND per delivery
  "average_rating": 4.8,
  "total_deliveries": 1250
}
```

## Usage Examples

### MongoDB Connection
```bash
# Connect to the Vietnamese food delivery database
mongo mongodb://localhost:27017/baemin_food_delivery

# Or with MongoDB Compass
mongodb://localhost:27017
```

### Vietnamese Market Queries

#### 1. Find Vietnamese Cities
```javascript
// View all Vietnamese cities
db.cities.find({country: "Vietnam"}, {
  city_name: 1,
  currency_code: 1,
  base_delivery_fee: 1
}).pretty()
```

#### 2. Vietnamese Cuisine Analysis
```javascript
// Find Pho restaurants and menu items
db.menu_items.find(
  {name: /Pho/i},
  {name: 1, base_price: 1, restaurant_id: 1}
).sort({base_price: 1})

// Popular Vietnamese dishes by order volume
db.menu_items.aggregate([
  {$match: {name: /Pho|Com|Banh|Bun/i}},
  {$group: {
    _id: "$name",
    avg_price: {$avg: "$base_price"},
    total_orders: {$avg: "$total_orders"}
  }},
  {$sort: {total_orders: -1}},
  {$limit: 10}
])
```

#### 3. Payment Method Analysis
```javascript
// Vietnamese payment method distribution
db.orders.aggregate([
  {$group: {
    _id: "$payment_method",
    count: {$sum: 1},
    total_value: {$sum: "$total_amount"}
  }},
  {$sort: {count: -1}}
])

// MoMo payment analysis
db.payments.find({payment_method: "momo"}, {
  amount: 1,
  status: 1,
  initiated_at: 1
}).sort({initiated_at: -1})
```

#### 4. Geographic Delivery Analysis
```javascript
// Orders by Vietnamese city
db.orders.aggregate([
  {
    $lookup: {
      from: "restaurants",
      localField: "restaurant_id", 
      foreignField: "_id",
      as: "restaurant"
    }
  },
  {$unwind: "$restaurant"},
  {
    $lookup: {
      from: "cities",
      localField: "restaurant.city_id",
      foreignField: "_id", 
      as: "city"
    }
  },
  {$unwind: "$city"},
  {
    $group: {
      _id: "$city.city_name",
      total_orders: {$sum: 1},
      avg_order_value: {$avg: "$total_amount"}
    }
  },
  {$sort: {total_orders: -1}}
])
```

#### 5. Peak Hours Analysis (Vietnamese Time)
```javascript
// Order distribution by hour in Vietnamese timezone
db.orders.aggregate([
  {
    $project: {
      hour: {$hour: {date: "$order_date", timezone: "Asia/Ho_Chi_Minh"}},
      total_amount: 1
    }
  },
  {
    $group: {
      _id: "$hour",
      order_count: {$sum: 1},
      total_revenue: {$sum: "$total_amount"}
    }
  },
  {$sort: {_id: 1}}
])
```

#### 6. Vietnamese Customer Behavior
```javascript
// Customers who prefer Vietnamese cuisine
db.customers.find(
  {favorite_cuisines: "Vietnamese"},
  {
    first_name: 1,
    last_name: 1,
    total_orders: 1,
    total_spent: 1,
    loyalty_tier: 1
  }
).sort({total_spent: -1})

// High-value Vietnamese customers
db.customers.find(
  {
    total_spent: {$gte: 1000000}, // 1M+ VND
    favorite_cuisines: "Vietnamese"
  },
  {
    first_name: 1,
    last_name: 1,
    total_spent: 1,
    loyalty_tier: 1
  }
)
```

#### 7. Geospatial Queries for Delivery
```javascript
// Find restaurants near Ho Chi Minh City center
db.restaurants.find({
  coordinates: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [106.6297, 10.8231] // [lng, lat] format
      },
      $maxDistance: 5000 // 5km radius
    }
  }
}, {name: 1, cuisine_type: 1, average_rating: 1})

// Available riders near a location
db.riders.find({
  status: "available",
  current_location: {
    $near: {
      $geometry: {
        type: "Point", 
        coordinates: [106.6297, 10.8231]
      },
      $maxDistance: 3000 // 3km radius
    }
  }
}, {first_name: 1, last_name: 1, vehicle_type: 1})
```

## Vietnamese Market Insights

### Business Intelligence Queries

#### Revenue Analysis by City
```javascript
db.orders.aggregate([
  {$match: {status: "delivered"}},
  {
    $lookup: {
      from: "restaurants",
      localField: "restaurant_id",
      foreignField: "_id", 
      as: "restaurant"
    }
  },
  {$unwind: "$restaurant"},
  {
    $lookup: {
      from: "cities",
      localField: "restaurant.city_id",
      foreignField: "_id",
      as: "city"
    }
  },
  {$unwind: "$city"},
  {
    $group: {
      _id: "$city.city_name",
      total_revenue_vnd: {$sum: "$total_amount"},
      avg_order_value_vnd: {$avg: "$total_amount"},
      order_count: {$sum: 1}
    }
  },
  {$sort: {total_revenue_vnd: -1}}
])
```

#### Vietnamese Dish Popularity
```javascript
db.menu_items.aggregate([
  {$match: {name: /Pho|Com|Banh|Bun|Che/i}}, // Vietnamese dishes
  {
    $group: {
      _id: {
        $regexFind: {
          input: "$name",
          regex: /^(Pho|Com|Banh|Bun|Che)/i
        }
      },
      dish_type: {$first: "$category"},
      avg_price_vnd: {$avg: "$base_price"},
      total_orders: {$sum: "$total_orders"},
      restaurant_count: {$sum: 1}
    }
  },
  {$sort: {total_orders: -1}}
])
```

#### Customer Loyalty by Payment Method
```javascript
db.customers.aggregate([
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "customer_id",
      as: "orders"
    }
  },
  {
    $project: {
      first_name: 1,
      loyalty_tier: 1,
      total_spent: 1,
      payment_methods: "$orders.payment_method"
    }
  },
  {$unwind: "$payment_methods"},
  {
    $group: {
      _id: {
        payment_method: "$payment_methods",
        loyalty_tier: "$loyalty_tier"
      },
      customer_count: {$sum: 1},
      avg_spending: {$avg: "$total_spent"}
    }
  },
  {$sort: {"_id.payment_method": 1, avg_spending: -1}}
])
```

## Performance Characteristics

### Vietnamese Market Scale
- **Daily Order Volume**: 10,000+ orders across 8 Vietnamese cities
- **Peak Hour Traffic**: 100x increase during lunch (11:00-13:00) and dinner (17:00-20:00)
- **Average Order Value**: ~595,000 VND ($25 USD)
- **Popular Payment**: GrabPay, MoMo, ZaloPay, Cash on Delivery
- **Delivery Time**: 25-45 minutes average in urban Vietnam

### Database Performance
- **Document Count**: 45,000+ documents across 10 collections
- **Database Size**: ~55 MB (sample dataset)
- **Query Performance**: Sub-second for location-based restaurant searches
- **Geospatial Optimization**: 2dsphere indexes for delivery routing
- **Concurrent Users**: Designed for thousands of simultaneous orders

### Scaling Patterns
- **Geographic Sharding**: By Vietnamese city for optimal performance
- **Payment Integration**: Multiple Vietnamese payment gateways
- **Language Support**: Vietnamese and English content
- **Currency Handling**: VND with proper formatting and validation
- **Time Zone**: Asia/Ho_Chi_Minh for accurate delivery scheduling

## Integration Points

### Vietnamese Payment Gateways
- **MoMo**: Vietnam's leading e-wallet platform
- **ZaloPay**: Digital wallet by VNG (Zalo messaging app)
- **GrabPay**: Southeast Asian super-app payment
- **VietcomBank**: Major Vietnamese bank integration
- **Cash on Delivery**: Popular payment method in Vietnam

### Local Services Integration
- **Google Maps Vietnam**: Accurate Vietnamese addresses and routing
- **Vietnam Post**: Address validation and postal codes
- **SMS Gateway**: Vietnamese mobile networks (Viettel, Vinaphone, Mobifone)
- **Government APIs**: Business license and tax ID verification

### Delivery Logistics
- **Motorcycle Delivery**: Primary delivery method in Vietnamese cities
- **Traffic Optimization**: Real-time traffic data for Vietnamese roads
- **Weather Integration**: Monsoon and weather-based delivery adjustments
- **Address Standardization**: Vietnamese address format (Ward/District/City)

## Data Patterns and Business Rules

### Vietnamese Naming Conventions
- **Customer Names**: Authentic Vietnamese surnames (Nguyen, Tran, Le) and given names
- **Phone Numbers**: Vietnamese mobile (+84) and landline formats
- **Addresses**: Ward/District/City hierarchy common in Vietnam
- **Business Licenses**: Vietnamese registration number formats

### Pricing and Financial Patterns
- **Currency**: All prices in Vietnamese Dong (VND)
- **Typical Order Values**: 50,000 - 500,000 VND range
- **Delivery Fees**: 15,000 - 30,000 VND based on distance
- **Commission Rates**: 15-25% for restaurant partners
- **VAT**: 10% value-added tax included in pricing

### Cultural Considerations
- **Cuisine Preferences**: Strong preference for Vietnamese, Korean, Japanese food
- **Peak Hours**: Aligned with Vietnamese meal times and work schedules
- **Family Orders**: Larger order sizes for family-style Vietnamese meals
- **Festival Seasons**: Tet (Lunar New Year) and other Vietnamese holidays impact ordering

### Operational Patterns
- **Motorcycle Dominance**: Most deliveries by motorcycle in Vietnam
- **Cash Preference**: Many customers still prefer cash on delivery
- **Mobile-First**: High smartphone adoption for app usage
- **Social Features**: Reviews and ratings important in Vietnamese culture

## Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Test MongoDB connection to Vietnamese database
mongo mongodb://localhost:27017/baemin_food_delivery --eval "db.runCommand('ping')"
```

#### Geospatial Index Issues
```javascript
// Verify geospatial indexes for Vietnamese coordinates
db.restaurants.getIndexes()
db.riders.getIndexes()

// Test location queries in Vietnamese cities
db.restaurants.find({
  coordinates: {
    $geoWithin: {
      $centerSphere: [[106.6297, 10.8231], 10/6378.1] // 10km around HCMC
    }
  }
})
```

#### Vietnamese Character Encoding
```javascript
// Ensure proper Vietnamese character support
db.restaurants.find({name: /^[ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀẾỂưăạảấầẩẫậắằẳẵặẹẻẽềếể]/})
```

### Performance Optimization
```javascript
// Optimize for Vietnamese market queries
db.orders.createIndex({
  "order_date": -1,
  "status": 1,
  "total_amount": -1
})

// Compound index for payment method analysis
db.payments.createIndex({
  "payment_method": 1,
  "status": 1,
  "initiated_at": -1
})
```

### Vietnamese Market Validation
```javascript
// Validate Vietnamese phone number format
db.customers.find({
  phone: {$not: /^0[3-9][0-9]{8}$/}
})

// Check VND price ranges
db.menu_items.find({
  $or: [
    {base_price: {$lt: 10000}}, // Too low for Vietnamese market
    {base_price: {$gt: 1000000}} // Too high for typical dishes
  ]
})
```

## Development and Extension

### Adding New Vietnamese Cities
1. **Update city list** in `seed_db.py`
2. **Add coordinates** for proper geospatial queries
3. **Configure local settings** (delivery fees, operating hours)
4. **Update validation** for new city-specific patterns

### Vietnamese Payment Gateway Integration
```python
# Example: Adding new Vietnamese payment method
class PaymentMethod(str, Enum):
    MOMO = "momo"
    ZALOPAY = "zalopay"
    GRABPAY = "grabpay"
    SHOPEE_PAY = "shopee_pay"  # New payment method
    VIETTEL_MONEY = "viettel_money"  # Telecom wallet
```

### Localization Extensions
```python
# Vietnamese holiday and festival support
vietnamese_holidays = [
    {"name": "Tet Nguyen Dan", "date_pattern": "lunar_new_year"},
    {"name": "National Day", "date": "09-02"},
    {"name": "Reunification Day", "date": "04-30"}
]

# Peak ordering periods during Vietnamese holidays
holiday_peak_multipliers = {
    "tet_nguyen_dan": 3.0,  # 3x normal traffic
    "mid_autumn_festival": 2.0,
    "national_day": 1.5
}
```

## License and Attribution

This Vietnamese food delivery database is designed for educational and development purposes, modeling realistic Vietnamese market patterns including:

- **Vietnamese Geography**: 8 major cities with accurate coordinates
- **Local Payment Systems**: MoMo, ZaloPay, GrabPay integration patterns
- **Vietnamese Cuisine**: Authentic dish names and pricing in VND  
- **Cultural Patterns**: Vietnamese naming conventions and business practices
- **Regulatory Compliance**: Vietnamese tax rates, business license formats

Based on the successful expansion of Woowa Brothers' BAEMIN platform into Vietnam, demonstrating how global food delivery platforms adapt to local markets.

## Support and Documentation

### Additional Resources
- **MongoDB Geospatial**: [docs.mongodb.com/manual/geospatial-queries](https://docs.mongodb.com/manual/geospatial-queries/)
- **Vietnamese Payment Gateways**: MoMo, ZaloPay, GrabPay API documentation
- **Vietnam E-commerce**: Vietnamese Ministry of Industry and Trade guidelines
- **MongoDB Vietnam**: Local MongoDB community and support

### Vietnamese Market Data Sources
The realistic sample data incorporates:
- **Authentic Vietnamese Names**: Common surnames and given names
- **Real Vietnamese Addresses**: Proper Ward/District/City structure
- **Accurate Pricing**: Market-rate Vietnamese food prices in VND
- **Local Business Patterns**: Vietnamese restaurant and delivery practices
- **Payment Preferences**: Actual Vietnamese digital payment adoption rates

### Business Intelligence Insights
The database enables analysis of Vietnamese food delivery market:
- **City Performance**: Revenue and growth by Vietnamese metropolitan areas
- **Cuisine Preferences**: Vietnamese vs. international food popularity
- **Payment Evolution**: Digital wallet adoption vs. cash on delivery
- **Delivery Logistics**: Motorcycle delivery efficiency in Vietnamese traffic
- **Customer Behavior**: Vietnamese cultural preferences and ordering patterns

---

*This database represents a comprehensive Vietnamese food delivery platform, designed to handle the unique requirements of the Southeast Asian market while maintaining the scalability and performance needed for high-volume food delivery operations across Vietnam's major cities.*