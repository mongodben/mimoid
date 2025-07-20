"""Database schema for BAEMIN Food Delivery Platform"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, validator
from enum import Enum
from decimal import Decimal

# Import base types from mimiod package
from mimiod import (
    IndexDirection,
    IndexDefinition,
    BaseCollectionSchema,
    BaseMongoDbSchema,
    PyObjectId,
    BaseMongoDbDocumentSchema,
)


# Enums for constrained fields
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    PICKED_UP = "picked_up"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class RiderStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ON_BREAK = "on_break"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    MOMO = "momo"
    ZALOPAY = "zalopay"
    GRABPAY = "grabpay"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class RestaurantStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"


class DeliveryStatus(str, Enum):
    ASSIGNED = "assigned"
    EN_ROUTE_TO_RESTAURANT = "en_route_to_restaurant"
    AT_RESTAURANT = "at_restaurant"
    PICKED_UP = "picked_up"
    EN_ROUTE_TO_CUSTOMER = "en_route_to_customer"
    DELIVERED = "delivered"
    FAILED = "failed"


class PromotionType(str, Enum):
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FIXED_AMOUNT_DISCOUNT = "fixed_amount_discount"
    FREE_DELIVERY = "free_delivery"
    BUY_ONE_GET_ONE = "buy_one_get_one"
    CASHBACK = "cashback"


class ReviewRating(int, Enum):
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5


# Document schemas
class City(BaseMongoDbDocumentSchema):
    # Basic city information
    city_name: str = Field(..., max_length=100)
    city_code: str = Field(..., max_length=10, description="Unique city identifier")
    country: str = Field(..., max_length=100)
    
    # Geographic information
    coordinates: Dict[str, float] = Field(..., description="City center coordinates")
    timezone: str = Field(..., max_length=50)
    
    # Operational configuration
    is_active: bool = Field(default=True)
    launch_date: datetime = Field(...)
    
    # Delivery configuration
    base_delivery_fee: float = Field(..., ge=0, description="Base delivery fee in local currency")
    max_delivery_radius_km: float = Field(..., ge=0, description="Maximum delivery distance")
    peak_hours: List[Dict[str, str]] = Field(default=[], description="Peak delivery time windows")
    
    # Localization
    currency_code: str = Field(..., max_length=3, description="ISO currency code")
    language_code: str = Field(..., max_length=5, description="Primary language")
    
    # Regulatory settings
    operating_license: Optional[str] = Field(None, max_length=100)
    tax_rate: float = Field(default=0.0, ge=0, le=1, description="Local tax rate")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Customer(BaseMongoDbDocumentSchema):
    # Personal information
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=255, description="Unique email address")
    phone: str = Field(..., max_length=20)
    
    # Account details
    password_hash: str = Field(..., description="Hashed password")
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    
    # Location and preferences
    primary_city_id: PyObjectId = Field(..., description="Primary city for operations")
    delivery_addresses: List[Dict[str, Any]] = Field(default=[], description="Saved delivery addresses")
    favorite_cuisines: List[str] = Field(default=[], description="Preferred cuisine types")
    dietary_restrictions: List[str] = Field(default=[], description="Allergies and dietary needs")
    
    # Profile data
    date_of_birth: Optional[datetime] = Field(None)
    avatar_url: Optional[str] = Field(None)
    loyalty_tier: str = Field(default="bronze", max_length=20)
    
    # Computed metrics
    total_orders: int = Field(default=0, ge=0)
    total_spent: float = Field(default=0.0, ge=0)
    average_order_value: float = Field(default=0.0, ge=0)
    average_rating_given: float = Field(default=0.0, ge=0, le=5)
    
    # Engagement metrics
    last_order_date: Optional[datetime] = Field(None)
    app_version: Optional[str] = Field(None, max_length=20)
    device_info: Dict[str, str] = Field(default={})
    
    # Status and settings
    is_active: bool = Field(default=True)
    marketing_opt_in: bool = Field(default=True)
    push_notifications: bool = Field(default=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Restaurant(BaseMongoDbDocumentSchema):
    # Basic restaurant information
    name: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    cuisine_type: List[str] = Field(..., description="Types of cuisine offered")
    
    # Location and contact
    city_id: PyObjectId = Field(..., description="Operating city")
    address: Dict[str, str] = Field(..., description="Full address details")
    coordinates: Dict[str, float] = Field(..., description="GPS coordinates")
    phone: str = Field(..., max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    
    # Business details
    business_license: str = Field(..., max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    owner_name: str = Field(..., max_length=100)
    
    # Operational settings
    status: RestaurantStatus = Field(default=RestaurantStatus.PENDING_APPROVAL)
    opening_hours: Dict[str, Dict[str, str]] = Field(..., description="Weekly operating hours")
    preparation_time_minutes: int = Field(..., ge=5, le=120, description="Average order preparation time")
    
    # Delivery settings
    delivery_radius_km: float = Field(..., ge=0, le=50, description="Maximum delivery distance")
    minimum_order_value: float = Field(default=0.0, ge=0)
    delivery_fee: float = Field(default=0.0, ge=0, description="Restaurant-specific delivery fee")
    
    # Financial settings
    commission_rate: float = Field(..., ge=0, le=1, description="Platform commission rate")
    payment_method: str = Field(..., max_length=50, description="How restaurant receives payments")
    
    # Media and branding
    logo_url: Optional[str] = Field(None)
    cover_image_url: Optional[str] = Field(None)
    gallery_images: List[str] = Field(default=[], description="Restaurant photos")
    
    # Computed metrics
    total_orders: int = Field(default=0, ge=0)
    average_rating: float = Field(default=0.0, ge=0, le=5)
    total_reviews: int = Field(default=0, ge=0)
    average_delivery_time: float = Field(default=0.0, ge=0, description="Average delivery time in minutes")
    
    # Performance metrics
    order_acceptance_rate: float = Field(default=1.0, ge=0, le=1)
    on_time_delivery_rate: float = Field(default=1.0, ge=0, le=1)
    customer_satisfaction_score: float = Field(default=0.0, ge=0, le=5)
    
    # Status flags
    featured: bool = Field(default=False)
    promoted: bool = Field(default=False)
    verified: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class MenuItem(BaseMongoDbDocumentSchema):
    restaurant_id: PyObjectId = Field(..., description="Parent restaurant")
    
    # Basic item information
    name: str = Field(..., max_length=200)
    description: str = Field(..., max_length=500)
    category: str = Field(..., max_length=100, description="Menu category")
    
    # Pricing
    base_price: float = Field(..., gt=0, description="Base price in local currency")
    discounted_price: Optional[float] = Field(None, ge=0, description="Sale price if applicable")
    
    # Availability
    is_available: bool = Field(default=True)
    availability_schedule: Optional[Dict[str, Any]] = Field(None, description="Time-based availability")
    max_daily_quantity: Optional[int] = Field(None, ge=0, description="Daily stock limit")
    current_stock: Optional[int] = Field(None, ge=0)
    
    # Item details
    preparation_time_minutes: int = Field(default=15, ge=1, le=60)
    calories: Optional[int] = Field(None, ge=0)
    ingredients: List[str] = Field(default=[], description="Main ingredients")
    allergens: List[str] = Field(default=[], description="Allergen information")
    
    # Customization options
    customization_options: List[Dict[str, Any]] = Field(default=[], description="Size, extras, modifications")
    
    # Media
    image_url: Optional[str] = Field(None)
    image_gallery: List[str] = Field(default=[], description="Additional item photos")
    
    # Performance metrics
    total_orders: int = Field(default=0, ge=0)
    average_rating: float = Field(default=0.0, ge=0, le=5)
    popularity_score: float = Field(default=0.0, ge=0, description="Algorithm-based popularity")
    
    # Flags
    spicy_level: Optional[int] = Field(None, ge=0, le=5, description="Spiciness rating")
    is_vegetarian: bool = Field(default=False)
    is_vegan: bool = Field(default=False)
    is_gluten_free: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    is_bestseller: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Rider(BaseMongoDbDocumentSchema):
    # Personal information
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=255)
    
    # Work assignment
    city_id: PyObjectId = Field(..., description="Operating city")
    employee_id: str = Field(..., max_length=50, description="Company employee ID")
    
    # Vehicle information
    vehicle_type: str = Field(..., max_length=50, description="Motorcycle, bicycle, car, etc.")
    vehicle_plate: str = Field(..., max_length=20)
    vehicle_model: Optional[str] = Field(None, max_length=100)
    
    # Current status
    status: RiderStatus = Field(default=RiderStatus.OFFLINE)
    current_location: Optional[Dict[str, float]] = Field(None, description="Current GPS coordinates")
    last_location_update: Optional[datetime] = Field(None)
    
    # Capacity and limits
    max_concurrent_orders: int = Field(default=3, ge=1, le=10)
    current_order_count: int = Field(default=0, ge=0)
    delivery_radius_km: float = Field(default=15.0, ge=0, le=50)
    
    # Performance metrics
    total_deliveries: int = Field(default=0, ge=0)
    successful_deliveries: int = Field(default=0, ge=0)
    average_delivery_time: float = Field(default=0.0, ge=0, description="Average delivery time in minutes")
    average_rating: float = Field(default=0.0, ge=0, le=5)
    
    # Financial information
    hourly_rate: Optional[float] = Field(None, ge=0, description="Base hourly pay")
    per_delivery_rate: float = Field(..., ge=0, description="Payment per delivery")
    bonus_eligible: bool = Field(default=True)
    
    # Work schedule
    shift_start: Optional[datetime] = Field(None)
    shift_end: Optional[datetime] = Field(None)
    weekly_hours_target: Optional[int] = Field(None, ge=0, le=168)
    
    # Account status
    is_active: bool = Field(default=True)
    background_check_passed: bool = Field(default=False)
    training_completed: bool = Field(default=False)
    
    # Emergency contact
    emergency_contact: Dict[str, str] = Field(default={}, description="Emergency contact information")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Order(BaseMongoDbDocumentSchema):
    # Order identification
    order_number: str = Field(..., max_length=50, description="Human-readable order number")
    
    # Parties involved
    customer_id: PyObjectId = Field(..., description="Customer who placed the order")
    restaurant_id: PyObjectId = Field(..., description="Restaurant fulfilling the order")
    rider_id: Optional[PyObjectId] = Field(None, description="Assigned delivery rider")
    
    # Order details
    items: List[Dict[str, Any]] = Field(..., description="Ordered items with customizations")
    subtotal: float = Field(..., ge=0, description="Items total before fees and discounts")
    delivery_fee: float = Field(default=0.0, ge=0)
    service_fee: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    total_amount: float = Field(..., gt=0, description="Final amount to be paid")
    
    # Delivery information
    delivery_address: Dict[str, str] = Field(..., description="Complete delivery address")
    delivery_coordinates: Dict[str, float] = Field(..., description="GPS coordinates")
    delivery_instructions: Optional[str] = Field(None, max_length=500)
    
    # Timing
    order_date: datetime = Field(default_factory=datetime.utcnow)
    estimated_preparation_time: int = Field(..., ge=5, description="Minutes for preparation")
    estimated_delivery_time: int = Field(..., ge=10, description="Total estimated delivery time")
    requested_delivery_time: Optional[datetime] = Field(None, description="Customer requested time")
    
    # Status tracking
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    status_history: List[Dict[str, Any]] = Field(default=[], description="Status change timeline")
    
    # Payment information
    payment_method: PaymentMethod = Field(...)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_transaction_id: Optional[str] = Field(None, max_length=100)
    
    # Promotions and discounts
    promotion_codes: List[str] = Field(default=[], description="Applied promotion codes")
    loyalty_points_used: int = Field(default=0, ge=0)
    loyalty_points_earned: int = Field(default=0, ge=0)
    
    # Special requirements
    contact_preference: str = Field(default="phone", max_length=20, description="How to contact customer")
    special_instructions: Optional[str] = Field(None, max_length=1000)
    
    # Ratings and feedback
    customer_rating: Optional[ReviewRating] = Field(None, description="Customer's rating of the order")
    customer_feedback: Optional[str] = Field(None, max_length=1000)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Delivery(BaseMongoDbDocumentSchema):
    order_id: PyObjectId = Field(..., description="Associated order")
    rider_id: PyObjectId = Field(..., description="Assigned rider")
    
    # Route information
    pickup_address: Dict[str, str] = Field(..., description="Restaurant pickup address")
    pickup_coordinates: Dict[str, float] = Field(..., description="Pickup GPS coordinates")
    delivery_address: Dict[str, str] = Field(..., description="Customer delivery address")
    delivery_coordinates: Dict[str, float] = Field(..., description="Delivery GPS coordinates")
    
    # Timing
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    picked_up_at: Optional[datetime] = Field(None)
    delivered_at: Optional[datetime] = Field(None)
    estimated_delivery_time: datetime = Field(...)
    
    # Status and tracking
    status: DeliveryStatus = Field(default=DeliveryStatus.ASSIGNED)
    current_rider_location: Optional[Dict[str, float]] = Field(None)
    location_updates: List[Dict[str, Any]] = Field(default=[], description="GPS tracking history")
    
    # Route optimization
    optimized_route: Optional[List[Dict[str, float]]] = Field(None, description="Calculated optimal route")
    distance_km: Optional[float] = Field(None, ge=0, description="Total delivery distance")
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    
    # Delivery details
    delivery_instructions: Optional[str] = Field(None, max_length=500)
    delivery_proof: Optional[Dict[str, Any]] = Field(None, description="Photo or signature proof")
    delivery_notes: Optional[str] = Field(None, max_length=500, description="Rider's delivery notes")
    
    # Issues and resolution
    issues_reported: List[Dict[str, Any]] = Field(default=[], description="Delivery problems")
    resolution_notes: Optional[str] = Field(None, max_length=1000)
    
    # Performance tracking
    actual_delivery_time_minutes: Optional[int] = Field(None, ge=0)
    customer_rating: Optional[ReviewRating] = Field(None)
    rider_efficiency_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Payment(BaseMongoDbDocumentSchema):
    order_id: PyObjectId = Field(..., description="Associated order")
    customer_id: PyObjectId = Field(..., description="Customer making payment")
    
    # Payment details
    payment_method: PaymentMethod = Field(...)
    amount: float = Field(..., gt=0, description="Payment amount")
    currency_code: str = Field(..., max_length=3, description="ISO currency code")
    
    # Transaction information
    transaction_id: str = Field(..., max_length=100, description="Payment gateway transaction ID")
    gateway_reference: Optional[str] = Field(None, max_length=100, description="Gateway-specific reference")
    external_transaction_id: Optional[str] = Field(None, max_length=100, description="External payment system ID")
    
    # Status and timing
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    
    # Payment method specifics
    card_last_four: Optional[str] = Field(None, max_length=4, description="Last 4 digits of card")
    wallet_type: Optional[str] = Field(None, max_length=50, description="Digital wallet provider")
    bank_reference: Optional[str] = Field(None, max_length=100, description="Bank transaction reference")
    
    # Fees and charges
    processing_fee: float = Field(default=0.0, ge=0, description="Payment processing fee")
    platform_fee: float = Field(default=0.0, ge=0, description="Platform service fee")
    
    # Refund information
    refund_amount: Optional[float] = Field(None, ge=0, description="Refunded amount if applicable")
    refund_reason: Optional[str] = Field(None, max_length=500)
    refunded_at: Optional[datetime] = Field(None)
    
    # Security and fraud
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="Fraud risk assessment")
    verification_status: str = Field(default="pending", max_length=20)
    
    # Reconciliation
    settled: bool = Field(default=False)
    settlement_date: Optional[datetime] = Field(None)
    settlement_amount: Optional[float] = Field(None, ge=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Review(BaseMongoDbDocumentSchema):
    # Review subject
    customer_id: PyObjectId = Field(..., description="Customer who wrote the review")
    restaurant_id: Optional[PyObjectId] = Field(None, description="Restaurant being reviewed")
    rider_id: Optional[PyObjectId] = Field(None, description="Rider being reviewed")
    order_id: PyObjectId = Field(..., description="Associated order")
    
    # Review content
    rating: ReviewRating = Field(..., description="Overall rating")
    food_rating: Optional[ReviewRating] = Field(None, description="Food quality rating")
    service_rating: Optional[ReviewRating] = Field(None, description="Service quality rating")
    delivery_rating: Optional[ReviewRating] = Field(None, description="Delivery experience rating")
    
    # Review text
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    comment: Optional[str] = Field(None, max_length=2000, description="Detailed review text")
    
    # Media attachments
    photos: List[str] = Field(default=[], description="Review photos")
    
    # Review metadata
    is_verified: bool = Field(default=True, description="Verified purchase review")
    is_anonymous: bool = Field(default=False, description="Anonymous review flag")
    language: str = Field(default="en", max_length=5, description="Review language")
    
    # Moderation
    is_approved: bool = Field(default=True)
    moderation_notes: Optional[str] = Field(None, max_length=500)
    flagged_content: List[str] = Field(default=[], description="Content moderation flags")
    
    # Engagement metrics
    helpful_votes: int = Field(default=0, ge=0, description="Number of helpful votes")
    total_votes: int = Field(default=0, ge=0, description="Total engagement votes")
    
    # Response from business
    business_response: Optional[str] = Field(None, max_length=1000, description="Restaurant's response")
    response_date: Optional[datetime] = Field(None)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Promotion(BaseMongoDbDocumentSchema):
    # Promotion identification
    code: str = Field(..., max_length=50, description="Promotion code")
    name: str = Field(..., max_length=200, description="Promotion display name")
    description: str = Field(..., max_length=1000, description="Promotion description")
    
    # Promotion type and value
    promotion_type: PromotionType = Field(...)
    discount_value: float = Field(..., ge=0, description="Discount amount or percentage")
    maximum_discount: Optional[float] = Field(None, ge=0, description="Maximum discount cap")
    minimum_order_value: float = Field(default=0.0, ge=0, description="Minimum order value to apply")
    
    # Validity period
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    
    # Usage limits
    total_usage_limit: Optional[int] = Field(None, ge=1, description="Total uses allowed")
    per_customer_limit: int = Field(default=1, ge=1, description="Uses per customer")
    current_usage_count: int = Field(default=0, ge=0)
    
    # Targeting
    applicable_cities: List[PyObjectId] = Field(default=[], description="Cities where promotion is valid")
    applicable_restaurants: List[PyObjectId] = Field(default=[], description="Specific restaurants")
    customer_segments: List[str] = Field(default=[], description="Target customer segments")
    new_customers_only: bool = Field(default=False)
    
    # Terms and conditions
    terms_conditions: str = Field(..., max_length=2000)
    
    # Status and settings
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False, description="Featured promotion flag")
    auto_apply: bool = Field(default=False, description="Automatically apply if eligible")
    
    # Performance tracking
    total_orders: int = Field(default=0, ge=0, description="Orders using this promotion")
    total_discount_given: float = Field(default=0.0, ge=0, description="Total discount amount given")
    conversion_rate: float = Field(default=0.0, ge=0, le=1, description="Usage to view ratio")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


# Collection schema definitions
class CityCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = City.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="city_code_unique",
            keys={"city_code": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="country_active",
            keys={
                "country": IndexDirection.ASCENDING,
                "is_active": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="coordinates_2dsphere",
            keys={"coordinates": "2dsphere"}
        )
    ]
    description: str = "Cities where food delivery service operates"


class CustomerCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Customer.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="email_unique",
            keys={"email": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="phone_unique",
            keys={"phone": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="city_active_customers",
            keys={
                "primary_city_id": IndexDirection.ASCENDING,
                "is_active": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="loyalty_tier_spending",
            keys={
                "loyalty_tier": IndexDirection.ASCENDING,
                "total_spent": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="last_order_analysis",
            keys={"last_order_date": IndexDirection.DESCENDING},
            sparse=True
        )
    ]
    description: str = "Customer profiles and preferences"


class RestaurantCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Restaurant.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="city_status_restaurants",
            keys={
                "city_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="coordinates_2dsphere",
            keys={"coordinates": "2dsphere"}
        ),
        IndexDefinition(
            name="cuisine_rating",
            keys={
                "cuisine_type": IndexDirection.ASCENDING,
                "average_rating": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="featured_promoted",
            keys={
                "featured": IndexDirection.DESCENDING,
                "promoted": IndexDirection.DESCENDING,
                "average_rating": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="performance_metrics",
            keys={
                "order_acceptance_rate": IndexDirection.DESCENDING,
                "on_time_delivery_rate": IndexDirection.DESCENDING
            }
        )
    ]
    description: str = "Restaurant partners and their operational data"


class MenuItemCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = MenuItem.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="restaurant_category_items",
            keys={
                "restaurant_id": IndexDirection.ASCENDING,
                "category": IndexDirection.ASCENDING,
                "is_available": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="popular_items",
            keys={
                "popularity_score": IndexDirection.DESCENDING,
                "is_available": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="featured_bestseller",
            keys={
                "is_featured": IndexDirection.DESCENDING,
                "is_bestseller": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="price_range",
            keys={
                "base_price": IndexDirection.ASCENDING,
                "is_available": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="dietary_filters",
            keys={
                "is_vegetarian": IndexDirection.DESCENDING,
                "is_vegan": IndexDirection.DESCENDING,
                "is_gluten_free": IndexDirection.DESCENDING
            }
        )
    ]
    description: str = "Restaurant menu items with pricing and availability"


class RiderCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Rider.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="employee_id_unique",
            keys={"employee_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="city_status_riders",
            keys={
                "city_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="current_location_2dsphere",
            keys={"current_location": "2dsphere"},
            sparse=True
        ),
        IndexDefinition(
            name="availability_capacity",
            keys={
                "status": IndexDirection.ASCENDING,
                "current_order_count": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="performance_rating",
            keys={
                "average_rating": IndexDirection.DESCENDING,
                "total_deliveries": IndexDirection.DESCENDING
            }
        )
    ]
    description: str = "Delivery riders and their availability status"


class OrderCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Order.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="order_number_unique",
            keys={"order_number": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="customer_orders_timeline",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "order_date": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="restaurant_orders_timeline",
            keys={
                "restaurant_id": IndexDirection.ASCENDING,
                "order_date": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="rider_assignments",
            keys={
                "rider_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            },
            sparse=True
        ),
        IndexDefinition(
            name="status_processing",
            keys={
                "status": IndexDirection.ASCENDING,
                "order_date": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="payment_status_tracking",
            keys={
                "payment_status": IndexDirection.ASCENDING,
                "order_date": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="delivery_coordinates_2dsphere",
            keys={"delivery_coordinates": "2dsphere"}
        )
    ]
    description: str = "Customer orders with items and delivery information"


class DeliveryCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Delivery.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="order_delivery_unique",
            keys={"order_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="rider_active_deliveries",
            keys={
                "rider_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="pickup_coordinates_2dsphere",
            keys={"pickup_coordinates": "2dsphere"}
        ),
        IndexDefinition(
            name="delivery_coordinates_2dsphere",
            keys={"delivery_coordinates": "2dsphere"}
        ),
        IndexDefinition(
            name="estimated_delivery_timeline",
            keys={"estimated_delivery_time": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="current_rider_location_2dsphere",
            keys={"current_rider_location": "2dsphere"},
            sparse=True
        )
    ]
    description: str = "Delivery tracking and logistics information"


class PaymentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Payment.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="transaction_id_unique",
            keys={"transaction_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="order_payments",
            keys={"order_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="customer_payment_history",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "initiated_at": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="payment_status_processing",
            keys={
                "status": IndexDirection.ASCENDING,
                "initiated_at": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="settlement_tracking",
            keys={
                "settled": IndexDirection.ASCENDING,
                "settlement_date": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="payment_method_analysis",
            keys={
                "payment_method": IndexDirection.ASCENDING,
                "completed_at": IndexDirection.DESCENDING
            }
        )
    ]
    description: str = "Payment transactions and financial records"


class ReviewCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Review.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="restaurant_reviews",
            keys={
                "restaurant_id": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING
            },
            sparse=True
        ),
        IndexDefinition(
            name="rider_reviews",
            keys={
                "rider_id": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING
            },
            sparse=True
        ),
        IndexDefinition(
            name="customer_review_history",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="order_review_unique",
            keys={"order_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="rating_approved_reviews",
            keys={
                "rating": IndexDirection.DESCENDING,
                "is_approved": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="helpful_reviews",
            keys={
                "helpful_votes": IndexDirection.DESCENDING,
                "is_approved": IndexDirection.DESCENDING
            }
        )
    ]
    description: str = "Customer reviews and ratings"


class PromotionCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Promotion.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="promotion_code_unique",
            keys={"code": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="active_promotions",
            keys={
                "is_active": IndexDirection.ASCENDING,
                "start_date": IndexDirection.ASCENDING,
                "end_date": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="city_promotions",
            keys={"applicable_cities": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="restaurant_promotions",
            keys={"applicable_restaurants": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="featured_promotions",
            keys={
                "is_featured": IndexDirection.DESCENDING,
                "start_date": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="promotion_performance",
            keys={
                "conversion_rate": IndexDirection.DESCENDING,
                "total_orders": IndexDirection.DESCENDING
            }
        )
    ]
    description: str = "Promotional campaigns and discount codes"


# Complete database schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "cities": CityCollectionSchema(),
        "customers": CustomerCollectionSchema(),
        "restaurants": RestaurantCollectionSchema(),
        "menu_items": MenuItemCollectionSchema(),
        "riders": RiderCollectionSchema(),
        "orders": OrderCollectionSchema(),
        "deliveries": DeliveryCollectionSchema(),
        "payments": PaymentCollectionSchema(),
        "reviews": ReviewCollectionSchema(),
        "promotions": PromotionCollectionSchema()
    }
    database_name: str = "baemin_food_delivery"
    description: str = "BAEMIN food delivery platform with multi-city operations and real-time logistics"


# Export the database schema
database_schema = MongoDbDataSchema()