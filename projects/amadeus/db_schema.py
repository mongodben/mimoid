"""Database schema for Amadeus Flight Offers Search API Database"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, field_validator
from enum import Enum
from decimal import Decimal

# Import base types from mimoid package
from mimoid import (
    IndexDirection,
    IndexDefinition,
    BaseCollectionSchema,
    BaseMongoDbSchema,
    PyObjectId,
    BaseMongoDbDocumentSchema,
)


# Enums for constrained fields
class TravelClass(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"


class TravelerType(str, Enum):
    ADULT = "ADULT"
    CHILD = "CHILD"
    SENIOR = "SENIOR"
    YOUNG = "YOUNG"
    HELD_INFANT = "HELD_INFANT"
    SEATED_INFANT = "SEATED_INFANT"
    STUDENT = "STUDENT"


class FareOption(str, Enum):
    STANDARD = "STANDARD"
    INCLUSIVE_TOUR = "INCLUSIVE_TOUR"
    SPANISH_MELILLA_RESIDENT = "SPANISH_MELILLA_RESIDENT"
    SPANISH_CEUTA_RESIDENT = "SPANISH_CEUTA_RESIDENT"
    SPANISH_CANARY_RESIDENT = "SPANISH_CANARY_RESIDENT"
    SPANISH_BALEARIC_RESIDENT = "SPANISH_BALEARIC_RESIDENT"
    AIR_FRANCE_METROPOLITAN_DISCOUNT_PASS = "AIR_FRANCE_METROPOLITAN_DISCOUNT_PASS"
    AIR_FRANCE_DOM_DISCOUNT_PASS = "AIR_FRANCE_DOM_DISCOUNT_PASS"
    AIR_FRANCE_COMBINED_DISCOUNT_PASS = "AIR_FRANCE_COMBINED_DISCOUNT_PASS"
    AIR_FRANCE_FAMILY = "AIR_FRANCE_FAMILY"
    ADULT_WITH_COMPANION = "ADULT_WITH_COMPANION"
    COMPANION = "COMPANION"


class FeeType(str, Enum):
    TICKETING = "TICKETING"
    FORM_OF_PAYMENT = "FORM_OF_PAYMENT"
    SUPPLIER = "SUPPLIER"


class AdditionalServiceType(str, Enum):
    CHECKED_BAGS = "CHECKED_BAGS"
    MEALS = "MEALS"
    SEATS = "SEATS"
    OTHER_SERVICES = "OTHER_SERVICES"


class FlightOfferSource(str, Enum):
    GDS = "GDS"


class BookingStatus(str, Enum):
    SEARCHING = "searching"
    QUOTED = "quoted"
    BOOKED = "booked"
    TICKETED = "ticketed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SearchStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# Document schemas
class Airline(BaseMongoDbDocumentSchema):
    # Basic airline information
    iata_code: str = Field(..., max_length=2, description="IATA airline code")
    icao_code: Optional[str] = Field(None, max_length=3, description="ICAO airline code")
    name: str = Field(..., max_length=200, description="Airline name")
    country_code: str = Field(..., max_length=2, description="Country of registration")
    
    # Operational details
    is_active: bool = Field(default=True, description="Currently operating")
    blacklisted_in_eu: bool = Field(default=False, description="EU blacklist status")
    website: Optional[str] = Field(None, max_length=500)
    
    # Business information
    alliance: Optional[str] = Field(None, max_length=50, description="Airline alliance")
    hub_airports: List[str] = Field(default=[], description="Primary hub airport codes")
    fleet_size: Optional[int] = Field(None, ge=0, description="Total aircraft count")
    destinations_count: Optional[int] = Field(None, ge=0, description="Destinations served")
    
    # Service characteristics
    low_cost_carrier: bool = Field(default=False, description="LCC classification")
    full_service_carrier: bool = Field(default=True, description="FSC classification")
    regional_carrier: bool = Field(default=False, description="Regional airline")
    
    # Contact and booking information
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    booking_classes: List[str] = Field(default=[], description="Available booking classes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Aircraft(BaseMongoDbDocumentSchema):
    # Aircraft identification
    iata_code: str = Field(..., max_length=3, description="IATA aircraft type code")
    icao_code: Optional[str] = Field(None, max_length=4, description="ICAO aircraft type code")
    name: str = Field(..., max_length=200, description="Aircraft model name")
    manufacturer: str = Field(..., max_length=100, description="Aircraft manufacturer")
    
    # Technical specifications
    capacity_economy: Optional[int] = Field(None, ge=0, description="Economy class seats")
    capacity_business: Optional[int] = Field(None, ge=0, description="Business class seats")
    capacity_first: Optional[int] = Field(None, ge=0, description="First class seats")
    capacity_total: Optional[int] = Field(None, ge=0, description="Total passenger capacity")
    
    # Performance characteristics
    range_km: Optional[int] = Field(None, ge=0, description="Maximum range in kilometers")
    cruise_speed_kmh: Optional[int] = Field(None, ge=0, description="Cruise speed in km/h")
    service_ceiling_m: Optional[int] = Field(None, ge=0, description="Service ceiling in meters")
    
    # Operational details
    first_flight_year: Optional[int] = Field(None, ge=1900, le=2030, description="Year of first flight")
    in_production: bool = Field(default=True, description="Currently in production")
    typical_routes: List[str] = Field(default=[], description="Typical route types (short-haul, long-haul, etc.)")
    
    # Engine and fuel information
    engine_count: Optional[int] = Field(None, ge=1, le=6, description="Number of engines")
    engine_type: Optional[str] = Field(None, max_length=100, description="Engine type")
    fuel_consumption_lph: Optional[float] = Field(None, ge=0, description="Fuel consumption per hour")
    
    # Environmental data
    co2_emission_factor: Optional[float] = Field(None, ge=0, description="CO2 emission factor")
    noise_category: Optional[str] = Field(None, max_length=20, description="Noise classification")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Airport(BaseMongoDbDocumentSchema):
    # Airport identification
    iata_code: str = Field(..., max_length=3, description="IATA airport code")
    icao_code: Optional[str] = Field(None, max_length=4, description="ICAO airport code")
    name: str = Field(..., max_length=200, description="Airport name")
    
    # Location information
    city_code: str = Field(..., max_length=3, description="IATA city code")
    city_name: str = Field(..., max_length=100, description="City name")
    country_code: str = Field(..., max_length=2, description="ISO country code")
    country_name: str = Field(..., max_length=100, description="Country name")
    continent: str = Field(..., max_length=50, description="Continent name")
    
    # Geographic coordinates
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude in decimal degrees")
    elevation_m: Optional[int] = Field(None, description="Elevation in meters above sea level")
    timezone: Optional[str] = Field(None, max_length=50, description="IANA timezone identifier")
    
    # Operational information
    is_active: bool = Field(default=True, description="Currently operational")
    airport_type: str = Field(..., max_length=50, description="Airport classification")
    hub_for_airlines: List[str] = Field(default=[], description="Airlines using as hub")
    terminals_count: Optional[int] = Field(None, ge=1, description="Number of terminals")
    
    # Capacity and traffic
    runways_count: Optional[int] = Field(None, ge=1, description="Number of runways")
    annual_passengers: Optional[int] = Field(None, ge=0, description="Annual passenger count")
    cargo_tonnage: Optional[int] = Field(None, ge=0, description="Annual cargo tonnage")
    
    # Services and facilities
    customs_airport: bool = Field(default=True, description="Has customs facilities")
    duty_free_available: bool = Field(default=True, description="Has duty-free shopping")
    wifi_available: bool = Field(default=True, description="Has WiFi service")
    lounges_count: Optional[int] = Field(None, ge=0, description="Number of lounges")
    
    # Connectivity
    ground_transport: List[str] = Field(default=[], description="Available ground transport modes")
    nearby_airports: List[str] = Field(default=[], description="Nearby airport codes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Country(BaseMongoDbDocumentSchema):
    # Country identification
    iso_code: str = Field(..., max_length=2, description="ISO 3166-1 alpha-2 code")
    iso3_code: str = Field(..., max_length=3, description="ISO 3166-1 alpha-3 code")
    name: str = Field(..., max_length=100, description="Country name")
    official_name: Optional[str] = Field(None, max_length=200, description="Official country name")
    
    # Geographic information
    continent: str = Field(..., max_length=50, description="Continent name")
    region: str = Field(..., max_length=100, description="Geographic region")
    subregion: Optional[str] = Field(None, max_length=100, description="Geographic subregion")
    
    # Political and economic
    capital_city: Optional[str] = Field(None, max_length=100, description="Capital city")
    currency_code: Optional[str] = Field(None, max_length=3, description="Primary currency code")
    languages: List[str] = Field(default=[], description="Official languages")
    
    # Travel and aviation
    visa_required_countries: List[str] = Field(default=[], description="Countries requiring visa")
    visa_free_countries: List[str] = Field(default=[], description="Countries with visa-free travel")
    major_airports: List[str] = Field(default=[], description="Major airport codes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Currency(BaseMongoDbDocumentSchema):  
    # Currency identification
    code: str = Field(..., max_length=3, description="ISO 4217 currency code")
    name: str = Field(..., max_length=100, description="Currency name")
    symbol: str = Field(..., max_length=10, description="Currency symbol")
    
    # Formatting information
    decimal_places: int = Field(default=2, ge=0, le=4, description="Number of decimal places")
    decimal_separator: str = Field(default=".", max_length=1, description="Decimal separator")
    thousands_separator: str = Field(default=",", max_length=1, description="Thousands separator")
    
    # Exchange rate information (relative to USD)
    exchange_rate_to_usd: float = Field(..., gt=0, description="Exchange rate to USD")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last rate update")
    
    # Regional information
    countries: List[str] = Field(default=[], description="Countries using this currency")
    is_major_currency: bool = Field(default=False, description="Major trading currency")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class SearchRequest(BaseMongoDbDocumentSchema):
    # Search identification
    search_id: str = Field(..., max_length=50, description="Unique search identifier")
    session_id: Optional[str] = Field(None, max_length=100, description="User session identifier")
    user_id: Optional[str] = Field(None, max_length=50, description="User identifier")
    
    # Search criteria
    origin_code: str = Field(..., max_length=3, description="Origin airport/city code")
    destination_code: str = Field(..., max_length=3, description="Destination airport/city code")
    departure_date: datetime = Field(..., description="Departure date")
    return_date: Optional[datetime] = Field(None, description="Return date for round-trip")
    
    # Passenger information
    adults: int = Field(default=1, ge=1, le=9, description="Number of adult passengers")
    children: int = Field(default=0, ge=0, le=9, description="Number of child passengers")
    infants: int = Field(default=0, ge=0, le=9, description="Number of infant passengers")
    
    # Search preferences
    travel_class: Optional[TravelClass] = Field(None, description="Preferred travel class")
    non_stop: bool = Field(default=False, description="Non-stop flights only")
    max_price: Optional[int] = Field(None, ge=1, description="Maximum price per traveler")
    currency_code: str = Field(default="USD", max_length=3, description="Preferred currency")
    
    # Airline preferences
    included_airlines: List[str] = Field(default=[], description="Preferred airline codes")
    excluded_airlines: List[str] = Field(default=[], description="Excluded airline codes")
    
    # Search metadata
    search_timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(None, max_length=45, description="Client IP address")
    user_agent: Optional[str] = Field(None, max_length=500, description="Client user agent")
    
    # Results information
    results_count: int = Field(default=0, ge=0, description="Number of results returned")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")
    status: SearchStatus = Field(default=SearchStatus.ACTIVE)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class FlightOffer(BaseMongoDbDocumentSchema):
    # Offer identification
    offer_id: str = Field(..., max_length=50, description="Flight offer identifier")
    search_request_id: Optional[PyObjectId] = Field(None, description="Associated search request")
    source: FlightOfferSource = Field(default=FlightOfferSource.GDS)
    
    # Booking characteristics
    instant_ticketing_required: bool = Field(default=False)
    one_way: bool = Field(default=False, description="One-way or round-trip")
    non_homogeneous: bool = Field(default=False, description="Multiple PNRs required")
    number_of_bookable_seats: int = Field(default=9, ge=1, le=9)
    
    # Timing constraints
    last_ticketing_date: Optional[datetime] = Field(None, description="Ticketing deadline")
    booking_deadline: Optional[datetime] = Field(None, description="Booking deadline")
    
    # Itinerary information
    itineraries: List[Dict[str, Any]] = Field(..., description="Flight itineraries")
    total_duration: Optional[str] = Field(None, description="Total journey duration (ISO 8601)")
    
    # Pricing information
    price: Dict[str, Any] = Field(..., description="Complete pricing breakdown")
    currency_code: str = Field(..., max_length=3, description="Price currency")
    total_price: float = Field(..., ge=0, description="Total price for all travelers")
    base_price: float = Field(..., ge=0, description="Base fare excluding taxes")
    taxes_and_fees: float = Field(default=0.0, ge=0, description="Total taxes and fees")
    
    # Traveler pricing
    traveler_pricings: List[Dict[str, Any]] = Field(..., description="Per-traveler pricing details")
    
    # Airline information
    validating_airline_codes: List[str] = Field(..., description="Validating airlines")
    operating_airlines: List[str] = Field(default=[], description="Operating airlines")
    marketing_airlines: List[str] = Field(default=[], description="Marketing airlines")
    
    # Fare details
    fare_type: List[str] = Field(default=["PUBLISHED"], description="Fare type classification")
    fare_family: Optional[str] = Field(None, max_length=100, description="Branded fare family")
    refundable: Optional[bool] = Field(None, description="Refundable fare")
    exchangeable: Optional[bool] = Field(None, description="Exchangeable fare")
    
    # Service inclusions
    included_checked_bags_only: bool = Field(default=False)
    additional_services: List[Dict[str, Any]] = Field(default=[], description="Available add-ons")
    
    # Booking constraints
    advance_purchase_required: Optional[int] = Field(None, description="Advance purchase days")
    minimum_stay_required: Optional[int] = Field(None, description="Minimum stay days")
    maximum_stay_allowed: Optional[int] = Field(None, description="Maximum stay days")
    
    # Availability and booking
    availability_source: str = Field(default="GDS", max_length=50)
    booking_class_availability: Dict[str, int] = Field(default={}, description="Available seats by class")
    
    # Performance metrics
    search_score: Optional[float] = Field(None, ge=0, le=100, description="Relevance score")
    popularity_score: Optional[float] = Field(None, ge=0, le=100, description="Popularity ranking")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    expires_at: Optional[datetime] = Field(None, description="Offer expiration time")


class Booking(BaseMongoDbDocumentSchema):
    # Booking identification
    booking_reference: str = Field(..., max_length=20, description="PNR or booking reference")
    confirmation_number: str = Field(..., max_length=20, description="Confirmation number")
    flight_offer_id: PyObjectId = Field(..., description="Associated flight offer")
    search_request_id: Optional[PyObjectId] = Field(None, description="Original search request")
    
    # Customer information
    customer_id: Optional[str] = Field(None, max_length=50, description="Customer identifier")
    contact_email: str = Field(..., max_length=255, description="Contact email")
    contact_phone: str = Field(..., max_length=50, description="Contact phone")
    
    # Traveler manifest
    travelers: List[Dict[str, Any]] = Field(..., description="Traveler details")
    lead_traveler: Dict[str, Any] = Field(..., description="Primary traveler information")
    
    # Booking status and timeline
    status: BookingStatus = Field(default=BookingStatus.BOOKED)
    booking_date: datetime = Field(default_factory=datetime.utcnow)
    ticketing_deadline: Optional[datetime] = Field(None, description="Ticketing deadline")
    departure_date: datetime = Field(..., description="First departure date")
    
    # Payment information
    total_amount_paid: float = Field(..., ge=0, description="Total amount paid")
    payment_currency: str = Field(..., max_length=3, description="Payment currency")
    payment_method: str = Field(..., max_length=50, description="Payment method")
    payment_status: str = Field(default="pending", max_length=50)
    
    # Ticketing information
    ticket_numbers: List[str] = Field(default=[], description="Issued ticket numbers")
    ticketing_date: Optional[datetime] = Field(None, description="Ticketing completion date")
    validating_carrier: str = Field(..., max_length=2, description="Validating airline")
    
    # Special services and requests
    special_service_requests: List[Dict[str, Any]] = Field(default=[], description="SSRs")
    meal_preferences: List[str] = Field(default=[], description="Meal requests")
    seat_preferences: List[str] = Field(default=[], description="Seat assignments")
    
    # Modifications and changes
    modification_history: List[Dict[str, Any]] = Field(default=[], description="Change history")
    cancellation_date: Optional[datetime] = Field(None, description="Cancellation date")
    refund_amount: Optional[float] = Field(None, ge=0, description="Refund amount")
    
    # Agency and booking source
    booking_source: str = Field(default="API", max_length=100, description="Booking channel")
    agency_code: Optional[str] = Field(None, max_length=20, description="Travel agency code")
    agent_id: Optional[str] = Field(None, max_length=50, description="Booking agent")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


# Collection schema definitions
class AirlineCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Airline.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="iata_code_unique",
            keys={"iata_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="name_text_search",
            keys={"name": "text"},
        ),
        IndexDefinition(
            name="country_active",
            keys={"country_code": IndexDirection.ASCENDING, "is_active": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="alliance_carriers",
            keys={"alliance": IndexDirection.ASCENDING, "is_active": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="carrier_type",
            keys={"low_cost_carrier": IndexDirection.ASCENDING, "is_active": IndexDirection.ASCENDING},
        ),
    ]
    description: str = "Airlines and carriers with operational details"


class AircraftCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Aircraft.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="iata_code_unique",
            keys={"iata_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="manufacturer_model",
            keys={"manufacturer": IndexDirection.ASCENDING, "name": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="capacity_range",
            keys={"capacity_total": IndexDirection.ASCENDING, "range_km": IndexDirection.DESCENDING},
        ),
        IndexDefinition(
            name="production_status",
            keys={"in_production": IndexDirection.ASCENDING, "first_flight_year": IndexDirection.DESCENDING},
        ),
    ]
    description: str = "Aircraft types and specifications"


class AirportCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Airport.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="iata_code_unique",
            keys={"iata_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="city_country",
            keys={"city_code": IndexDirection.ASCENDING, "country_code": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="location_2dsphere",
            keys={"latitude": IndexDirection.ASCENDING, "longitude": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="hub_airlines",
            keys={"hub_for_airlines": IndexDirection.ASCENDING, "is_active": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="passenger_volume",
            keys={"annual_passengers": IndexDirection.DESCENDING, "is_active": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="name_text_search",
            keys={"name": "text", "city_name": "text"},
        ),
    ]
    description: str = "Airports and location information"


class CountryCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Country.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="iso_code_unique",
            keys={"iso_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="continent_region",
            keys={"continent": IndexDirection.ASCENDING, "region": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="name_text_search",
            keys={"name": "text", "official_name": "text"},
        ),
    ]
    description: str = "Countries and geographic reference data"


class CurrencyCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Currency.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="code_unique",
            keys={"code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="exchange_rate_updated",
            keys={"last_updated": IndexDirection.DESCENDING, "is_major_currency": IndexDirection.DESCENDING},
        ),
    ]
    description: str = "Currencies and exchange rate information"


class SearchRequestCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = SearchRequest.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="search_id_unique",
            keys={"search_id": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="route_date_search",
            keys={
                "origin_code": IndexDirection.ASCENDING,
                "destination_code": IndexDirection.ASCENDING,
                "departure_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="user_session_tracking",
            keys={"user_id": IndexDirection.ASCENDING, "search_timestamp": IndexDirection.DESCENDING},
            sparse=True,
        ),
        IndexDefinition(
            name="search_performance",
            keys={"response_time_ms": IndexDirection.ASCENDING, "results_count": IndexDirection.DESCENDING},
        ),
        IndexDefinition(
            name="popular_routes",
            keys={"origin_code": IndexDirection.ASCENDING, "destination_code": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="search_timeline",
            keys={"search_timestamp": IndexDirection.DESCENDING, "status": IndexDirection.ASCENDING},
        ),
    ]
    description: str = "Flight search requests and patterns"


class FlightOfferCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = FlightOffer.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="offer_id_unique",
            keys={"offer_id": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="search_results",
            keys={"search_request_id": IndexDirection.ASCENDING, "total_price": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="price_currency",
            keys={"currency_code": IndexDirection.ASCENDING, "total_price": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="airlines_offers",
            keys={"validating_airline_codes": IndexDirection.ASCENDING, "total_price": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="booking_deadline",
            keys={"last_ticketing_date": IndexDirection.ASCENDING, "expires_at": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="offer_scoring",
            keys={"search_score": IndexDirection.DESCENDING, "popularity_score": IndexDirection.DESCENDING},
        ),
        IndexDefinition(
            name="fare_characteristics",
            keys={"refundable": IndexDirection.ASCENDING, "exchangeable": IndexDirection.ASCENDING},
            sparse=True,
        ),
    ]
    description: str = "Flight offers with pricing and availability"


class BookingCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Booking.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="booking_reference_unique",
            keys={"booking_reference": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="confirmation_unique",
            keys={"confirmation_number": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="customer_bookings",
            keys={"customer_id": IndexDirection.ASCENDING, "booking_date": IndexDirection.DESCENDING},
            sparse=True,
        ),
        IndexDefinition(
            name="departure_timeline",
            keys={"departure_date": IndexDirection.ASCENDING, "status": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="ticketing_deadline",
            keys={"ticketing_deadline": IndexDirection.ASCENDING, "status": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="payment_tracking",
            keys={"payment_status": IndexDirection.ASCENDING, "total_amount_paid": IndexDirection.DESCENDING},
        ),
        IndexDefinition(
            name="airline_bookings",
            keys={"validating_carrier": IndexDirection.ASCENDING, "booking_date": IndexDirection.DESCENDING},
        ),
    ]
    description: str = "Flight bookings and reservation records"


# Complete database schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "airlines": AirlineCollectionSchema(),
        "aircraft": AircraftCollectionSchema(),
        "airports": AirportCollectionSchema(),
        "countries": CountryCollectionSchema(),
        "currencies": CurrencyCollectionSchema(),
        "search_requests": SearchRequestCollectionSchema(),
        "flight_offers": FlightOfferCollectionSchema(),
        "bookings": BookingCollectionSchema(),
    }
    database_name: str = "amadeus_flight_booking"
    description: str = "Amadeus Flight Offers Search API database with comprehensive flight booking and search capabilities"


# Export the database schema
database_schema = MongoDbDataSchema()