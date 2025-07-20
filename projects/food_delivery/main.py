#!/usr/bin/env python3
"""
Main execution script for BAEMIN Food Delivery Platform Database

This script initializes and seeds the food delivery database with realistic sample data
tailored for the Vietnamese market, including Vietnamese cities, cuisine types, payment
methods, and localized business patterns.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except ImportError:
    print("❌ Error: pymongo is required. Install with: pip install pymongo")
    sys.exit(1)

try:
    from seed_db import seed_database, FoodDeliverySeeder
    from db_schema import database_schema
except ImportError as e:
    print(f"❌ Error importing project modules: {e}")
    print("Make sure you're running from the correct directory with all required files.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'food_delivery_seed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


class FoodDeliverySetupManager:
    """Manages the complete food delivery database setup process"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.client = None
        self.db = None
        self.seeder = None
        
    def run_complete_setup(self, record_counts: Optional[Dict[str, int]] = None):
        """Run the complete database setup process"""
        try:
            print("🍕 BAEMIN Food Delivery Platform Database")
            print("=" * 60)
            print("Starting Vietnamese food delivery database setup...")
            print()
            
            # Step 1: Pre-flight checks
            self._run_preflight_checks()
            
            # Step 2: Initialize seeder
            self._initialize_seeder()
            
            # Step 3: Seed database
            self._seed_database(record_counts)
            
            # Step 4: Post-seeding validation
            self._run_post_validation()
            
            # Step 5: Generate report
            self._generate_completion_report()
            
            print("✅ Food delivery database setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            print(f"❌ Setup failed: {e}")
            if logger.level == logging.DEBUG:
                traceback.print_exc()
            return False
            
        finally:
            if self.client:
                self.client.close()
                
    def _run_preflight_checks(self):
        """Run pre-flight checks before seeding"""
        print("🔍 Running pre-flight checks...")
        
        # Check MongoDB connection
        print("  • Testing MongoDB connection...", end=" ")
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Force connection attempt
            self.client.admin.command('ping')
            self.db = self.client[database_schema.database_name]
            print("✅")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print("❌")
            raise Exception(f"Cannot connect to MongoDB: {e}")
            
        # Check available disk space (if possible)
        print("  • Checking system resources...", end=" ")
        try:
            import shutil
            disk_space = shutil.disk_usage("/")
            free_space_gb = disk_space.free / (1024**3)
            if free_space_gb < 3:  # Need at least 3GB free for food delivery data
                print("⚠️")
                logger.warning(f"Low disk space: {free_space_gb:.1f}GB free")
            else:
                print("✅")
        except Exception:
            print("⚠️ (Could not check disk space)")
            
        # Check database state
        print("  • Checking database state...", end=" ")
        existing_collections = self.db.list_collection_names()
        if existing_collections:
            print(f"⚠️ ({len(existing_collections)} existing collections)")
            logger.info(f"Found existing collections: {existing_collections}")
        else:
            print("✅ (Clean database)")
            
        print("  Pre-flight checks completed\n")
        
    def _initialize_seeder(self):
        """Initialize the database seeder"""
        print("🛠️  Initializing food delivery seeder...")
        
        try:
            self.seeder = FoodDeliverySeeder(self.connection_string)
            print("  • Seeder initialized successfully ✅")
            print(f"  • Target database: {database_schema.database_name}")
            print(f"  • Collections to create: {len(database_schema.collections)}")
            print("  • Market focus: Vietnam (BAEMIN-style)")
            print()
            
        except Exception as e:
            raise Exception(f"Failed to initialize seeder: {e}")
            
    def _seed_database(self, record_counts: Optional[Dict[str, int]] = None):
        """Seed the database with sample data"""
        print("🌱 Seeding database with Vietnamese market data...")
        
        if record_counts is None:
            record_counts = {
                'cities': 8,          # Major Vietnamese cities
                'customers': 5000,    # Platform users
                'restaurants': 500,   # Restaurant partners
                'menu_items': 5000,   # Menu items across restaurants
                'riders': 200,        # Delivery riders
                'orders': 10000,      # Customer orders
                'deliveries': 8500,   # Delivery tracking records
                'payments': 10000,    # Payment transactions
                'reviews': 6000,      # Customer reviews
                'promotions': 25      # Marketing campaigns
            }
            
        total_records = sum(record_counts.values())
        print(f"  • Total records to generate: {total_records:,}")
        print("  • Record distribution:")
        for collection, count in record_counts.items():
            print(f"    - {collection}: {count:,}")
        print()
        
        start_time = datetime.now()
        
        # Clear existing data
        print("  🗑️  Clearing existing data...")
        self.seeder.clear_database()
        
        # Seed all collections
        print("  📊 Generating Vietnamese food delivery data...")
        print("    • Vietnamese cities (Ho Chi Minh City, Hanoi, Da Nang...)")
        print("    • Local cuisine types (Pho, Com Tam, Banh Mi...)")
        print("    • Vietnamese payment methods (MoMo, ZaloPay, Cash...)")
        print("    • Realistic delivery patterns and pricing in VND")
        self.seeder.seed_all_collections(record_counts)
        
        # Create indexes
        print("  🗂️  Creating geospatial and performance indexes...")
        self.seeder.create_indexes()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"  • Seeding completed in {duration.total_seconds():.1f} seconds")
        print(f"  • Average: {total_records / duration.total_seconds():.0f} records/second")
        print()
        
    def _run_post_validation(self):
        """Run post-seeding validation"""
        print("🔍 Running post-seeding validation...")
        
        try:
            self.seeder.validate_seed_data()
            print("  • Data validation passed ✅")
            
        except Exception as e:
            print(f"  • Data validation failed ❌: {e}")
            raise
            
        # Additional food delivery specific checks
        print("  • Running food delivery specific checks...")
        
        # Check order status distribution
        total_orders = self.db.orders.count_documents({})
        if total_orders > 0:
            delivered_orders = self.db.orders.count_documents({'status': 'delivered'})
            delivered_ratio = delivered_orders / total_orders
            print(f"    - Order completion rate: {delivered_ratio:.1%}")
            
        # Check payment method distribution
        payment_pipeline = [
            {"$group": {"_id": "$payment_method", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        payment_methods = list(self.db.orders.aggregate(payment_pipeline))
        if payment_methods:
            top_payment = payment_methods[0]
            print(f"    - Most popular payment method: {top_payment['_id']} ({top_payment['count']} orders)")
            
        # Check average order value
        avg_pipeline = [
            {"$group": {"_id": None, "avg_total": {"$avg": "$total_amount"}}},
            {"$project": {"_id": 0, "avg_total": 1}}
        ]
        result = list(self.db.orders.aggregate(avg_pipeline))
        if result:
            avg_order_value = result[0]['avg_total']
            print(f"    - Average order value: {avg_order_value:,.0f} VND")
            
        # Check city coverage
        cities_with_orders = self.db.orders.aggregate([
            {"$lookup": {"from": "restaurants", "localField": "restaurant_id", "foreignField": "_id", "as": "restaurant"}},
            {"$unwind": "$restaurant"},
            {"$lookup": {"from": "cities", "localField": "restaurant.city_id", "foreignField": "_id", "as": "city"}},
            {"$unwind": "$city"},
            {"$group": {"_id": "$city.city_name", "orders": {"$sum": 1}}},
            {"$sort": {"orders": -1}}
        ])
        top_cities = list(cities_with_orders)[:3]
        if top_cities:
            print(f"    - Top ordering cities: {', '.join([city['_id'] for city in top_cities])}")
            
        print("  • Food delivery validation completed ✅")
        print()
        
    def _generate_completion_report(self):
        """Generate a completion report"""
        print("📋 Food Delivery Database Setup Report")
        print("-" * 50)
        
        # Collection statistics
        print("Collection Statistics:")
        total_documents = 0
        for collection_name in sorted(database_schema.collections.keys()):
            count = self.db[collection_name].count_documents({})
            total_documents += count
            print(f"  • {collection_name:<20} {count:>8,} documents")
            
        print(f"  {'Total':<20} {total_documents:>8,} documents")
        print()
        
        # Database size estimation
        try:
            db_stats = self.db.command("dbstats")
            data_size_mb = db_stats.get('dataSize', 0) / (1024 * 1024)
            storage_size_mb = db_stats.get('storageSize', 0) / (1024 * 1024)
            
            print(f"Database Size:")
            print(f"  • Data size:     {data_size_mb:>8.1f} MB")
            print(f"  • Storage size:  {storage_size_mb:>8.1f} MB")
            print()
        except Exception:
            print("Database size: Unable to determine")
            print()
            
        # Index statistics
        print("Indexes Created:")
        total_indexes = 0
        for collection_name in sorted(database_schema.collections.keys()):
            indexes = list(self.db[collection_name].list_indexes())
            collection_indexes = len(indexes)
            total_indexes += collection_indexes
            print(f"  • {collection_name:<20} {collection_indexes:>3} indexes")
            
        print(f"  {'Total':<20} {total_indexes:>3} indexes")
        print()
        
        # Vietnamese market data preview
        print("Vietnamese Market Data Preview:")
        
        # Show sample cities
        cities = list(self.db.cities.find({}, {'city_name': 1, 'currency_code': 1}).limit(3))
        if cities:
            city_names = [city['city_name'] for city in cities]
            print(f"  • Sample Cities: {', '.join(city_names)}")
            print(f"    Currency: {cities[0]['currency_code']}")
            
        # Show sample Vietnamese restaurant
        restaurant = self.db.restaurants.find_one({'cuisine_type': 'Vietnamese'})
        if restaurant:
            print(f"  • Sample Vietnamese Restaurant: {restaurant.get('name')}")
            cuisine_types = restaurant.get('cuisine_type', [])
            print(f"    Cuisine Types: {', '.join(cuisine_types)}")
            
        # Show sample Vietnamese dishes
        vietnamese_items = list(self.db.menu_items.find(
            {'name': {'$regex': 'Pho|Com|Banh|Bun', '$options': 'i'}},
            {'name': 1, 'base_price': 1}
        ).limit(3))
        if vietnamese_items:
            dishes = [f"{item['name']} ({item['base_price']:,.0f} VND)" for item in vietnamese_items]
            print(f"  • Sample Vietnamese Dishes: {', '.join(dishes)}")
            
        # Show payment method distribution
        payment_methods = list(self.db.orders.aggregate([
            {"$group": {"_id": "$payment_method", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 3}
        ]))
        if payment_methods:
            methods = [f"{pm['_id']} ({pm['count']})" for pm in payment_methods]
            print(f"  • Top Payment Methods: {', '.join(methods)}")
            
        print()
        
        # Connection information
        print("Connection Information:")
        print(f"  • Database: {database_schema.database_name}")
        print(f"  • Connection: {self.connection_string}")
        print()
        
        # Vietnamese market insights
        print("Vietnamese Market Insights:")
        print("  • 8 major cities including Ho Chi Minh City, Hanoi, Da Nang")
        print("  • Local payment methods: MoMo, ZaloPay, GrabPay, Cash")
        print("  • Authentic Vietnamese cuisine with Pho, Com Tam, Banh Mi")
        print("  • Prices in Vietnamese Dong (VND) with realistic market rates")
        print("  • Motorcycle delivery riders with Vietnamese naming patterns")
        print()
        
        # Next steps
        print("Next Steps:")
        print("  1. Connect to MongoDB to explore the Vietnamese food delivery data:")
        print(f"     mongo {self.connection_string}/{database_schema.database_name}")
        print()
        print("  2. Query examples for Vietnamese market analysis:")
        print("     • View Vietnamese cities: db.cities.find({country: 'Vietnam'}).pretty()")
        print("     • Find Pho restaurants: db.menu_items.find({name: /Pho/i}, {name:1, base_price:1})")
        print("     • Analyze payment methods: db.orders.aggregate([{$group: {_id: '$payment_method', count: {$sum: 1}}}])")
        print("     • Check MoMo payments: db.payments.find({payment_method: 'momo'}).count()")
        print()
        print("  3. Geospatial queries for delivery optimization:")
        print("     • Find nearby restaurants: db.restaurants.find({coordinates: {$near: {$geometry: {type: 'Point', coordinates: [106.6297, 10.8231]}, $maxDistance: 5000}}})")
        print("     • Track rider locations: db.riders.find({current_location: {$exists: true}})")
        print()
        print("  4. Business intelligence for Vietnamese market:")
        print("     • Popular Vietnamese dishes by order volume")
        print("     • Peak ordering times in Vietnamese timezone")
        print("     • City-wise performance and growth metrics")
        print("     • Customer preference analysis for Vietnamese cuisine")
        print()


def main():
    """Main entry point"""
    # Configuration
    connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Custom record counts (can be overridden via environment)
    record_counts = None
    if os.getenv("CUSTOM_RECORD_COUNTS"):
        # Example: CUSTOM_RECORD_COUNTS="cities=5,customers=1000,restaurants=100"
        try:
            pairs = os.getenv("CUSTOM_RECORD_COUNTS").split(",")
            record_counts = {}
            for pair in pairs:
                key, value = pair.split("=")
                record_counts[key.strip()] = int(value.strip())
        except Exception as e:
            print(f"⚠️  Invalid CUSTOM_RECORD_COUNTS format: {e}")
            print("Using default record counts...")
    
    # Enable debug logging if requested
    if os.getenv("DEBUG", "").lower() in ["true", "1", "yes"]:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 Debug logging enabled")
        print()
    
    # Vietnamese market mode
    if os.getenv("VIETNAM_MODE", "true").lower() in ["true", "1", "yes"]:
        print("🇻🇳 Vietnamese market mode enabled")
        print("   • Vietnamese cities and addresses")
        print("   • Local payment methods (MoMo, ZaloPay, etc.)")
        print("   • Vietnamese cuisine and dish names")
        print("   • VND pricing and Vietnamese phone numbers")
        print()
    
    # Run setup
    manager = FoodDeliverySetupManager(connection_string)
    success = manager.run_complete_setup(record_counts)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()