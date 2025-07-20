# Technical Design - BAEMIN Food Delivery Platform

Based on the Woowa Brothers Vietnam case study, this document outlines the technical design for a comprehensive food delivery platform that handles high-volume orders, real-time logistics optimization, and multi-city operations across Vietnam and beyond.

## 1. Identify Application Workload

### Application Context

BAEMIN is a leading food delivery platform that expanded from Korea to Vietnam, serving 21 cities with rapid scaling capabilities. The platform handles spiky traffic patterns around meal times and requires real-time order processing, rider optimization, and dynamic scaling during peak periods and regulatory changes.

Core systems:
- **Order Management**: Real-time order processing and tracking
- **Logistics Optimization**: AI-powered rider selection and route optimization
- **Restaurant Network**: Multi-vendor platform with menu and inventory management  
- **Customer Experience**: User preferences, recommendations, and loyalty programs
- **Payment Processing**: Multi-payment method support with transaction tracking
- **Analytics & ML**: Data-driven insights for demand forecasting and optimization

### Data Requirements

The application needs to handle:
- High-volume order processing during peak meal times (100x traffic spikes)
- Real-time rider tracking and route optimization
- Dynamic menu and inventory management across thousands of restaurants
- Customer preference learning and recommendation engines
- Multi-city expansion with localized operations
- Regulatory compliance with rapid policy changes
- Financial transaction processing and reconciliation
- Performance metrics and business intelligence

### Workload Table

| Action | Query Type | Information | Frequency | Priority |
|--------|------------|-------------|-----------|----------|
| Place order | Write | customer_info, restaurant_items, payment_details | 10M per day | Critical |
| Track order status | Read | order_progress, rider_location, eta_updates | 50M per day | Critical |
| Find restaurants | Read | location_based_search, filters, availability | 25M per day | High |
| Update rider location | Write | gps_coordinates, status, capacity | 5M per day | Critical |
| Process payment | Write/Read | transaction_details, payment_status, refunds | 10M per day | Critical |
| Menu updates | Write | item_availability, pricing, promotions | 500K per day | High |
| Customer recommendations | Read | preference_analysis, ml_predictions, personalization | 15M per day | Medium |
| Restaurant analytics | Read | sales_data, performance_metrics, insights | 100K per day | Medium |
| Delivery optimization | Read/Write | route_calculation, rider_assignment, eta_prediction | 10M per day | Critical |
| Promotional campaigns | Read/Write | discount_rules, campaign_metrics, targeting | 50K per day | Medium |
| Customer support | Read/Write | issue_tracking, chat_history, resolution_status | 200K per day | High |
| Financial reporting | Read | transaction_summaries, commission_calculations | 10K per day | Medium |

## 2. Map Schema Relationships

### Entity Relationship Analysis

**Core Entities:**
1. **Customers** - User profiles with preferences and order history
2. **Restaurants** - Vendor profiles with menus and operational details
3. **Orders** - Transaction records with items, payments, and delivery details
4. **Riders** - Delivery personnel with location tracking and performance metrics
5. **Menu_Items** - Restaurant offerings with pricing and availability
6. **Deliveries** - Logistics tracking with routes and real-time updates
7. **Payments** - Financial transactions with multiple payment methods
8. **Reviews** - Customer feedback for restaurants and delivery experience
9. **Promotions** - Marketing campaigns with discount rules and targeting
10. **Cities** - Geographic regions with operational configurations

**Relationships:**
- Customer (1) → Orders (Many): Each customer can place multiple orders
- Restaurant (1) → Menu_Items (Many): Each restaurant has multiple menu items
- Order (1) → Order_Items (Many): Each order contains multiple items
- Order (1) → Delivery (1): Each order has one delivery record
- Rider (1) → Deliveries (Many): Each rider handles multiple deliveries
- Customer (Many) → Reviews (Many): Customers can review multiple restaurants
- Restaurant (1) → Reviews (Many): Each restaurant receives multiple reviews
- Promotion (Many) → Orders (Many): Orders can use multiple promotions
- City (1) → Restaurants (Many): Each city has multiple restaurants
- City (1) → Riders (Many): Each city has multiple riders

