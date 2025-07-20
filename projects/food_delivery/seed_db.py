"""Database seeder for BAEMIN Food Delivery Platform"""

from faker import Faker
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Optional, List, Any
import logging
import math

# Import the database schema and base types
from db_schema import (
    database_schema,
    OrderStatus,
    RiderStatus,
    PaymentMethod,
    PaymentStatus,
    RestaurantStatus,
    DeliveryStatus,
    PromotionType,
    ReviewRating
)
from mimiod import DatabaseSeeder as BaseDatabaseSeeder

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FoodDeliverySeeder(BaseDatabaseSeeder):
    """Database seeder for food delivery platform"""
    
    def __init__(self, connection_string: str):
        super().__init__(connection_string, database_schema)
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        self.fake = Faker()
        
        # Vietnamese-specific localization
        self.vietnamese_cities = [
            {"name": "Ho Chi Minh City", "code": "HCM", "coords": [10.8231, 106.6297]},
            {"name": "Hanoi", "code": "HAN", "coords": [21.0285, 105.8542]},
            {"name": "Da Nang", "code": "DAD", "coords": [16.0471, 108.2062]},
            {"name": "Haiphong", "code": "HPH", "coords": [20.8449, 106.6881]},
            {"name": "Can Tho", "code": "CTH", "coords": [10.0452, 105.7469]},
            {"name": "Bien Hoa", "code": "BHO", "coords": [10.9447, 106.8230]},
            {"name": "Nha Trang", "code": "NTR", "coords": [12.2388, 109.1967]},
            {"name": "Hue", "code": "HUE", "coords": [16.4637, 107.5909]}
        ]
        
        # Vietnamese cuisine types
        self.cuisine_types = [
            "Vietnamese", "Korean", "Japanese", "Chinese", "Thai", "Western", 
            "Fast Food", "Street Food", "Seafood", "Vegetarian", "BBQ", "Hotpot",
            "Cafe", "Dessert", "Bubble Tea", "Pizza", "Burger", "Sushi"
        ]
        
        # Vietnamese dish names and categories
        self.vietnamese_dishes = {
            "Noodle Soup": ["Pho Bo", "Pho Ga", "Bun Bo Hue", "Mi Quang", "Bun Rieu"],
            "Rice Dishes": ["Com Tam", "Com Ga", "Com Suon", "Com Chien", "Com Hen"],
            "Noodle Dishes": ["Bun Cha", "Bun Bo Nam Bo", "Mi Xao", "Hu Tieu", "Cao Lau"],
            "Street Food": ["Banh Mi", "Goi Cuon", "Cha Ca", "Nem Ran", "Bot Chien"],
            "Drinks": ["Tra Da", "Ca Phe Sua Da", "Sinh To", "Nuoc Mia", "Che Ba Mau"],
            "Desserts": ["Che", "Banh Flan", "Banh Chuoi", "Kem", "Yogurt"]
        }
        
        # Payment methods popular in Vietnam
        self.vietnamese_payment_methods = [
            PaymentMethod.CASH,
            PaymentMethod.MOMO,
            PaymentMethod.ZALOPAY,
            PaymentMethod.GRABPAY,
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.BANK_TRANSFER
        ]
        
        # Common Vietnamese names
        self.vietnamese_first_names = [
            "Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Vo", "Vu", "Dang", "Bui",
            "Do", "Ho", "Ngo", "Duong", "Ly", "Mai", "Phan", "Lam", "Truong", "Dinh"
        ]
        
        self.vietnamese_given_names = {
            "male": ["Minh", "Duc", "Hung", "Quang", "Dung", "Hieu", "Long", "Nam", "Phong", "Tuan"],
            "female": ["Linh", "Anh", "Huong", "Lan", "Mai", "Nga", "Thao", "Yen", "Ha", "My"]
        }
        
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        if num_records is None:
            num_records = {
                'cities': 8,
                'customers': 5000,
                'restaurants': 500,
                'menu_items': 5000,
                'riders': 200,
                'orders': 10000,
                'deliveries': 8500,
                'payments': 10000,
                'reviews': 6000,
                'promotions': 25
            }
            
        logger.info("Starting food delivery database seeding process...")
        
        # Seed in dependency order
        city_ids = self.seed_cities(num_records['cities'])
        customer_ids = self.seed_customers(num_records['customers'], city_ids)
        restaurant_ids = self.seed_restaurants(num_records['restaurants'], city_ids)
        menu_item_ids = self.seed_menu_items(num_records['menu_items'], restaurant_ids)
        rider_ids = self.seed_riders(num_records['riders'], city_ids)
        
        # Orders depend on customers, restaurants, and riders
        order_ids = self.seed_orders(num_records['orders'], customer_ids, restaurant_ids, rider_ids)
        
        # Deliveries, payments, and reviews depend on orders
        self.seed_deliveries(num_records['deliveries'], order_ids, rider_ids)
        self.seed_payments(num_records['payments'], order_ids, customer_ids)
        self.seed_reviews(num_records['reviews'], order_ids, customer_ids, restaurant_ids, rider_ids)
        self.seed_promotions(num_records['promotions'], city_ids, restaurant_ids)
        
        logger.info("Food delivery database seeding completed successfully!")
        
    def seed_cities(self, count: int) -> List[ObjectId]:
        """Generate and insert city documents"""
        logger.info(f"Seeding {count} cities...")
        
        cities = []
        selected_cities = self.vietnamese_cities[:count]
        
        for i, city_data in enumerate(selected_cities):
            city = {
                '_id': ObjectId(),
                'city_name': city_data['name'],
                'city_code': city_data['code'],
                'country': "Vietnam",
                'coordinates': {
                    'latitude': city_data['coords'][0],
                    'longitude': city_data['coords'][1]
                },
                'timezone': "Asia/Ho_Chi_Minh",
                'is_active': True,
                'launch_date': self.fake.date_time_between(start_date='-3y', end_date='-6m'),
                'base_delivery_fee': random.uniform(15000, 30000),  # VND
                'max_delivery_radius_km': random.uniform(15, 25),
                'peak_hours': [
                    {'start': '11:00', 'end': '13:00', 'name': 'lunch'},
                    {'start': '17:00', 'end': '20:00', 'name': 'dinner'}
                ],
                'currency_code': 'VND',
                'language_code': 'vi-VN',
                'operating_license': f"VN-{city_data['code']}-{random.randint(100000, 999999)}",
                'tax_rate': 0.1,  # 10% VAT in Vietnam
                'created_at': datetime.utcnow(),
                'updated_at': None
            }
            cities.append(city)
            
        self.db.cities.insert_many(cities)
        logger.info(f"Inserted {len(cities)} cities")
        return [city['_id'] for city in cities]
        
    def seed_customers(self, count: int, city_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert customer documents"""
        logger.info(f"Seeding {count} customers...")
        
        customers = []
        for i in range(count):
            gender = random.choice(['male', 'female'])
            first_name = random.choice(self.vietnamese_first_names)
            given_name = random.choice(self.vietnamese_given_names[gender])
            
            # Generate realistic customer metrics
            total_orders = random.randint(0, 150)
            avg_order_value = random.uniform(50000, 300000)  # VND
            total_spent = total_orders * avg_order_value * random.uniform(0.8, 1.2)
            
            loyalty_tiers = ["bronze", "silver", "gold", "platinum"]
            if total_spent > 5000000:
                loyalty_tier = random.choice(["gold", "platinum"])
            elif total_spent > 2000000:
                loyalty_tier = random.choice(["silver", "gold"])
            else:
                loyalty_tier = random.choice(["bronze", "silver"])
            
            customer = {
                '_id': ObjectId(),
                'first_name': first_name,
                'last_name': given_name,
                'email': f"{first_name.lower()}.{given_name.lower()}{random.randint(1, 999)}@email.com",
                'phone': f"0{random.randint(900000000, 999999999)}",  # Vietnamese phone format
                'password_hash': self.fake.sha256(),
                'email_verified': random.choice([True, True, True, False]),  # 75% verified
                'phone_verified': random.choice([True, True, False]),  # 66% verified
                'primary_city_id': random.choice(city_ids),
                'delivery_addresses': self._generate_delivery_addresses(random.randint(1, 4)),
                'favorite_cuisines': random.sample(self.cuisine_types, k=random.randint(2, 5)),
                'dietary_restrictions': random.sample(
                    ["vegetarian", "vegan", "gluten-free", "halal", "no-pork", "no-seafood", "diabetic"], 
                    k=random.randint(0, 2)
                ),
                'date_of_birth': self.fake.date_time_between(start_date='-65y', end_date='-18y') if random.random() > 0.3 else None,
                'avatar_url': f"https://cdn.baemin.vn/avatars/{i+1}.jpg" if random.random() > 0.4 else None,
                'loyalty_tier': loyalty_tier,
                'total_orders': total_orders,
                'total_spent': total_spent,
                'average_order_value': avg_order_value,
                'average_rating_given': random.uniform(3.5, 5.0),
                'last_order_date': self.fake.date_time_between(start_date='-30d', end_date='now') if total_orders > 0 else None,
                'app_version': f"2.{random.randint(15, 25)}.{random.randint(0, 9)}",
                'device_info': {
                    'platform': random.choice(['ios', 'android']),
                    'device_model': random.choice(['iPhone 12', 'Samsung Galaxy S21', 'Oppo Reno', 'Xiaomi Mi 11']),
                    'os_version': f"{random.randint(12, 15)}.{random.randint(0, 9)}"
                },
                'is_active': random.choice([True] * 9 + [False]),  # 90% active
                'marketing_opt_in': random.choice([True, False]),
                'push_notifications': random.choice([True] * 7 + [False] * 3),  # 70% enabled
                'created_at': self.fake.date_time_between(start_date='-2y', end_date='-1m'),
                'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now') if random.random() > 0.6 else None
            }
            customers.append(customer)
            
        self.db.customers.insert_many(customers)
        logger.info(f"Inserted {len(customers)} customers")
        return [customer['_id'] for customer in customers]
        
    def seed_restaurants(self, count: int, city_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert restaurant documents"""
        logger.info(f"Seeding {count} restaurants...")
        
        restaurants = []
        restaurant_types = [
            "Family Restaurant", "Fast Food", "Cafe", "Street Food", "Fine Dining",
            "Casual Dining", "Quick Service", "Food Truck", "Bakery", "Dessert Shop"
        ]
        
        for i in range(count):
            city_id = random.choice(city_ids)
            cuisine = random.choice(self.cuisine_types)
            restaurant_type = random.choice(restaurant_types)
            
            name = f"{self._generate_restaurant_name(cuisine)} {restaurant_type}"
            
            # Generate realistic performance metrics
            total_orders = random.randint(50, 5000)
            avg_rating = random.uniform(3.0, 5.0)
            total_reviews = int(total_orders * random.uniform(0.1, 0.4))  # 10-40% review rate
            
            restaurant = {
                '_id': ObjectId(),
                'name': name,
                'description': f"Authentic {cuisine.lower()} cuisine with fresh ingredients and traditional recipes. Popular {restaurant_type.lower()} serving delicious meals for the whole family.",
                'cuisine_type': [cuisine] + (random.sample(self.cuisine_types, k=random.randint(0, 2)) if random.random() > 0.7 else []),
                'city_id': city_id,
                'address': self._generate_restaurant_address(),
                'coordinates': self._generate_coordinates_near_city(city_id, city_ids),
                'phone': f"0{random.randint(200000000, 299999999)}",  # Vietnamese landline format
                'email': f"info@{name.lower().replace(' ', '')}.com.vn" if random.random() > 0.3 else None,
                'business_license': f"BL-{random.randint(100000000, 999999999)}",
                'tax_id': f"TAX-{random.randint(1000000000, 9999999999)}" if random.random() > 0.2 else None,
                'owner_name': f"{random.choice(self.vietnamese_first_names)} {random.choice(self.vietnamese_given_names['male'])}",
                'status': random.choice([RestaurantStatus.ACTIVE] * 8 + [RestaurantStatus.INACTIVE, RestaurantStatus.SUSPENDED]),
                'opening_hours': self._generate_opening_hours(),
                'preparation_time_minutes': random.randint(15, 45),
                'delivery_radius_km': random.uniform(5, 20),
                'minimum_order_value': random.choice([0, 50000, 100000, 150000]),  # VND
                'delivery_fee': random.uniform(10000, 25000),  # VND
                'commission_rate': random.uniform(0.15, 0.25),  # 15-25% commission
                'payment_method': random.choice(["bank_transfer", "cash_on_delivery", "digital_wallet"]),
                'logo_url': f"https://cdn.baemin.vn/restaurants/logos/{i+1}.jpg",
                'cover_image_url': f"https://cdn.baemin.vn/restaurants/covers/{i+1}.jpg",
                'gallery_images': [
                    f"https://cdn.baemin.vn/restaurants/gallery/{i+1}_{j}.jpg" 
                    for j in range(random.randint(3, 8))
                ],
                'total_orders': total_orders,
                'average_rating': avg_rating,
                'total_reviews': total_reviews,
                'average_delivery_time': random.uniform(25, 55),
                'order_acceptance_rate': random.uniform(0.85, 0.99),
                'on_time_delivery_rate': random.uniform(0.80, 0.95),
                'customer_satisfaction_score': avg_rating * random.uniform(0.9, 1.0),
                'featured': random.choice([True] * 1 + [False] * 9),  # 10% featured
                'promoted': random.choice([True] * 2 + [False] * 8),  # 20% promoted
                'verified': random.choice([True] * 8 + [False] * 2),  # 80% verified
                'created_at': self.fake.date_time_between(start_date='-18m', end_date='-2m'),
                'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now') if random.random() > 0.4 else None
            }
            restaurants.append(restaurant)
            
        self.db.restaurants.insert_many(restaurants)
        logger.info(f"Inserted {len(restaurants)} restaurants")
        return [restaurant['_id'] for restaurant in restaurants]
        
    def seed_menu_items(self, count: int, restaurant_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert menu item documents"""
        logger.info(f"Seeding {count} menu items...")
        
        menu_items = []
        items_per_restaurant = count // len(restaurant_ids)
        
        for restaurant_id in restaurant_ids:
            restaurant_items_count = random.randint(max(1, items_per_restaurant - 5), items_per_restaurant + 5)
            
            for i in range(restaurant_items_count):
                category = random.choice(list(self.vietnamese_dishes.keys()))
                dish_name = random.choice(self.vietnamese_dishes[category])
                
                base_price = self._generate_realistic_price(category)
                discounted_price = base_price * random.uniform(0.8, 0.95) if random.random() < 0.2 else None
                
                menu_item = {
                    '_id': ObjectId(),
                    'restaurant_id': restaurant_id,
                    'name': f"{dish_name} {random.choice(['Special', 'Deluxe', 'Traditional', 'Premium', ''])}".strip(),
                    'description': self._generate_item_description(dish_name, category),
                    'category': category,
                    'base_price': base_price,
                    'discounted_price': discounted_price,
                    'is_available': random.choice([True] * 9 + [False]),  # 90% available
                    'availability_schedule': self._generate_availability_schedule() if random.random() < 0.3 else None,
                    'max_daily_quantity': random.randint(20, 100) if random.random() < 0.4 else None,
                    'current_stock': random.randint(5, 50) if random.random() < 0.4 else None,
                    'preparation_time_minutes': random.randint(10, 30),
                    'calories': random.randint(200, 800) if random.random() > 0.3 else None,
                    'ingredients': self._generate_ingredients(dish_name),
                    'allergens': random.sample(["nuts", "dairy", "eggs", "soy", "gluten", "shellfish"], k=random.randint(0, 2)),
                    'customization_options': self._generate_customization_options(category),
                    'image_url': f"https://cdn.baemin.vn/items/{dish_name.lower().replace(' ', '_')}.jpg",
                    'image_gallery': [
                        f"https://cdn.baemin.vn/items/gallery/{dish_name.lower().replace(' ', '_')}_{j}.jpg"
                        for j in range(random.randint(1, 3))
                    ] if random.random() > 0.5 else [],
                    'total_orders': random.randint(0, 500),
                    'average_rating': random.uniform(3.5, 5.0),
                    'popularity_score': random.uniform(0, 100),
                    'spicy_level': random.randint(0, 5) if "spicy" in dish_name.lower() or random.random() < 0.3 else None,
                    'is_vegetarian': "vegetarian" in dish_name.lower() or random.random() < 0.2,
                    'is_vegan': random.random() < 0.1,
                    'is_gluten_free': random.random() < 0.15,
                    'is_featured': random.choice([True] * 1 + [False] * 9),  # 10% featured
                    'is_bestseller': random.choice([True] * 1 + [False] * 9),  # 10% bestseller
                    'created_at': self.fake.date_time_between(start_date='-12m', end_date='-1m'),
                    'updated_at': self.fake.date_time_between(start_date='-1m', end_date='now') if random.random() > 0.5 else None
                }
                menu_items.append(menu_item)
                
        self.db.menu_items.insert_many(menu_items)
        logger.info(f"Inserted {len(menu_items)} menu items")
        return [item['_id'] for item in menu_items]
        
    def seed_riders(self, count: int, city_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert rider documents"""
        logger.info(f"Seeding {count} riders...")
        
        riders = []
        for i in range(count):
            gender = random.choice(['male', 'female'])
            first_name = random.choice(self.vietnamese_first_names)
            given_name = random.choice(self.vietnamese_given_names[gender])
            
            # Generate realistic performance metrics
            total_deliveries = random.randint(100, 3000)
            success_rate = random.uniform(0.90, 0.99)
            successful_deliveries = int(total_deliveries * success_rate)
            
            rider = {
                '_id': ObjectId(),
                'first_name': first_name,
                'last_name': given_name,
                'phone': f"0{random.randint(900000000, 999999999)}",
                'email': f"{first_name.lower()}.{given_name.lower()}.rider@baemin.vn",
                'city_id': random.choice(city_ids),
                'employee_id': f"RID{i+1:04d}",
                'vehicle_type': random.choice(["motorcycle", "bicycle", "scooter", "motorbike"]),
                'vehicle_plate': f"{random.choice(['29', '30', '31', '59', '60'])}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-{random.randint(10000, 99999)}",
                'vehicle_model': random.choice(["Honda Wave", "Yamaha Jupiter", "Honda Air Blade", "Yamaha Sirius", "Suzuki Axelo"]),
                'status': random.choice([
                    RiderStatus.AVAILABLE, RiderStatus.AVAILABLE, RiderStatus.BUSY, RiderStatus.OFFLINE
                ]),
                'current_location': self._generate_random_coordinates(city_ids) if random.random() > 0.3 else None,
                'last_location_update': datetime.utcnow() - timedelta(minutes=random.randint(1, 60)) if random.random() > 0.2 else None,
                'max_concurrent_orders': random.choice([2, 3, 4, 5]),
                'current_order_count': random.randint(0, 3),
                'delivery_radius_km': random.uniform(10, 25),
                'total_deliveries': total_deliveries,
                'successful_deliveries': successful_deliveries,
                'average_delivery_time': random.uniform(25, 45),
                'average_rating': random.uniform(4.0, 5.0),
                'hourly_rate': random.uniform(25000, 40000) if random.random() > 0.5 else None,  # VND per hour
                'per_delivery_rate': random.uniform(15000, 25000),  # VND per delivery
                'bonus_eligible': random.choice([True] * 8 + [False] * 2),  # 80% bonus eligible
                'shift_start': self.fake.time() if random.random() > 0.3 else None,
                'shift_end': self.fake.time() if random.random() > 0.3 else None,
                'weekly_hours_target': random.randint(35, 48) if random.random() > 0.2 else None,
                'is_active': random.choice([True] * 9 + [False]),  # 90% active
                'background_check_passed': random.choice([True] * 9 + [False]),  # 90% passed
                'training_completed': random.choice([True] * 8 + [False] * 2),  # 80% completed
                'emergency_contact': {
                    'name': f"{random.choice(self.vietnamese_first_names)} {random.choice(self.vietnamese_given_names['female'])}",
                    'phone': f"0{random.randint(900000000, 999999999)}",
                    'relationship': random.choice(['spouse', 'parent', 'sibling', 'friend'])
                },
                'created_at': self.fake.date_time_between(start_date='-18m', end_date='-1m'),
                'updated_at': self.fake.date_time_between(start_date='-7d', end_date='now') if random.random() > 0.4 else None
            }
            riders.append(rider)
            
        self.db.riders.insert_many(riders)
        logger.info(f"Inserted {len(riders)} riders")
        return [rider['_id'] for rider in riders]
        
    def seed_orders(self, count: int, customer_ids: List[ObjectId], 
                   restaurant_ids: List[ObjectId], rider_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert order documents"""
        logger.info(f"Seeding {count} orders...")
        
        orders = []
        batch_size = 1000
        orders_inserted = 0
        
        while orders_inserted < count:
            current_batch_size = min(batch_size, count - orders_inserted)
            batch_orders = []
            
            for i in range(current_batch_size):
                customer_id = random.choice(customer_ids)
                restaurant_id = random.choice(restaurant_ids)
                rider_id = random.choice(rider_ids) if random.random() > 0.15 else None  # 85% have assigned riders
                
                # Generate order timing
                order_date = self.fake.date_time_between(start_date='-60d', end_date='now')
                
                # Generate order items
                num_items = random.randint(1, 5)
                items = self._generate_order_items(num_items)
                subtotal = sum(item['total_price'] for item in items)
                
                delivery_fee = random.uniform(15000, 30000)
                service_fee = subtotal * 0.02  # 2% service fee
                tax_amount = (subtotal + delivery_fee + service_fee) * 0.1  # 10% VAT
                discount_amount = subtotal * random.uniform(0, 0.3) if random.random() < 0.3 else 0
                total_amount = subtotal + delivery_fee + service_fee + tax_amount - discount_amount
                
                # Order status distribution
                if order_date < datetime.utcnow() - timedelta(days=1):
                    status = random.choice([
                        OrderStatus.DELIVERED] * 7 + 
                        [OrderStatus.CANCELLED] * 2 + 
                        [OrderStatus.REFUNDED] * 1
                    )
                else:
                    status = random.choice([
                        OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING,
                        OrderStatus.READY_FOR_PICKUP, OrderStatus.PICKED_UP, 
                        OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED
                    ])
                
                order = {
                    '_id': ObjectId(),
                    'order_number': f"BAE{order_date.strftime('%Y%m%d')}{orders_inserted + i + 1:06d}",
                    'customer_id': customer_id,
                    'restaurant_id': restaurant_id,
                    'rider_id': rider_id,
                    'items': items,
                    'subtotal': subtotal,
                    'delivery_fee': delivery_fee,
                    'service_fee': service_fee,
                    'tax_amount': tax_amount,
                    'discount_amount': discount_amount,
                    'total_amount': total_amount,
                    'delivery_address': self._generate_delivery_address(),
                    'delivery_coordinates': self._generate_random_coordinates(),
                    'delivery_instructions': self._generate_delivery_instructions() if random.random() > 0.6 else None,
                    'order_date': order_date,
                    'estimated_preparation_time': random.randint(15, 30),
                    'estimated_delivery_time': random.randint(30, 60),
                    'requested_delivery_time': order_date + timedelta(minutes=random.randint(45, 120)) if random.random() < 0.2 else None,
                    'status': status,
                    'status_history': self._generate_status_history(status, order_date),
                    'payment_method': random.choice(self.vietnamese_payment_methods),
                    'payment_status': self._determine_payment_status(status),
                    'payment_transaction_id': f"TXN{random.randint(1000000000, 9999999999)}" if status != OrderStatus.PENDING else None,
                    'promotion_codes': [f"PROMO{random.randint(100, 999)}"] if random.random() < 0.25 else [],
                    'loyalty_points_used': random.randint(0, 500) if random.random() < 0.15 else 0,
                    'loyalty_points_earned': int(total_amount / 1000) if status == OrderStatus.DELIVERED else 0,  # 1 point per 1000 VND
                    'contact_preference': random.choice(["phone", "app", "sms"]),
                    'special_instructions': self._generate_special_instructions() if random.random() > 0.7 else None,
                    'customer_rating': random.choice(list(ReviewRating)) if status == OrderStatus.DELIVERED and random.random() > 0.4 else None,
                    'customer_feedback': self._generate_customer_feedback() if random.random() > 0.8 else None,
                    'created_at': order_date,
                    'updated_at': order_date + timedelta(minutes=random.randint(5, 120)) if random.random() > 0.3 else None
                }
                batch_orders.append(order)
                
            self.db.orders.insert_many(batch_orders)
            orders_inserted += len(batch_orders)
            orders.extend(batch_orders)
            
            if orders_inserted % 2000 == 0:
                logger.info(f"Inserted {orders_inserted} orders...")
                
        logger.info(f"Inserted {orders_inserted} total orders")
        return [order['_id'] for order in orders]
        
    def seed_deliveries(self, count: int, order_ids: List[ObjectId], rider_ids: List[ObjectId]):
        """Generate and insert delivery documents"""
        logger.info(f"Seeding {count} deliveries...")
        
        deliveries = []
        selected_order_ids = random.sample(order_ids, min(count, len(order_ids)))
        
        for order_id in selected_order_ids:
            rider_id = random.choice(rider_ids)
            
            assigned_at = self.fake.date_time_between(start_date='-60d', end_date='now')
            pickup_time = assigned_at + timedelta(minutes=random.randint(10, 25))
            delivery_time = pickup_time + timedelta(minutes=random.randint(15, 45))
            
            status_options = [DeliveryStatus.DELIVERED] * 7 + [DeliveryStatus.FAILED] * 1 + [
                DeliveryStatus.ASSIGNED, DeliveryStatus.EN_ROUTE_TO_RESTAURANT, 
                DeliveryStatus.AT_RESTAURANT, DeliveryStatus.PICKED_UP, 
                DeliveryStatus.EN_ROUTE_TO_CUSTOMER
            ] * 2
            
            status = random.choice(status_options)
            
            delivery = {
                '_id': ObjectId(),
                'order_id': order_id,
                'rider_id': rider_id,
                'pickup_address': self._generate_restaurant_address(),
                'pickup_coordinates': self._generate_random_coordinates(),
                'delivery_address': self._generate_delivery_address(),
                'delivery_coordinates': self._generate_random_coordinates(),
                'assigned_at': assigned_at,
                'picked_up_at': pickup_time if status not in [DeliveryStatus.ASSIGNED, DeliveryStatus.EN_ROUTE_TO_RESTAURANT] else None,
                'delivered_at': delivery_time if status == DeliveryStatus.DELIVERED else None,
                'estimated_delivery_time': assigned_at + timedelta(minutes=random.randint(45, 75)),
                'status': status,
                'current_rider_location': self._generate_random_coordinates() if status not in [DeliveryStatus.DELIVERED, DeliveryStatus.FAILED] else None,
                'location_updates': self._generate_location_updates(assigned_at, status),
                'optimized_route': self._generate_optimized_route() if random.random() > 0.4 else None,
                'distance_km': random.uniform(2, 15),
                'estimated_duration_minutes': random.randint(20, 50),
                'delivery_instructions': self._generate_delivery_instructions() if random.random() > 0.5 else None,
                'delivery_proof': {
                    'photo_url': f"https://cdn.baemin.vn/delivery-proof/{order_id}.jpg",
                    'signature': "digital_signature",
                    'timestamp': delivery_time
                } if status == DeliveryStatus.DELIVERED and random.random() > 0.3 else None,
                'delivery_notes': self._generate_delivery_notes() if random.random() > 0.7 else None,
                'issues_reported': self._generate_delivery_issues() if status == DeliveryStatus.FAILED or random.random() < 0.1 else [],
                'resolution_notes': "Issue resolved successfully" if random.random() > 0.8 else None,
                'actual_delivery_time_minutes': random.randint(25, 60) if status == DeliveryStatus.DELIVERED else None,
                'customer_rating': random.choice(list(ReviewRating)) if status == DeliveryStatus.DELIVERED and random.random() > 0.4 else None,
                'rider_efficiency_score': random.uniform(75, 100) if status == DeliveryStatus.DELIVERED else None,
                'created_at': assigned_at,
                'updated_at': delivery_time if status == DeliveryStatus.DELIVERED else assigned_at + timedelta(minutes=random.randint(5, 60))
            }
            deliveries.append(delivery)
            
        self.db.deliveries.insert_many(deliveries)
        logger.info(f"Inserted {len(deliveries)} deliveries")
        
    def seed_payments(self, count: int, order_ids: List[ObjectId], customer_ids: List[ObjectId]):
        """Generate and insert payment documents"""
        logger.info(f"Seeding {count} payments...")
        
        payments = []
        for i, order_id in enumerate(random.choices(order_ids, k=count)):
            customer_id = random.choice(customer_ids)
            payment_method = random.choice(self.vietnamese_payment_methods)
            
            amount = random.uniform(50000, 500000)  # VND
            initiated_at = self.fake.date_time_between(start_date='-60d', end_date='now')
            
            # Payment status distribution
            status_weights = [
                (PaymentStatus.COMPLETED, 0.85),
                (PaymentStatus.FAILED, 0.08),
                (PaymentStatus.REFUNDED, 0.04),
                (PaymentStatus.PENDING, 0.02),
                (PaymentStatus.CANCELLED, 0.01)
            ]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]
            
            payment = {
                '_id': ObjectId(),
                'order_id': order_id,
                'customer_id': customer_id,
                'payment_method': payment_method,
                'amount': amount,
                'currency_code': 'VND',
                'transaction_id': f"PAY{random.randint(1000000000, 9999999999)}",
                'gateway_reference': f"GW{random.randint(100000, 999999)}" if payment_method != PaymentMethod.CASH else None,
                'external_transaction_id': f"EXT{random.randint(1000000, 9999999)}" if payment_method in [PaymentMethod.MOMO, PaymentMethod.ZALOPAY, PaymentMethod.GRABPAY] else None,
                'status': status,
                'initiated_at': initiated_at,
                'completed_at': initiated_at + timedelta(seconds=random.randint(10, 300)) if status == PaymentStatus.COMPLETED else None,
                'card_last_four': str(random.randint(1000, 9999)) if payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD] else None,
                'wallet_type': payment_method.value if payment_method in [PaymentMethod.MOMO, PaymentMethod.ZALOPAY, PaymentMethod.GRABPAY] else None,
                'bank_reference': f"BANK{random.randint(1000000, 9999999)}" if payment_method == PaymentMethod.BANK_TRANSFER else None,
                'processing_fee': amount * 0.025 if payment_method != PaymentMethod.CASH else 0,  # 2.5% processing fee
                'platform_fee': amount * 0.02,  # 2% platform fee
                'refund_amount': amount * random.uniform(0.5, 1.0) if status == PaymentStatus.REFUNDED else None,
                'refund_reason': random.choice([
                    "Customer request", "Order cancelled", "Service issue", "Quality concern"
                ]) if status == PaymentStatus.REFUNDED else None,
                'refunded_at': initiated_at + timedelta(days=random.randint(1, 7)) if status == PaymentStatus.REFUNDED else None,
                'risk_score': random.uniform(0, 100) if random.random() > 0.8 else None,
                'verification_status': random.choice(["verified", "pending", "failed"]),
                'settled': status == PaymentStatus.COMPLETED and random.choice([True] * 9 + [False]),
                'settlement_date': initiated_at + timedelta(days=random.randint(1, 3)) if status == PaymentStatus.COMPLETED else None,
                'settlement_amount': amount * 0.95 if status == PaymentStatus.COMPLETED else None,  # 95% after fees
                'created_at': initiated_at,
                'updated_at': initiated_at + timedelta(minutes=random.randint(1, 30)) if random.random() > 0.4 else None
            }
            payments.append(payment)
            
        self.db.payments.insert_many(payments)
        logger.info(f"Inserted {len(payments)} payments")
        
    def seed_reviews(self, count: int, order_ids: List[ObjectId], customer_ids: List[ObjectId], 
                    restaurant_ids: List[ObjectId], rider_ids: List[ObjectId]):
        """Generate and insert review documents"""
        logger.info(f"Seeding {count} reviews...")
        
        reviews = []
        for i in range(count):
            order_id = random.choice(order_ids)
            customer_id = random.choice(customer_ids)
            
            # 70% restaurant reviews, 30% rider reviews
            if random.random() < 0.7:
                restaurant_id = random.choice(restaurant_ids)
                rider_id = None
            else:
                restaurant_id = None
                rider_id = random.choice(rider_ids)
            
            overall_rating = random.choice(list(ReviewRating))
            
            review = {
                '_id': ObjectId(),
                'customer_id': customer_id,
                'restaurant_id': restaurant_id,
                'rider_id': rider_id,
                'order_id': order_id,
                'rating': overall_rating,
                'food_rating': random.choice(list(ReviewRating)) if restaurant_id else None,
                'service_rating': random.choice(list(ReviewRating)),
                'delivery_rating': random.choice(list(ReviewRating)),
                'title': self._generate_review_title(overall_rating) if random.random() > 0.4 else None,
                'comment': self._generate_review_comment(overall_rating) if random.random() > 0.3 else None,
                'photos': [
                    f"https://cdn.baemin.vn/reviews/{order_id}_{j}.jpg"
                    for j in range(random.randint(0, 3))
                ] if random.random() > 0.7 else [],
                'is_verified': True,  # All reviews are from verified orders
                'is_anonymous': random.choice([True] * 2 + [False] * 8),  # 20% anonymous
                'language': random.choice(["vi", "en"]),
                'is_approved': random.choice([True] * 95 + [False] * 5),  # 95% approved
                'moderation_notes': "Approved automatically" if random.random() > 0.9 else None,
                'flagged_content': ["spam"] if random.random() < 0.02 else [],
                'helpful_votes': random.randint(0, 25) if random.random() > 0.6 else 0,
                'total_votes': random.randint(0, 30) if random.random() > 0.6 else 0,
                'business_response': self._generate_business_response() if restaurant_id and random.random() > 0.6 else None,
                'response_date': self.fake.date_time_between(start_date='-30d', end_date='now') if random.random() > 0.7 else None,
                'created_at': self.fake.date_time_between(start_date='-60d', end_date='now'),
                'updated_at': None
            }
            reviews.append(review)
            
        self.db.reviews.insert_many(reviews)
        logger.info(f"Inserted {len(reviews)} reviews")
        
    def seed_promotions(self, count: int, city_ids: List[ObjectId], restaurant_ids: List[ObjectId]):
        """Generate and insert promotion documents"""
        logger.info(f"Seeding {count} promotions...")
        
        promotions = []
        promotion_names = [
            "Welcome New Customer", "Weekend Special", "Lunch Deal", "Free Delivery Friday",
            "Happy Hour", "Student Discount", "Flash Sale", "Bundle Deal", "Loyalty Bonus",
            "First Order Free", "Birthday Special", "Holiday Promotion", "Rainy Day Deal"
        ]
        
        for i in range(count):
            promotion_name = f"{random.choice(promotion_names)} {random.randint(1, 100)}"
            promotion_type = random.choice(list(PromotionType))
            
            start_date = self.fake.date_time_between(start_date='-30d', end_date='+30d')
            end_date = start_date + timedelta(days=random.randint(1, 60))
            
            # Set discount value based on type
            if promotion_type == PromotionType.PERCENTAGE_DISCOUNT:
                discount_value = random.randint(10, 50)  # 10-50%
                maximum_discount = random.uniform(50000, 200000)  # VND
            elif promotion_type == PromotionType.FIXED_AMOUNT_DISCOUNT:
                discount_value = random.uniform(20000, 100000)  # VND
                maximum_discount = None
            elif promotion_type == PromotionType.FREE_DELIVERY:
                discount_value = 0  # Free delivery has no direct value
                maximum_discount = None
            else:
                discount_value = random.uniform(10000, 50000)  # VND
                maximum_discount = None
            
            promotion = {
                '_id': ObjectId(),
                'code': f"BAE{random.choice(['MIN', 'MAX', 'NEW', 'VIP', 'HOT'])}{random.randint(100, 999)}",
                'name': promotion_name,
                'description': self._generate_promotion_description(promotion_type, discount_value),
                'promotion_type': promotion_type,
                'discount_value': discount_value,
                'maximum_discount': maximum_discount,
                'minimum_order_value': random.choice([0, 100000, 200000, 300000]),  # VND
                'start_date': start_date,
                'end_date': end_date,
                'total_usage_limit': random.choice([None, 100, 500, 1000, 5000]),
                'per_customer_limit': random.randint(1, 5),
                'current_usage_count': random.randint(0, 100),
                'applicable_cities': random.sample(city_ids, k=random.randint(1, len(city_ids))) if random.random() > 0.3 else [],
                'applicable_restaurants': random.sample(restaurant_ids, k=random.randint(0, min(10, len(restaurant_ids)))) if random.random() > 0.7 else [],
                'customer_segments': random.sample(
                    ["new_customer", "vip", "frequent_user", "inactive", "high_value"],
                    k=random.randint(0, 2)
                ),
                'new_customers_only': random.choice([True] * 3 + [False] * 7),  # 30% new customer only
                'terms_conditions': "Valid for limited time only. Cannot be combined with other offers. Terms and conditions apply.",
                'is_active': random.choice([True] * 8 + [False] * 2),  # 80% active
                'is_featured': random.choice([True] * 2 + [False] * 8),  # 20% featured
                'auto_apply': random.choice([True] * 1 + [False] * 9),  # 10% auto-apply
                'total_orders': random.randint(0, 500),
                'total_discount_given': random.uniform(0, 10000000),  # VND
                'conversion_rate': random.uniform(0.05, 0.40),  # 5-40% conversion
                'created_at': self.fake.date_time_between(start_date='-60d', end_date='now'),
                'updated_at': self.fake.date_time_between(start_date='-7d', end_date='now') if random.random() > 0.5 else None
            }
            promotions.append(promotion)
            
        self.db.promotions.insert_many(promotions)
        logger.info(f"Inserted {len(promotions)} promotions")
        
    def create_indexes(self):
        """Create indexes as defined in the schema"""
        logger.info("Creating database indexes...")
        
        for collection_name, collection_schema in database_schema.collections.items():
            collection = self.db[collection_name]
            for index_def in collection_schema.indexes:
                try:
                    if "2dsphere" in str(index_def.keys):
                        # Handle geospatial indexes
                        field_name = list(index_def.keys.keys())[0]
                        collection.create_index(
                            [(field_name, "2dsphere")],
                            name=index_def.name,
                            sparse=index_def.sparse,
                            background=index_def.background
                        )
                    else:
                        # Handle regular indexes
                        index_keys = [(field, direction.value) for field, direction in index_def.keys.items()]
                        collection.create_index(
                            index_keys,
                            name=index_def.name,
                            unique=index_def.unique,
                            sparse=index_def.sparse,
                            background=index_def.background
                        )
                    logger.info(f"Created index '{index_def.name}' on collection '{collection_name}'")
                except Exception as e:
                    logger.warning(f"Failed to create index '{index_def.name}' on '{collection_name}': {e}")
                    
        logger.info("Index creation completed")
        
    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        logger.info("Clearing database...")
        
        for collection_name in database_schema.collections.keys():
            self.db[collection_name].drop()
            logger.info(f"Dropped collection '{collection_name}'")
            
        logger.info("Database cleared")
        
    def validate_seed_data(self):
        """Validate the seeded data meets quality standards"""
        logger.info("Validating seeded data...")
        
        # Check collection counts
        for collection_name in database_schema.collections.keys():
            count = self.db[collection_name].count_documents({})
            logger.info(f"Collection '{collection_name}': {count} documents")
            
        # Check referential integrity
        self._validate_referential_integrity()
        
        # Check data distribution
        self._validate_data_distribution()
        
        logger.info("Data validation completed successfully!")
        
    # Helper methods for data generation
    def _generate_delivery_addresses(self, count: int) -> List[Dict[str, Any]]:
        """Generate realistic delivery addresses"""
        addresses = []
        for i in range(count):
            addresses.append({
                'label': random.choice(['Home', 'Office', 'Other']),
                'street': f"{random.randint(1, 999)} {random.choice(['Nguyen Van', 'Le Loi', 'Tran Hung Dao', 'Ba Trieu'])} Street",
                'ward': f"Ward {random.randint(1, 28)}",
                'district': f"District {random.randint(1, 12)}",
                'city': random.choice([city['name'] for city in self.vietnamese_cities]),
                'coordinates': {'latitude': random.uniform(10.0, 21.5), 'longitude': random.uniform(105.0, 109.5)},
                'is_default': i == 0
            })
        return addresses
        
    def _generate_restaurant_name(self, cuisine: str) -> str:
        """Generate realistic restaurant names based on cuisine"""
        if cuisine == "Vietnamese":
            prefixes = ["Pho", "Com", "Bun", "Quan", "Nha Hang"]
            suffixes = ["Saigon", "Hanoi", "Hue", "Viet", "Ngon"]
        elif cuisine == "Korean":
            prefixes = ["Seoul", "Kimchi", "BBQ", "K-"]
            suffixes = ["House", "Kitchen", "Grill", "Restaurant"]
        elif cuisine == "Japanese":
            prefixes = ["Sushi", "Ramen", "Tokyo", "Sakura"]
            suffixes = ["Ya", "House", "Kitchen", "Sushi Bar"]
        else:
            prefixes = ["Golden", "Royal", "Fresh", "Delicious"]
            suffixes = ["House", "Kitchen", "Restaurant", "Cafe"]
            
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
        
    def _generate_restaurant_address(self) -> Dict[str, str]:
        """Generate realistic restaurant addresses"""
        return {
            'street': f"{random.randint(1, 999)} {random.choice(['Nguyen Van Linh', 'Le Loi', 'Tran Hung Dao', 'Nguyen Hue'])} Street",
            'ward': f"Ward {random.randint(1, 28)}",
            'district': f"District {random.randint(1, 12)}",
            'city': random.choice([city['name'] for city in self.vietnamese_cities]),
            'postal_code': str(random.randint(700000, 799999))
        }
        
    def _generate_coordinates_near_city(self, city_id: ObjectId, city_ids: List[ObjectId]) -> Dict[str, float]:
        """Generate coordinates near a specific city"""
        city_index = city_ids.index(city_id)
        base_coords = self.vietnamese_cities[city_index]['coords']
        
        # Add random offset within ~20km
        lat_offset = random.uniform(-0.2, 0.2)
        lng_offset = random.uniform(-0.2, 0.2)
        
        return {
            'latitude': base_coords[0] + lat_offset,
            'longitude': base_coords[1] + lng_offset
        }
        
    def _generate_opening_hours(self) -> Dict[str, Dict[str, str]]:
        """Generate realistic restaurant opening hours"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        hours = {}
        
        for day in days:
            if random.random() > 0.1:  # 90% chance restaurant is open
                start_hour = random.choice(['06:00', '07:00', '08:00', '09:00', '10:00'])
                end_hour = random.choice(['21:00', '22:00', '23:00', '00:00'])
                hours[day] = {'open': start_hour, 'close': end_hour}
            else:
                hours[day] = {'open': None, 'close': None}  # Closed
                
        return hours
        
    def _generate_realistic_price(self, category: str) -> float:
        """Generate realistic Vietnamese food prices"""
        price_ranges = {
            "Noodle Soup": (25000, 60000),
            "Rice Dishes": (30000, 80000),
            "Noodle Dishes": (25000, 70000),
            "Street Food": (15000, 45000),
            "Drinks": (10000, 35000),
            "Desserts": (15000, 50000)
        }
        
        min_price, max_price = price_ranges.get(category, (20000, 100000))
        return random.uniform(min_price, max_price)
        
    def _generate_item_description(self, dish_name: str, category: str) -> str:
        """Generate realistic item descriptions"""
        descriptions = {
            "Pho Bo": "Traditional Vietnamese beef noodle soup with fresh herbs and spices",
            "Com Tam": "Broken rice served with grilled pork, pickled vegetables, and fish sauce",
            "Banh Mi": "Vietnamese sandwich with fresh vegetables, meat, and homemade sauce",
            "Bun Cha": "Grilled pork served with rice vermicelli and fresh herbs"
        }
        
        return descriptions.get(dish_name, f"Delicious {dish_name.lower()} made with fresh ingredients and authentic Vietnamese flavors. Perfect for lunch or dinner.")
        
    def _generate_ingredients(self, dish_name: str) -> List[str]:
        """Generate realistic ingredient lists"""
        common_ingredients = {
            "Pho Bo": ["beef", "rice noodles", "onions", "ginger", "star anise", "cinnamon", "fish sauce"],
            "Com Tam": ["broken rice", "grilled pork", "pickled vegetables", "cucumber", "tomato", "fish sauce"],
            "Banh Mi": ["baguette", "pate", "Vietnamese ham", "cilantro", "cucumber", "pickled carrots"],
            "Bun Cha": ["rice vermicelli", "grilled pork", "lettuce", "herbs", "fish sauce", "vinegar"]
        }
        
        return common_ingredients.get(dish_name, ["rice", "vegetables", "herbs", "fish sauce", "garlic", "onions"])
        
    def _generate_customization_options(self, category: str) -> List[Dict[str, Any]]:
        """Generate menu item customization options"""
        options = []
        
        if category in ["Noodle Soup", "Noodle Dishes"]:
            options.append({
                'name': 'Noodle Amount',
                'type': 'single_choice',
                'required': True,
                'options': [
                    {'label': 'Regular', 'price': 0},
                    {'label': 'Extra', 'price': 5000}
                ]
            })
            
        if category in ["Rice Dishes", "Noodle Soup"]:
            options.append({
                'name': 'Spice Level',
                'type': 'single_choice',
                'required': False,
                'options': [
                    {'label': 'Mild', 'price': 0},
                    {'label': 'Medium', 'price': 0},
                    {'label': 'Spicy', 'price': 0}
                ]
            })
            
        # Add-ons
        options.append({
            'name': 'Add-ons',
            'type': 'multiple_choice',
            'required': False,
            'options': [
                {'label': 'Extra vegetables', 'price': 8000},
                {'label': 'Extra meat', 'price': 15000},
                {'label': 'Fried egg', 'price': 10000}
            ]
        })
        
        return options
        
    def _generate_availability_schedule(self) -> Dict[str, Any]:
        """Generate time-based availability for menu items"""
        return {
            'breakfast': {'start': '06:00', 'end': '10:00'},
            'lunch': {'start': '11:00', 'end': '14:00'},
            'dinner': {'start': '17:00', 'end': '22:00'}
        }
        
    def _generate_random_coordinates(self, city_ids: List[ObjectId] = None) -> Dict[str, float]:
        """Generate random coordinates in Vietnam"""
        if city_ids:
            city = random.choice(self.vietnamese_cities[:len(city_ids)])
            base_lat, base_lng = city['coords']
            lat_offset = random.uniform(-0.1, 0.1)
            lng_offset = random.uniform(-0.1, 0.1)
            return {
                'latitude': base_lat + lat_offset,
                'longitude': base_lng + lng_offset
            }
        else:
            return {
                'latitude': random.uniform(10.0, 21.5),
                'longitude': random.uniform(105.0, 109.5)
            }
            
    def _generate_order_items(self, count: int) -> List[Dict[str, Any]]:
        """Generate realistic order items"""
        items = []
        for i in range(count):
            base_price = random.uniform(25000, 150000)  # VND
            quantity = random.randint(1, 3)
            total_price = base_price * quantity
            
            item = {
                'menu_item_id': ObjectId(),
                'name': random.choice([dish for dishes in self.vietnamese_dishes.values() for dish in dishes]),
                'base_price': base_price,
                'quantity': quantity,
                'customizations': [
                    {'name': 'Spice Level', 'value': 'Medium', 'price': 0}
                ] if random.random() > 0.7 else [],
                'special_instructions': "No onions" if random.random() > 0.8 else None,
                'total_price': total_price
            }
            items.append(item)
            
        return items
        
    def _generate_delivery_address(self) -> Dict[str, str]:
        """Generate delivery address"""
        return {
            'street': f"{random.randint(1, 999)} {random.choice(['Nguyen Van', 'Le Loi', 'Tran Hung Dao'])} Street",
            'ward': f"Ward {random.randint(1, 28)}",
            'district': f"District {random.randint(1, 12)}",
            'city': random.choice([city['name'] for city in self.vietnamese_cities]),
            'landmark': random.choice(['Near ABC Mall', 'Opposite XYZ School', 'Next to Coffee Shop']) if random.random() > 0.6 else None
        }
        
    def _generate_delivery_instructions(self) -> str:
        """Generate delivery instructions"""
        instructions = [
            "Call when you arrive",
            "Leave at the door",
            "Ring the doorbell",
            "Meet at the lobby",
            "Apartment 3B, 2nd floor",
            "Use the back entrance",
            "Contact security first"
        ]
        return random.choice(instructions)
        
    def _generate_status_history(self, current_status: OrderStatus, order_date: datetime) -> List[Dict[str, Any]]:
        """Generate order status change history"""
        history = []
        statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.READY_FOR_PICKUP,
            OrderStatus.PICKED_UP,
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED
        ]
        
        current_time = order_date
        for status in statuses:
            history.append({
                'status': status,
                'timestamp': current_time,
                'notes': f"Order {status.value}"
            })
            current_time += timedelta(minutes=random.randint(5, 20))
            
            if status == current_status:
                break
                
        return history
        
    def _determine_payment_status(self, order_status: OrderStatus) -> PaymentStatus:
        """Determine payment status based on order status"""
        if order_status == OrderStatus.DELIVERED:
            return PaymentStatus.COMPLETED
        elif order_status == OrderStatus.CANCELLED:
            return random.choice([PaymentStatus.CANCELLED, PaymentStatus.REFUNDED])
        elif order_status == OrderStatus.PENDING:
            return PaymentStatus.PENDING
        else:
            return PaymentStatus.PROCESSING
            
    def _generate_special_instructions(self) -> str:
        """Generate special order instructions"""
        instructions = [
            "Extra spicy please",
            "No ice in drinks",
            "Pack soup separately",
            "Include extra napkins",
            "Cut into small pieces",
            "Add extra sauce on the side"
        ]
        return random.choice(instructions)
        
    def _generate_customer_feedback(self) -> str:
        """Generate customer feedback"""
        feedback_options = [
            "Food was delicious and delivered hot!",
            "Great service, will order again",
            "Delivery was a bit slow but food was good",
            "Perfect portion size and taste",
            "Could use more vegetables in the dish"
        ]
        return random.choice(feedback_options)
        
    def _generate_location_updates(self, start_time: datetime, status: DeliveryStatus) -> List[Dict[str, Any]]:
        """Generate GPS location updates for delivery tracking"""
        updates = []
        current_time = start_time
        
        for i in range(random.randint(3, 8)):
            updates.append({
                'timestamp': current_time,
                'latitude': random.uniform(10.0, 21.5),
                'longitude': random.uniform(105.0, 109.5),
                'accuracy': random.uniform(5, 15),  # GPS accuracy in meters
                'speed': random.uniform(15, 45) if i > 0 else 0  # km/h
            })
            current_time += timedelta(minutes=random.randint(3, 10))
            
        return updates
        
    def _generate_optimized_route(self) -> List[Dict[str, float]]:
        """Generate optimized delivery route waypoints"""
        waypoints = []
        for _ in range(random.randint(3, 6)):
            waypoints.append({
                'latitude': random.uniform(10.0, 21.5),
                'longitude': random.uniform(105.0, 109.5),
                'order': len(waypoints) + 1
            })
        return waypoints
        
    def _generate_delivery_notes(self) -> str:
        """Generate delivery notes from rider"""
        notes = [
            "Delivered to customer directly",
            "Left with security guard",
            "Customer was not available, left with neighbor",
            "Delivered to office reception",
            "Smooth delivery, customer was waiting"
        ]
        return random.choice(notes)
        
    def _generate_delivery_issues(self) -> List[Dict[str, Any]]:
        """Generate delivery issues"""
        issues = [
            {'type': 'address_not_found', 'description': 'Unable to locate the delivery address'},
            {'type': 'customer_not_available', 'description': 'Customer did not answer phone calls'},
            {'type': 'vehicle_breakdown', 'description': 'Motorcycle had technical issues'},
            {'type': 'weather_delay', 'description': 'Heavy rain caused delivery delay'},
            {'type': 'traffic_jam', 'description': 'Unexpected traffic congestion'}
        ]
        return [random.choice(issues)]
        
    def _generate_review_title(self, rating: ReviewRating) -> str:
        """Generate review titles based on rating"""
        titles = {
            ReviewRating.FIVE_STARS: ["Excellent food!", "Amazing service", "Perfect meal", "Highly recommended"],
            ReviewRating.FOUR_STARS: ["Very good", "Tasty food", "Good experience", "Will order again"],
            ReviewRating.THREE_STARS: ["Decent food", "Average experience", "Could be better", "Okay service"],
            ReviewRating.TWO_STARS: ["Below expectations", "Not great", "Disappointed", "Could improve"],
            ReviewRating.ONE_STAR: ["Terrible experience", "Very poor", "Worst meal ever", "Never again"]
        }
        return random.choice(titles[rating])
        
    def _generate_review_comment(self, rating: ReviewRating) -> str:
        """Generate review comments based on rating"""
        comments = {
            ReviewRating.FIVE_STARS: [
                "The food was absolutely delicious and delivered hot. Excellent packaging and fast delivery!",
                "Amazing taste and generous portions. The restaurant really knows how to make authentic Vietnamese food.",
                "Perfect delivery experience. Food arrived exactly on time and the rider was very professional."
            ],
            ReviewRating.FOUR_STARS: [
                "Good food overall, delivery was quick. Just wish there were larger portions for the price.",
                "Tasty meal and decent delivery time. Would definitely order again from this restaurant.",
                "The pho was very good, though not the best I've had. Service was reliable."
            ],
            ReviewRating.THREE_STARS: [
                "Food was okay, nothing special. Delivery took longer than expected but arrived warm.",
                "Average taste, reasonable price. The packaging could be better to prevent spills.",
                "Decent meal but had higher expectations based on reviews. Service was standard."
            ],
            ReviewRating.TWO_STARS: [
                "Food was cold when it arrived and took much longer than estimated. Disappointing.",
                "The taste was below average and portions were smaller than expected. Not worth the price.",
                "Poor packaging led to spillage. Food quality was not up to standard."
            ],
            ReviewRating.ONE_STAR: [
                "Terrible experience. Food was cold, delivery was extremely late, and taste was awful.",
                "Worst meal I've ever ordered. Everything was wrong and customer service was unhelpful.",
                "Complete waste of money. Food was inedible and delivery was a disaster."
            ]
        }
        return random.choice(comments[rating])
        
    def _generate_business_response(self) -> str:
        """Generate business responses to reviews"""
        responses = [
            "Thank you so much for your wonderful review! We're delighted you enjoyed your meal.",
            "We appreciate your feedback and are glad you had a positive experience with our restaurant.",
            "Thank you for choosing our restaurant. We're sorry to hear about the issue and will improve.",
            "We value your honest feedback and will work hard to provide better service next time.",
            "Thank you for your review. We're constantly working to improve our food and service quality."
        ]
        return random.choice(responses)
        
    def _generate_promotion_description(self, promo_type: PromotionType, value: float) -> str:
        """Generate promotion descriptions"""
        descriptions = {
            PromotionType.PERCENTAGE_DISCOUNT: f"Get {int(value)}% off your order! Limited time offer.",
            PromotionType.FIXED_AMOUNT_DISCOUNT: f"Save {int(value):,} VND on your next order. Don't miss out!",
            PromotionType.FREE_DELIVERY: "Enjoy free delivery on all orders. Order now and save!",
            PromotionType.BUY_ONE_GET_ONE: "Buy one get one free on selected items. Perfect for sharing!",
            PromotionType.CASHBACK: f"Get {int(value):,} VND cashback on your order. Money back guaranteed!"
        }
        return descriptions.get(promo_type, "Special promotion available for limited time!")
        
    def _validate_referential_integrity(self):
        """Validate referential integrity across collections"""
        logger.info("Checking referential integrity...")
        
        # Check city references
        city_ids = set(doc['_id'] for doc in self.db.cities.find({}, {'_id': 1}))
        
        invalid_customer_cities = self.db.customers.count_documents({
            'primary_city_id': {'$nin': list(city_ids)}
        })
        if invalid_customer_cities > 0:
            raise ValueError(f"Found {invalid_customer_cities} customers with invalid city references")
            
        # Check restaurant references
        restaurant_ids = set(doc['_id'] for doc in self.db.restaurants.find({}, {'_id': 1}))
        
        invalid_order_restaurants = self.db.orders.count_documents({
            'restaurant_id': {'$nin': list(restaurant_ids)}
        })
        if invalid_order_restaurants > 0:
            raise ValueError(f"Found {invalid_order_restaurants} orders with invalid restaurant references")
            
        logger.info("Referential integrity check passed")
        
    def _validate_data_distribution(self):
        """Validate data distribution patterns"""
        logger.info("Checking data distribution...")
        
        # Check order status distribution
        total_orders = self.db.orders.count_documents({})
        if total_orders > 0:
            delivered_orders = self.db.orders.count_documents({'status': OrderStatus.DELIVERED})
            delivered_ratio = delivered_orders / total_orders
            logger.info(f"Delivered orders ratio: {delivered_ratio:.2%}")
            
        # Check payment method distribution
        payment_methods = {}
        for doc in self.db.orders.find({}, {'payment_method': 1}):
            method = doc['payment_method']
            payment_methods[method] = payment_methods.get(method, 0) + 1
            
        logger.info(f"Payment method distribution: {payment_methods}")
        
        # Check average order value
        pipeline = [
            {"$group": {"_id": None, "avg_total": {"$avg": "$total_amount"}}},
            {"$project": {"_id": 0, "avg_total": 1}}
        ]
        result = list(self.db.orders.aggregate(pipeline))
        if result:
            avg_order_value = result[0]['avg_total']
            logger.info(f"Average order value: {avg_order_value:,.0f} VND")
            
        logger.info("Data distribution check completed")


def seed_database(connection_string: str = "mongodb://localhost:27017", 
                 num_records: Optional[Dict[str, int]] = None):
    """
    Seed the food delivery database with realistic sample data
    
    Args:
        connection_string: MongoDB connection string
        num_records: Dictionary specifying number of records per collection
    """
    seeder = FoodDeliverySeeder(connection_string)
    
    # Clear existing data
    seeder.clear_database()
    
    # Seed with sample data
    seeder.seed_all_collections(num_records)
    
    # Create indexes
    seeder.create_indexes()
    
    # Validate the seeded data
    seeder.validate_seed_data()
    
    return seeder


if __name__ == "__main__":
    import os
    
    # Get connection string from environment or use default
    connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Default record counts for a comprehensive food delivery dataset
    record_counts = {
        'cities': 8,          # Vietnamese cities
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
    
    try:
        seeder = seed_database(connection_string, record_counts)
        print(f"✓ Successfully seeded database '{database_schema.database_name}'")
        print("Food delivery database ready with realistic Vietnamese market data!")
        
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        raise