### Schema Design Decisions

**Embed vs Reference Strategy:**

1. **Orders (Hybrid Strategy)**
   - Reference customer and restaurant for normalization
   - Embed order items for atomic operations and performance
   - Embed delivery tracking for real-time updates
   - Reason: Orders are self-contained transactions requiring ACID properties

2. **Restaurants (Embed Strategy)**  
   - Embed menu items with current pricing and availability
   - Embed operating hours and delivery zones
   - Reference city for location-based queries
   - Reason: Menu data accessed together, frequent updates to availability

3. **Customers (Computed Values)**
   - Store aggregated metrics like total_orders, average_rating
   - Embed preferences and delivery addresses
   - Reference order history for detailed analysis
   - Reason: Profile data accessed frequently, expensive to compute on-demand

4. **Riders (Real-time Strategy)**
   - Embed current location and status for fast queries
   - Store delivery history as references
   - Pre-calculate performance metrics
   - Reason: Location updates are frequent, routing requires fast access

5. **Deliveries (Time-series Strategy)**
   - Store location updates as time-series data
   - Embed route information and ETA calculations
   - Reference order and rider for relationships
   - Reason: High-frequency GPS updates, time-based queries for analytics

## 3. Apply Design Patterns

### Design Pattern Applications

1. **Event Sourcing Pattern**
   - Track order status changes as immutable events
   - Enable order reconstruction and audit trails
   - Support complex state transitions and rollbacks

2. **CQRS Pattern**
   - Separate read models for restaurant search and recommendations
   - Optimize write models for order processing and payments
   - Enable independent scaling of read and write workloads

3. **Time-Series Pattern**
   - Store rider GPS coordinates with timestamps
   - Efficient storage and querying of location data
   - Support real-time tracking and route optimization

4. **Computed Values Pattern**
   - Pre-calculate restaurant ratings and delivery times
   - Store customer lifetime value and order frequency
   - Enable fast dashboard and recommendation queries

5. **Polymorphic Pattern**
   - Handle different payment methods in unified collection
   - Support various promotion types and discount structures
   - Manage diverse menu item categories and customizations

6. **Extended Reference Pattern**
   - Store restaurant summary data with order references
   - Include customer preferences with order items
   - Optimize for order processing workflows

### Performance Optimizations

**Indexing Strategy:**
- Location-based indexes for restaurant and rider queries (2dsphere)
- Order tracking indexes (customer_id + order_date, status + created_at)
- Real-time rider location indexes (rider_id + timestamp)
- Menu search indexes (restaurant_id + category, availability)
- Payment processing indexes (transaction_id, payment_status)
- Analytics indexes (restaurant_id + date, customer_id + order_value)

**Caching Strategy:**
- Restaurant menu data cached for fast search results
- Customer preferences cached for recommendation engine
- Rider availability cached for assignment optimization
- Popular items cached for menu recommendations

**Sharding Strategy:**
- Shard orders by customer_id for balanced distribution
- Shard riders by city for location-based queries  
- Shard menu items by restaurant_id for vendor operations
- Consider geographic sharding for multi-region expansion

### Real-time Processing Architecture

**Data Flow Pipeline:**
1. **Order Ingestion**: High-throughput order processing with validation
2. **Rider Assignment**: ML-powered optimal rider selection algorithm
3. **Route Optimization**: Real-time route calculation and ETA prediction
4. **Status Updates**: Event-driven status propagation to customers
5. **Payment Processing**: Secure transaction handling with retry logic
6. **Analytics Ingestion**: Real-time metrics for business intelligence

**ML/AI Integration Points:**
- Demand forecasting for restaurant preparation optimization
- Dynamic pricing based on supply/demand and weather
- Customer preference learning for personalized recommendations
- Delivery time prediction using historical and real-time data
- Fraud detection for payment and promotional abuse
- Route optimization considering traffic and weather patterns

### Multi-City Operations Architecture

**Geographic Distribution:**
- City-specific configurations for operations and regulations
- Localized pricing and promotional strategies
- Regional rider pools and restaurant partnerships
- Compliance with local payment methods and regulations

**Scaling Patterns:**
- Horizontal scaling during meal time traffic spikes
- Auto-scaling based on order volume and city activity
- Load balancing across geographic regions
- Failover strategies for critical order processing

### Regulatory Compliance Design

**Rapid Policy Adaptation:**
- Feature flags for instant service area modifications
- Dynamic restaurant operating hours based on regulations
- Configurable delivery restrictions by location and time
- Automated compliance reporting and audit trails

**Data Governance:**
- Customer data privacy compliance (GDPR, local regulations)
- Financial transaction audit requirements
- Location data handling for rider privacy
- Cross-border data transfer considerations for expansion

## 4. Integration Considerations

### External System Integration

**Payment Gateways:**
- Multiple payment processors for redundancy and local preferences
- Wallet integrations (MoMo, ZaloPay, GrabPay)
- Credit card processing with PCI compliance
- Cash on delivery with driver reconciliation

**Mapping and Navigation:**
- Google Maps API for location services and routing
- Local mapping providers for accurate Vietnam coverage
- Real-time traffic data for delivery optimization
- Geocoding services for address validation

**Communication Services:**
- SMS notifications for order status updates
- Push notifications for mobile app engagement
- Email marketing and transactional emails
- In-app messaging for customer support

**Analytics and Monitoring:**
- Business intelligence platforms for operational insights
- A/B testing frameworks for feature optimization
- Performance monitoring for application health
- Custom dashboards for restaurant and rider metrics

### API Design Patterns

**Microservices Architecture:**
- Order Service: Order processing and tracking
- Restaurant Service: Menu management and restaurant operations  
- Rider Service: Delivery assignment and tracking
- Customer Service: User management and preferences
- Payment Service: Transaction processing and financial operations
- Notification Service: Multi-channel communication
- Analytics Service: Data processing and insights

**Event-Driven Communication:**
- Order status changes trigger notification events
- Payment confirmations initiate delivery assignments
- Rider location updates trigger ETA recalculations
- Restaurant availability changes update search indexes

### Data Consistency Strategies

**Transaction Management:**
- Order placement requires atomic updates across multiple collections
- Payment processing with compensation patterns for failures
- Inventory management with eventual consistency for menu availability
- Rider assignment with optimistic locking for concurrent requests

**Conflict Resolution:**
- Last-writer-wins for restaurant menu updates
- Timestamp-based resolution for rider location conflicts
- Business logic validation for promotional code usage
- Manual resolution for payment disputes and refunds

## 5. Operational Excellence

### Monitoring and Alerting

**Key Performance Indicators:**
- Order processing latency and success rates
- Rider assignment efficiency and delivery times
- Payment transaction success and fraud detection
- Customer satisfaction scores and retention rates
- Restaurant partner performance and compliance

**Real-time Dashboards:**
- Live order volume and geographical distribution
- Rider availability and utilization across cities
- Restaurant performance and popular items
- System health and infrastructure metrics

### Disaster Recovery

**Backup Strategies:**
- Continuous backup of order and financial data
- Geographic replication for business continuity
- Point-in-time recovery for data corruption scenarios
- Cross-region failover for critical system components

**Business Continuity:**
- Offline mode capabilities for rider applications
- Cached menu data for service degradation scenarios
- Alternative payment processing for gateway failures
- Manual order processing for system emergencies

### Capacity Planning

**Growth Projections:**
- 70% customer growth year-over-year based on historical data
- 100x traffic spikes during peak meal times and events
- Geographic expansion to additional Vietnamese cities
- International expansion following Delivery Hero partnership

**Resource Scaling:**
- Auto-scaling compute resources based on order volume
- Database cluster scaling for increased data storage
- CDN optimization for menu images and content delivery
- Network bandwidth planning for real-time tracking data

This technical design provides the foundation for a robust, scalable food delivery platform capable of handling rapid growth, regulatory changes, and the complex operational requirements of multi-city food delivery operations in Southeast Asia.