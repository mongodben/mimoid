"""Database seeder for Amadeus Flight Booking Database"""

import os
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from faker import Faker
import uuid

# Import the database schema
from db_schema import (
    database_schema,
    Airline, Aircraft, Airport, Country, Currency,
    SearchRequest, FlightOffer, Booking,
    TravelClass, TravelerType, FareOption, BookingStatus, SearchStatus,
    FlightOfferSource
)

# Import base seeder class
from mimoid import DatabaseSeeder


class AmadeusFlightSeeder(DatabaseSeeder):
    """Seeder for Amadeus Flight Booking Database with realistic aviation data"""

    def __init__(self, mongo_uri: str = None, database_name: str = None):
        connection_string = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        super().__init__(connection_string, database_schema)
        self.database_name = database_name or database_schema.database_name
        self.db_client = MongoClient(connection_string)
        self.db = self.db_client[self.database_name]
        self.fake = Faker(['en_US', 'en_GB', 'de_DE', 'fr_FR', 'es_ES', 'it_IT', 'pt_BR', 'ja_JP', 'zh_CN'])
        
        # Storage for generated IDs to maintain referential integrity
        self.airline_ids = []
        self.aircraft_ids = []
        self.airport_ids = []
        self.country_ids = []
        self.currency_ids = []
        self.search_request_ids = []
        self.flight_offer_ids = []
        
        # Real aviation data for realism
        self.real_airlines = [
            {"iata": "AA", "name": "American Airlines", "country": "US", "alliance": "oneworld", "lcc": False},
            {"iata": "DL", "name": "Delta Air Lines", "country": "US", "alliance": "SkyTeam", "lcc": False},
            {"iata": "UA", "name": "United Airlines", "country": "US", "alliance": "Star Alliance", "lcc": False},
            {"iata": "LH", "name": "Lufthansa", "country": "DE", "alliance": "Star Alliance", "lcc": False},
            {"iata": "BA", "name": "British Airways", "country": "GB", "alliance": "oneworld", "lcc": False},
            {"iata": "AF", "name": "Air France", "country": "FR", "alliance": "SkyTeam", "lcc": False},
            {"iata": "KL", "name": "KLM Royal Dutch Airlines", "country": "NL", "alliance": "SkyTeam", "lcc": False},
            {"iata": "EK", "name": "Emirates", "country": "AE", "alliance": None, "lcc": False},
            {"iata": "QR", "name": "Qatar Airways", "country": "QA", "alliance": "oneworld", "lcc": False},
            {"iata": "SQ", "name": "Singapore Airlines", "country": "SG", "alliance": "Star Alliance", "lcc": False},
            {"iata": "TK", "name": "Turkish Airlines", "country": "TR", "alliance": "Star Alliance", "lcc": False},
            {"iata": "FR", "name": "Ryanair", "country": "IE", "alliance": None, "lcc": True},
            {"iata": "U2", "name": "easyJet", "country": "GB", "alliance": None, "lcc": True},
            {"iata": "WN", "name": "Southwest Airlines", "country": "US", "alliance": None, "lcc": True},
            {"iata": "B6", "name": "JetBlue Airways", "country": "US", "alliance": None, "lcc": True},
            {"iata": "NK", "name": "Spirit Airlines", "country": "US", "alliance": None, "lcc": True},
        ]
        
        self.real_aircraft = [
            {"iata": "32A", "name": "Airbus A320", "manufacturer": "Airbus", "capacity": 180, "range": 6150},
            {"iata": "32B", "name": "Airbus A321", "manufacturer": "Airbus", "capacity": 220, "range": 7400},
            {"iata": "32S", "name": "Airbus A319", "manufacturer": "Airbus", "capacity": 156, "range": 6900},
            {"iata": "333", "name": "Airbus A330-300", "manufacturer": "Airbus", "capacity": 335, "range": 11750},
            {"iata": "343", "name": "Airbus A340-300", "manufacturer": "Airbus", "capacity": 295, "range": 13500},
            {"iata": "359", "name": "Airbus A350-900", "manufacturer": "Airbus", "capacity": 325, "range": 15000},
            {"iata": "380", "name": "Airbus A380-800", "manufacturer": "Airbus", "capacity": 525, "range": 15200},
            {"iata": "737", "name": "Boeing 737-800", "manufacturer": "Boeing", "capacity": 189, "range": 5765},
            {"iata": "73G", "name": "Boeing 737-700", "manufacturer": "Boeing", "capacity": 149, "range": 6230},
            {"iata": "73H", "name": "Boeing 737 MAX 8", "manufacturer": "Boeing", "capacity": 210, "range": 6570},
            {"iata": "738", "name": "Boeing 737-800", "manufacturer": "Boeing", "capacity": 162, "range": 5765},
            {"iata": "763", "name": "Boeing 767-300", "manufacturer": "Boeing", "capacity": 269, "range": 11065},
            {"iata": "772", "name": "Boeing 777-200", "manufacturer": "Boeing", "capacity": 314, "range": 14260},
            {"iata": "77W", "name": "Boeing 777-300ER", "manufacturer": "Boeing", "capacity": 396, "range": 14490},
            {"iata": "787", "name": "Boeing 787-8", "manufacturer": "Boeing", "capacity": 242, "range": 14800},
            {"iata": "789", "name": "Boeing 787-9", "manufacturer": "Boeing", "capacity": 290, "range": 15750},
        ]
        
        self.real_airports = [
            {"iata": "JFK", "name": "John F. Kennedy International Airport", "city": "NYC", "city_name": "New York", "country": "US", "lat": 40.6413, "lon": -73.7781},
            {"iata": "LAX", "name": "Los Angeles International Airport", "city": "LAX", "city_name": "Los Angeles", "country": "US", "lat": 33.9425, "lon": -118.4081},
            {"iata": "LHR", "name": "London Heathrow Airport", "city": "LON", "city_name": "London", "country": "GB", "lat": 51.4700, "lon": -0.4543},
            {"iata": "CDG", "name": "Charles de Gaulle Airport", "city": "PAR", "city_name": "Paris", "country": "FR", "lat": 49.0097, "lon": 2.5479},
            {"iata": "FRA", "name": "Frankfurt am Main Airport", "city": "FRA", "city_name": "Frankfurt", "country": "DE", "lat": 49.4264, "lon": 8.5706},
            {"iata": "AMS", "name": "Amsterdam Airport Schiphol", "city": "AMS", "city_name": "Amsterdam", "country": "NL", "lat": 52.3086, "lon": 4.7639},
            {"iata": "DXB", "name": "Dubai International Airport", "city": "DXB", "city_name": "Dubai", "country": "AE", "lat": 25.2532, "lon": 55.3657},
            {"iata": "SIN", "name": "Singapore Changi Airport", "city": "SIN", "city_name": "Singapore", "country": "SG", "lat": 1.3644, "lon": 103.9915},
            {"iata": "HND", "name": "Tokyo Haneda Airport", "city": "TYO", "city_name": "Tokyo", "country": "JP", "lat": 35.5494, "lon": 139.7798},
            {"iata": "ICN", "name": "Incheon International Airport", "city": "SEL", "city_name": "Seoul", "country": "KR", "lat": 37.4602, "lon": 126.4407},
            {"iata": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "SYD", "city_name": "Sydney", "country": "AU", "lat": -33.9399, "lon": 151.1753},
            {"iata": "BKK", "name": "Suvarnabhumi Airport", "city": "BKK", "city_name": "Bangkok", "country": "TH", "lat": 13.6900, "lon": 100.7501},
            {"iata": "PEK", "name": "Beijing Capital International Airport", "city": "BJS", "city_name": "Beijing", "country": "CN", "lat": 40.0799, "lon": 116.6031},
            {"iata": "GRU", "name": "São Paulo/Guarulhos International Airport", "city": "SAO", "city_name": "São Paulo", "country": "BR", "lat": -23.4356, "lon": -46.4731},
            {"iata": "YYZ", "name": "Toronto Pearson International Airport", "city": "YTO", "city_name": "Toronto", "country": "CA", "lat": 43.6777, "lon": -79.6248},
        ]
        
        self.countries_data = [
            {"iso": "US", "name": "United States", "continent": "North America", "currency": "USD"},
            {"iso": "GB", "name": "United Kingdom", "continent": "Europe", "currency": "GBP"},
            {"iso": "DE", "name": "Germany", "continent": "Europe", "currency": "EUR"},
            {"iso": "FR", "name": "France", "continent": "Europe", "currency": "EUR"},
            {"iso": "NL", "name": "Netherlands", "continent": "Europe", "currency": "EUR"},
            {"iso": "AE", "name": "United Arab Emirates", "continent": "Asia", "currency": "AED"},
            {"iso": "SG", "name": "Singapore", "continent": "Asia", "currency": "SGD"},
            {"iso": "JP", "name": "Japan", "continent": "Asia", "currency": "JPY"},
            {"iso": "KR", "name": "South Korea", "continent": "Asia", "currency": "KRW"},
            {"iso": "AU", "name": "Australia", "continent": "Oceania", "currency": "AUD"},
            {"iso": "TH", "name": "Thailand", "continent": "Asia", "currency": "THB"},
            {"iso": "CN", "name": "China", "continent": "Asia", "currency": "CNY"},
            {"iso": "BR", "name": "Brazil", "continent": "South America", "currency": "BRL"},
            {"iso": "CA", "name": "Canada", "continent": "North America", "currency": "CAD"},
        ]
        
        self.currencies_data = [
            {"code": "USD", "name": "US Dollar", "symbol": "$", "rate": 1.0, "major": True},
            {"code": "EUR", "name": "Euro", "symbol": "€", "rate": 0.85, "major": True},
            {"code": "GBP", "name": "British Pound", "symbol": "£", "rate": 0.73, "major": True},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "rate": 110.0, "major": True},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "rate": 1.35, "major": False},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "rate": 1.25, "major": False},
            {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF", "rate": 0.92, "major": True},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "rate": 6.45, "major": False},
            {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$", "rate": 1.35, "major": False},
            {"code": "AED", "name": "UAE Dirham", "symbol": "AED", "rate": 3.67, "major": False},
        ]

    def create_database_schema(self):
        """Create the database schema with indexes"""
        print("Creating database schema with indexes...")
        
        # Drop database if it exists
        self.db_client.drop_database(self.database_name)
        
        # Get database reference
        db = self.db_client[self.database_name]
        
        # Create collections with indexes
        for collection_name, collection_schema in database_schema.collections.items():
            collection = db[collection_name]
            
            # Create indexes
            for index_def in collection_schema.indexes:
                try:
                    # Handle text indexes
                    if any(isinstance(direction, str) and direction == "text" for direction in index_def.keys.values()):
                        text_fields = [(field, "text") for field, direction in index_def.keys.items() if direction == "text"]
                        collection.create_index(
                            text_fields,
                            name=index_def.name,
                            background=index_def.background
                        )
                    else:
                        # Regular indexes
                        index_keys = [(field, direction.value if hasattr(direction, 'value') else direction) 
                                     for field, direction in index_def.keys.items()]
                        collection.create_index(
                            index_keys,
                            name=index_def.name,
                            unique=index_def.unique,
                            sparse=index_def.sparse,
                            background=index_def.background
                        )
                    print(f"  ✅ Created index '{index_def.name}' on collection '{collection_name}'")
                except Exception as e:
                    print(f"  ⚠️ Warning: Could not create index '{index_def.name}' on '{collection_name}': {e}")

    def seed_countries(self, count: int = 50) -> List[str]:
        """Seed countries collection"""
        print(f"🌍 Seeding {count} countries...")
        
        countries = []
        country_ids = []
        
        # Add real countries first
        for country_data in self.countries_data[:count]:
            country_id = self.get_object_id()
            country = Country(
                _id=country_id,
                iso_code=country_data["iso"],
                iso3_code=self.fake.country_code(representation="alpha-3"),
                name=country_data["name"],
                official_name=f"The {country_data['name']}" if random.choice([True, False]) else country_data["name"],
                continent=country_data["continent"],
                region=random.choice(["Northern", "Southern", "Eastern", "Western", "Central"]) + " " + country_data["continent"],
                capital_city=self.fake.city(),
                currency_code=country_data["currency"],
                languages=[self.fake.language_name() for _ in range(random.randint(1, 3))],
                major_airports=[airport["iata"] for airport in self.real_airports if airport["country"] == country_data["iso"]],
            )
            countries.append(country.model_dump())
            country_ids.append(country_id)
        
        # Add additional fake countries if needed
        used_iso_codes = set([c["iso"] for c in self.countries_data])
        for i in range(len(self.countries_data), count):
            country_id = self.get_object_id()
            
            # Generate unique ISO code
            fake_iso = self.fake.country_code()
            while fake_iso in used_iso_codes:
                fake_iso = self.fake.country_code()
            used_iso_codes.add(fake_iso)
            
            country = Country(
                _id=country_id,
                iso_code=fake_iso,
                iso3_code=self.fake.country_code(representation="alpha-3"),
                name=self.fake.country(),
                continent=random.choice(["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]),
                region=self.fake.word().title() + " Region",
                capital_city=self.fake.city(),
                currency_code=random.choice([c["code"] for c in self.currencies_data]),
                languages=[self.fake.language_name() for _ in range(random.randint(1, 2))],
            )
            countries.append(country.model_dump())
            country_ids.append(country_id)
        
        # Bulk insert
        self.db["countries"].insert_many(countries)
        self.country_ids = country_ids
        return country_ids

    def seed_currencies(self, count: int = 20) -> List[str]:
        """Seed currencies collection"""
        print(f"💱 Seeding {count} currencies...")
        
        currencies = []
        currency_ids = []
        
        # Add real currencies first
        for currency_data in self.currencies_data[:count]:
            currency_id = self.get_object_id()
            currency = Currency(
                _id=currency_id,
                code=currency_data["code"],
                name=currency_data["name"],
                symbol=currency_data["symbol"],
                decimal_places=0 if currency_data["code"] == "JPY" else 2,
                exchange_rate_to_usd=currency_data["rate"],
                countries=[c["iso"] for c in self.countries_data if c["currency"] == currency_data["code"]],
                is_major_currency=currency_data["major"],
            )
            currencies.append(currency.model_dump())
            currency_ids.append(currency_id)
        
        # Add additional fake currencies if needed
        for i in range(len(self.currencies_data), count):
            currency_id = self.get_object_id()
            currency = Currency(
                _id=currency_id,
                code=self.fake.currency_code(),
                name=f"{self.fake.country()} {random.choice(['Dollar', 'Pound', 'Franc', 'Peso', 'Real'])}",
                symbol=random.choice(["$", "€", "£", "¥", "₹", "₽", "₩"]),
                decimal_places=random.choice([0, 2]),
                exchange_rate_to_usd=round(random.uniform(0.1, 10.0), 4),
                is_major_currency=False,
            )
            currencies.append(currency.model_dump())
            currency_ids.append(currency_id)
        
        # Bulk insert
        self.db["currencies"].insert_many(currencies)
        self.currency_ids = currency_ids
        return currency_ids

    def seed_airlines(self, count: int = 100) -> List[str]:
        """Seed airlines collection"""
        print(f"✈️ Seeding {count} airlines...")
        
        airlines = []
        airline_ids = []
        
        # Add real airlines first
        for airline_data in self.real_airlines:
            airline_id = self.get_object_id()
            
            airline = Airline(
                _id=airline_id,
                iata_code=airline_data["iata"],
                icao_code=self.fake.lexify("???").upper(),
                name=airline_data["name"],
                country_code=airline_data["country"],
                is_active=True,
                alliance=airline_data["alliance"],
                hub_airports=[airport["iata"] for airport in self.real_airports if airport["country"] == airline_data["country"]][:3],
                fleet_size=random.randint(50, 800),
                destinations_count=random.randint(50, 300),
                low_cost_carrier=airline_data["lcc"],
                full_service_carrier=not airline_data["lcc"],
                website=f"https://www.{airline_data['iata'].lower()}.com",
                phone=self.fake.phone_number(),
                booking_classes=["Y", "B", "M", "H", "Q", "V", "W", "S", "T", "L", "A", "K", "U", "E", "N", "R", "G", "X", "O", "I", "F", "C", "J", "D", "Z", "P"],
            )
            airlines.append(airline.model_dump())
            airline_ids.append(airline_id)
        
        # Add additional fake airlines
        for i in range(len(self.real_airlines), count):
            airline_id = self.get_object_id()
            
            # Generate unique 2-letter IATA code
            iata_code = self.fake.lexify("??").upper()
            while any(a["iata_code"] == iata_code for a in airlines):
                iata_code = self.fake.lexify("??").upper()
            
            country_code = random.choice(self.countries_data)["iso"]
            is_lcc = random.choice([True, False])
            
            airline = Airline(
                _id=airline_id,
                iata_code=iata_code,
                icao_code=self.fake.lexify("???").upper(),
                name=f"{self.fake.company()} {random.choice(['Airlines', 'Airways', 'Air', 'Express', 'Connect'])}",
                country_code=country_code,
                is_active=random.choice([True, True, True, False]),  # 75% active
                alliance=random.choice([None, None, "Star Alliance", "oneworld", "SkyTeam"]),
                hub_airports=[airport["iata"] for airport in self.real_airports if airport["country"] == country_code][:2],
                fleet_size=random.randint(10, 300),
                destinations_count=random.randint(10, 150),
                low_cost_carrier=is_lcc,
                full_service_carrier=not is_lcc,
                regional_carrier=random.choice([True, False]),
                website=f"https://www.{iata_code.lower()}.com",
                phone=self.fake.phone_number(),
                booking_classes=random.sample(["Y", "B", "M", "H", "Q", "V", "W", "S", "T", "L", "A", "K", "U", "E", "N", "R", "G", "X", "O", "I", "F", "C", "J", "D", "Z", "P"], random.randint(8, 16)),
            )
            airlines.append(airline.model_dump())
            airline_ids.append(airline_id)
        
        # Bulk insert
        self.db["airlines"].insert_many(airlines)
        self.airline_ids = airline_ids
        return airline_ids

    def seed_aircraft(self, count: int = 50) -> List[str]:
        """Seed aircraft collection"""
        print(f"🛩️ Seeding {count} aircraft types...")
        
        aircraft = []
        aircraft_ids = []
        
        # Add real aircraft first
        for aircraft_data in self.real_aircraft[:count]:
            aircraft_id = self.get_object_id()
            
            capacity = aircraft_data["capacity"]
            business_seats = int(capacity * random.uniform(0.1, 0.25))
            first_seats = int(capacity * random.uniform(0.02, 0.08)) if capacity > 200 else 0
            economy_seats = capacity - business_seats - first_seats
            
            plane = Aircraft(
                _id=aircraft_id,
                iata_code=aircraft_data["iata"],
                icao_code=self.fake.lexify("????").upper(),
                name=aircraft_data["name"],
                manufacturer=aircraft_data["manufacturer"],
                capacity_economy=economy_seats,
                capacity_business=business_seats,
                capacity_first=first_seats,
                capacity_total=capacity,
                range_km=aircraft_data["range"],
                cruise_speed_kmh=random.randint(450, 950),
                service_ceiling_m=random.randint(10000, 13000),
                first_flight_year=random.randint(1990, 2020),
                in_production=random.choice([True, False]),
                typical_routes=["short-haul"] if aircraft_data["range"] < 4000 else ["long-haul"] if aircraft_data["range"] > 10000 else ["medium-haul"],
                engine_count=2 if "A380" not in aircraft_data["name"] else 4,
                engine_type=f"{random.choice(['CFM', 'IAE', 'RR', 'GE'])} {random.randint(1000, 9999)}",
                fuel_consumption_lph=random.randint(1500, 8000),
                co2_emission_factor=random.uniform(0.5, 1.2),
            )
            aircraft.append(plane.model_dump())
            aircraft_ids.append(aircraft_id)
        
        # Add additional fake aircraft if needed
        for i in range(len(self.real_aircraft), count):
            aircraft_id = self.get_object_id()
            
            capacity = random.randint(50, 600)
            business_seats = int(capacity * random.uniform(0.1, 0.25))
            first_seats = int(capacity * random.uniform(0.02, 0.08)) if capacity > 200 else 0
            economy_seats = capacity - business_seats - first_seats
            
            plane = Aircraft(
                _id=aircraft_id,
                iata_code=self.fake.lexify("???").upper(),
                icao_code=self.fake.lexify("????").upper(),
                name=f"{random.choice(['Airbus', 'Boeing', 'Embraer', 'Bombardier'])} {random.choice(['A', 'B', 'E', 'CRJ'])}{random.randint(100, 900)}",
                manufacturer=random.choice(["Airbus", "Boeing", "Embraer", "Bombardier", "ATR"]),
                capacity_economy=economy_seats,
                capacity_business=business_seats,
                capacity_first=first_seats,
                capacity_total=capacity,
                range_km=random.randint(1000, 16000),
                cruise_speed_kmh=random.randint(450, 950),
                first_flight_year=random.randint(1980, 2023),
                in_production=random.choice([True, False]),
                engine_count=random.choice([2, 4]),
                fuel_consumption_lph=random.randint(1000, 10000),
            )
            aircraft.append(plane.model_dump())
            aircraft_ids.append(aircraft_id)
        
        # Bulk insert
        self.db["aircraft"].insert_many(aircraft)
        self.aircraft_ids = aircraft_ids
        return aircraft_ids

    def seed_airports(self, count: int = 200) -> List[str]:
        """Seed airports collection"""
        print(f"🏢 Seeding {count} airports...")
        
        airports = []
        airport_ids = []
        
        # Add real airports first
        for airport_data in self.real_airports:
            airport_id = self.get_object_id()
            
            airport = Airport(
                _id=airport_id,
                iata_code=airport_data["iata"],
                icao_code=self.fake.lexify("????").upper(),
                name=airport_data["name"],
                city_code=airport_data["city"],
                city_name=airport_data["city_name"],
                country_code=airport_data["country"],
                country_name=next(c["name"] for c in self.countries_data if c["iso"] == airport_data["country"]),
                continent=next(c["continent"] for c in self.countries_data if c["iso"] == airport_data["country"]),
                latitude=airport_data["lat"],
                longitude=airport_data["lon"],
                elevation_m=random.randint(0, 4000),
                timezone=self.fake.timezone(),
                is_active=True,
                airport_type="International",
                hub_for_airlines=[airline["iata"] for airline in self.real_airlines if airline["country"] == airport_data["country"]][:3],
                terminals_count=random.randint(1, 8),
                runways_count=random.randint(1, 6),
                annual_passengers=random.randint(1000000, 100000000),
                cargo_tonnage=random.randint(100000, 5000000),
                customs_airport=True,
                duty_free_available=True,
                wifi_available=True,
                lounges_count=random.randint(5, 50),
                ground_transport=["Bus", "Train", "Taxi", "Car Rental", "Metro"],
            )
            airports.append(airport.model_dump())
            airport_ids.append(airport_id)
        
        # Add additional fake airports
        for i in range(len(self.real_airports), count):
            airport_id = self.get_object_id()
            
            # Generate unique 3-letter IATA code
            iata_code = self.fake.lexify("???").upper()
            while any(a["iata_code"] == iata_code for a in airports):
                iata_code = self.fake.lexify("???").upper()
            
            country_data = random.choice(self.countries_data)
            city_name = self.fake.city()
            
            airport = Airport(
                _id=airport_id,
                iata_code=iata_code,
                icao_code=self.fake.lexify("????").upper(),
                name=f"{city_name} {random.choice(['International Airport', 'Airport', 'Regional Airport', 'Municipal Airport'])}",
                city_code=iata_code,  # Simplified: use same code for city
                city_name=city_name,
                country_code=country_data["iso"],
                country_name=country_data["name"],
                continent=country_data["continent"],
                latitude=self.fake.latitude(),
                longitude=self.fake.longitude(),
                elevation_m=random.randint(0, 3000),
                timezone=self.fake.timezone(),
                is_active=random.choice([True, True, True, False]),  # 75% active
                airport_type=random.choice(["International", "Domestic", "Regional", "Military"]),
                terminals_count=random.randint(1, 4),
                runways_count=random.randint(1, 3),
                annual_passengers=random.randint(50000, 10000000),
                cargo_tonnage=random.randint(1000, 500000),
                customs_airport=random.choice([True, False]),
                duty_free_available=random.choice([True, False]),
                wifi_available=random.choice([True, False]),
                lounges_count=random.randint(0, 10),
                ground_transport=random.sample(["Bus", "Train", "Taxi", "Car Rental", "Metro", "Shuttle"], random.randint(2, 5)),
            )
            airports.append(airport.model_dump())
            airport_ids.append(airport_id)
        
        # Bulk insert
        self.db["airports"].insert_many(airports)
        self.airport_ids = airport_ids
        return airport_ids

    def seed_search_requests(self, count: int = 10000) -> List[str]:
        """Seed search requests collection"""
        print(f"🔍 Seeding {count} search requests...")
        
        search_requests = []
        search_request_ids = []
        
        # Get popular routes
        popular_routes = [
            ("JFK", "LHR"), ("LAX", "NRT"), ("SYD", "BKK"), ("CDG", "JFK"),
            ("LHR", "DXB"), ("FRA", "SIN"), ("AMS", "JFK"), ("DXB", "BKK"),
            ("SIN", "SYD"), ("ICN", "LAX"), ("GRU", "CDG"), ("YYZ", "LHR"),
        ]
        
        for i in range(count):
            search_id = f"SEARCH{datetime.utcnow().strftime('%Y%m%d')}{i+1:06d}"
            search_request_id = self.get_object_id()
            
            # 70% use popular routes, 30% random
            if random.random() < 0.7 and popular_routes:
                origin, destination = random.choice(popular_routes)
            else:
                origin = random.choice([a["iata"] for a in self.real_airports])
                destination = random.choice([a["iata"] for a in self.real_airports])
                while destination == origin:
                    destination = random.choice([a["iata"] for a in self.real_airports])
            
            # Random departure date in the next 365 days
            departure_date = datetime.utcnow() + timedelta(days=random.randint(1, 365))
            
            # Round trip probability
            return_date = None
            if random.random() < 0.6:  # 60% round trip
                return_date = departure_date + timedelta(days=random.randint(1, 30))
            
            search_request = SearchRequest(
                _id=search_request_id,
                search_id=search_id,
                session_id=str(uuid.uuid4()) if random.random() < 0.7 else None,
                user_id=f"USER{random.randint(1, 100000):06d}" if random.random() < 0.5 else None,
                origin_code=origin,
                destination_code=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=random.choices([1, 2, 3, 4], weights=[40, 35, 15, 10])[0],
                children=random.choices([0, 1, 2], weights=[70, 20, 10])[0],
                infants=random.choices([0, 1], weights=[85, 15])[0],
                travel_class=random.choice(list(TravelClass)) if random.random() < 0.3 else None,
                non_stop=random.choice([True, False]),
                max_price=random.randint(200, 5000) if random.random() < 0.2 else None,
                currency_code=random.choice(["USD", "EUR", "GBP", "JPY"]),
                search_timestamp=datetime.utcnow() - timedelta(minutes=random.randint(0, 43200)),  # Last 30 days
                ip_address=self.fake.ipv4(),
                user_agent=self.fake.user_agent(),
                results_count=random.randint(0, 250),
                response_time_ms=random.randint(200, 3000),
                status=random.choices(list(SearchStatus), weights=[10, 80, 5, 5])[0],
            )
            search_requests.append(search_request.model_dump())
            search_request_ids.append(search_request_id)
        
        # Bulk insert
        batch_size = 1000
        for i in range(0, len(search_requests), batch_size):
            batch = search_requests[i:i + batch_size]
            self.db["search_requests"].insert_many(batch)
        
        self.search_request_ids = search_request_ids
        return search_request_ids

    def seed_flight_offers(self, count: int = 50000) -> List[str]:
        """Seed flight offers collection with realistic pricing and routes"""
        print(f"💺 Seeding {count} flight offers...")
        
        flight_offers = []
        flight_offer_ids = []
        
        for i in range(count):
            offer_id = f"OFFER{datetime.utcnow().strftime('%Y%m%d')}{i+1:08d}"
            flight_offer_id = self.get_object_id()
            
            # Select random search request
            search_request_id = random.choice(self.search_request_ids) if self.search_request_ids else None
            
            # Select airlines and aircraft
            validating_airline = random.choice([a["iata"] for a in self.real_airlines])
            operating_airlines = [validating_airline]
            if random.random() < 0.3:  # 30% chance of codeshare
                operating_airlines.append(random.choice([a["iata"] for a in self.real_airlines]))
            
            # Generate realistic pricing
            currency_code = random.choice(["USD", "EUR", "GBP", "JPY"])
            
            # Base price varies by route distance and class
            base_price = random.uniform(200, 1500)
            if random.random() < 0.2:  # 20% premium cabin
                base_price *= random.uniform(2.5, 8.0)
            
            taxes_and_fees = base_price * random.uniform(0.15, 0.35)
            total_price = base_price + taxes_and_fees
            
            # Adjust for currency
            if currency_code == "EUR":
                total_price *= 0.85
            elif currency_code == "GBP":
                total_price *= 0.73
            elif currency_code == "JPY":
                total_price *= 110
            
            # Create realistic itinerary structure
            origin = random.choice([a["iata"] for a in self.real_airports])
            destination = random.choice([a["iata"] for a in self.real_airports])
            while destination == origin:
                destination = random.choice([a["iata"] for a in self.real_airports])
            
            departure_time = datetime.utcnow() + timedelta(days=random.randint(1, 365), hours=random.randint(0, 23), minutes=random.choice([0, 15, 30, 45]))
            arrival_time = departure_time + timedelta(hours=random.randint(2, 16), minutes=random.randint(0, 59))
            
            segments = [{
                "id": "1",
                "departure": {
                    "iataCode": origin,
                    "at": departure_time.isoformat(),
                    "terminal": str(random.randint(1, 5)) if random.random() < 0.8 else None
                },
                "arrival": {
                    "iataCode": destination,
                    "at": arrival_time.isoformat(),
                    "terminal": str(random.randint(1, 5)) if random.random() < 0.8 else None
                },
                "carrierCode": validating_airline,
                "number": str(random.randint(1, 9999)),
                "aircraft": {"code": random.choice([a["iata"] for a in self.real_aircraft])},
                "duration": f"PT{(arrival_time - departure_time).seconds // 3600}H{((arrival_time - departure_time).seconds % 3600) // 60}M",
                "numberOfStops": 0,
                "blacklistedInEU": False
            }]
            
            # Add connecting flight for some routes (30% chance)
            if random.random() < 0.3:
                connection_airport = random.choice([a["iata"] for a in self.real_airports])
                while connection_airport in [origin, destination]:
                    connection_airport = random.choice([a["iata"] for a in self.real_airports])
                
                # Update first segment
                segments[0]["arrival"]["iataCode"] = connection_airport
                segments[0]["arrival"]["at"] = (departure_time + timedelta(hours=random.randint(2, 8))).isoformat()
                segments[0]["numberOfStops"] = 1
                
                # Add second segment
                connection_departure = departure_time + timedelta(hours=random.randint(3, 10))
                final_arrival = connection_departure + timedelta(hours=random.randint(2, 8))
                
                segments.append({
                    "id": "2", 
                    "departure": {
                        "iataCode": connection_airport,
                        "at": connection_departure.isoformat(),
                        "terminal": str(random.randint(1, 5)) if random.random() < 0.8 else None
                    },
                    "arrival": {
                        "iataCode": destination,
                        "at": final_arrival.isoformat(),
                        "terminal": str(random.randint(1, 5)) if random.random() < 0.8 else None
                    },
                    "carrierCode": validating_airline,
                    "number": str(random.randint(1, 9999)),
                    "aircraft": {"code": random.choice([a["iata"] for a in self.real_aircraft])},
                    "duration": f"PT{(final_arrival - connection_departure).seconds // 3600}H{((final_arrival - connection_departure).seconds % 3600) // 60}M",
                    "numberOfStops": 0,
                    "blacklistedInEU": False
                })
            
            itinerary = {
                "duration": f"PT{random.randint(2, 24)}H{random.randint(0, 59)}M",
                "segments": segments
            }
            
            # Traveler pricing
            travel_class = random.choice(list(TravelClass))
            traveler_pricings = [{
                "travelerId": "1",
                "fareOption": random.choice(list(FareOption)),
                "travelerType": TravelerType.ADULT,
                "price": {
                    "currency": currency_code,
                    "total": f"{total_price:.2f}",
                    "base": f"{base_price:.2f}"
                },
                "fareDetailsBySegment": [{
                    "segmentId": seg["id"],
                    "cabin": travel_class,
                    "fareBasis": f"{random.choice(['Y', 'B', 'M', 'H', 'Q', 'V', 'W', 'S'])}{random.randint(1, 9)}{validating_airline}{random.randint(10, 99)}",
                    "class": random.choice(["Y", "B", "M", "H", "Q", "V", "W", "S", "T", "L", "A", "K", "U", "E", "N", "R", "G", "X", "O", "I", "F", "C", "J", "D", "Z", "P"]),
                    "includedCheckedBags": {
                        "quantity": random.randint(0, 2),
                        "weight": random.choice([20, 23, 32]),
                        "weightUnit": "KG"
                    }
                } for seg in segments]
            }]
            
            flight_offer = FlightOffer(
                _id=flight_offer_id,
                offer_id=offer_id,
                search_request_id=search_request_id,
                source=FlightOfferSource.GDS,
                instant_ticketing_required=random.choice([True, False]),
                one_way=random.choice([True, False]),
                non_homogeneous=False,
                number_of_bookable_seats=random.randint(1, 9),
                last_ticketing_date=departure_time - timedelta(days=random.randint(1, 7)),
                itineraries=[itinerary],
                total_duration=itinerary["duration"],
                price={
                    "currency": currency_code,
                    "total": f"{total_price:.2f}",
                    "base": f"{base_price:.2f}",
                    "fees": [
                        {"amount": f"{taxes_and_fees * 0.7:.2f}", "type": "SUPPLIER"},
                        {"amount": f"{taxes_and_fees * 0.3:.2f}", "type": "TICKETING"}
                    ],
                    "grandTotal": f"{total_price:.2f}"
                },
                currency_code=currency_code,
                total_price=total_price,
                base_price=base_price,
                taxes_and_fees=taxes_and_fees,
                traveler_pricings=traveler_pricings,
                validating_airline_codes=[validating_airline],
                operating_airlines=operating_airlines,
                marketing_airlines=[validating_airline],
                fare_type=["PUBLISHED"],
                refundable=random.choice([True, False, None]),
                exchangeable=random.choice([True, False, None]),
                included_checked_bags_only=random.choice([True, False]),
                search_score=random.uniform(70, 100),
                popularity_score=random.uniform(50, 95),
                expires_at=datetime.utcnow() + timedelta(hours=random.randint(1, 24))
            )
            
            flight_offers.append(flight_offer.model_dump())
            flight_offer_ids.append(flight_offer_id)
        
        # Bulk insert
        batch_size = 1000
        for i in range(0, len(flight_offers), batch_size):
            batch = flight_offers[i:i + batch_size]
            self.db["flight_offers"].insert_many(batch)
            
        self.flight_offer_ids = flight_offer_ids
        return flight_offer_ids

    def seed_bookings(self, count: int = 5000) -> List[str]:
        """Seed bookings collection with realistic booking data"""
        print(f"📋 Seeding {count} bookings...")
        
        bookings = []
        booking_ids = []
        
        for i in range(count):
            booking_id = self.get_object_id()
            
            # Generate booking reference (PNR format)
            booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            confirmation_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Select associated flight offer
            flight_offer_id = random.choice(self.flight_offer_ids) if self.flight_offer_ids else self.get_object_id()
            search_request_id = random.choice(self.search_request_ids) if self.search_request_ids and random.random() < 0.7 else None
            
            # Booking timeline
            booking_date = datetime.utcnow() - timedelta(days=random.randint(0, 90))
            departure_date = booking_date + timedelta(days=random.randint(1, 365))
            ticketing_deadline = booking_date + timedelta(days=random.randint(1, 3))
            
            # Payment and pricing
            currency = random.choice(["USD", "EUR", "GBP", "JPY"])
            total_amount = random.uniform(300, 3000)
            if currency == "EUR":
                total_amount *= 0.85
            elif currency == "GBP":
                total_amount *= 0.73
            elif currency == "JPY":
                total_amount *= 110
            
            # Traveler information
            num_travelers = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
            travelers = []
            for t in range(num_travelers):
                traveler = {
                    "id": str(t + 1),
                    "type": random.choice(list(TravelerType)),
                    "name": {
                        "firstName": self.fake.first_name(),
                        "lastName": self.fake.last_name()
                    },
                    "dateOfBirth": self.fake.date_of_birth(minimum_age=2, maximum_age=80).isoformat(),
                    "gender": random.choice(["MALE", "FEMALE"]),
                    "contact": {
                        "emailAddress": self.fake.email(),
                        "phone": self.fake.phone_number()
                    } if t == 0 else None  # Only lead traveler has contact
                }
                travelers.append(traveler)
            
            lead_traveler = travelers[0].copy()
            lead_traveler["contact"] = {
                "emailAddress": self.fake.email(),
                "phone": self.fake.phone_number()
            }
            
            # Booking status progression
            status_weights = {"booked": 60, "ticketed": 30, "cancelled": 8, "refunded": 2}
            status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
            
            # Special services
            special_services = []
            if random.random() < 0.3:  # 30% have special requests
                special_services = random.sample([
                    {"type": "MEAL", "description": "Vegetarian meal"},
                    {"type": "SEAT", "description": "Window seat preference"},
                    {"type": "ASSISTANCE", "description": "Wheelchair assistance"},
                    {"type": "BAGGAGE", "description": "Extra baggage"},
                ], random.randint(1, 2))
            
            booking = Booking(
                _id=booking_id,
                booking_reference=booking_reference,
                confirmation_number=confirmation_number,
                flight_offer_id=flight_offer_id,
                search_request_id=search_request_id,
                customer_id=f"CUST{random.randint(1, 50000):06d}" if random.random() < 0.6 else None,
                contact_email=lead_traveler["contact"]["emailAddress"],
                contact_phone=lead_traveler["contact"]["phone"],
                travelers=travelers,
                lead_traveler=lead_traveler,
                status=BookingStatus(status),
                booking_date=booking_date,
                ticketing_deadline=ticketing_deadline,
                departure_date=departure_date,
                total_amount_paid=total_amount,
                payment_currency=currency,
                payment_method=random.choice(["Credit Card", "Debit Card", "PayPal", "Bank Transfer", "Miles"]),
                payment_status=random.choice(["completed", "pending", "failed"]) if status == "booked" else "completed",
                ticket_numbers=[f"{random.randint(100000000000, 999999999999)}" for _ in travelers] if status in ["ticketed", "refunded"] else [],
                ticketing_date=booking_date + timedelta(hours=random.randint(1, 72)) if status in ["ticketed", "refunded"] else None,
                validating_carrier=random.choice([a["iata"] for a in self.real_airlines]),
                special_service_requests=special_services,
                meal_preferences=[random.choice(["VGML", "HNML", "KOSHER", "MOML"]) for _ in travelers] if random.random() < 0.2 else [],
                booking_source=random.choice(["API", "Website", "Mobile App", "Call Center", "Travel Agent"]),
                agency_code=f"AG{random.randint(100000, 999999)}" if random.random() < 0.3 else None,
                cancellation_date=booking_date + timedelta(days=random.randint(1, 30)) if status in ["cancelled", "refunded"] else None,
                refund_amount=total_amount * random.uniform(0.5, 1.0) if status == "refunded" else None,
            )
            
            bookings.append(booking.model_dump())
            booking_ids.append(booking_id)
        
        # Bulk insert
        batch_size = 1000
        for i in range(0, len(bookings), batch_size):
            batch = bookings[i:i + batch_size]
            self.db["bookings"].insert_many(batch)
        
        return booking_ids

    # Implement abstract methods from DatabaseSeeder
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Seed all collections with sample data"""
        if num_records is None:
            num_records = {
                "countries": 50,
                "currencies": 20,
                "airlines": 100,
                "aircraft": 50,
                "airports": 200,
                "search_requests": 10000,
                "flight_offers": 50000,
                "bookings": 5000
            }
        
        results = {}
        
        # Seed reference data first
        results["countries"] = len(self.seed_countries(num_records.get("countries", 50)))
        results["currencies"] = len(self.seed_currencies(num_records.get("currencies", 20)))
        results["airlines"] = len(self.seed_airlines(num_records.get("airlines", 100)))
        results["aircraft"] = len(self.seed_aircraft(num_records.get("aircraft", 50)))
        results["airports"] = len(self.seed_airports(num_records.get("airports", 200)))
        
        # Seed transaction data
        results["search_requests"] = len(self.seed_search_requests(num_records.get("search_requests", 10000)))
        results["flight_offers"] = len(self.seed_flight_offers(num_records.get("flight_offers", 50000)))
        results["bookings"] = len(self.seed_bookings(num_records.get("bookings", 5000)))
        
        return results

    def create_indexes(self):
        """Create indexes as defined in the schema"""
        self.create_database_schema()

    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        self.drop_database()

    def validate_seed_data(self) -> Dict[str, Any]:
        """Validate the seeded data meets quality standards"""
        validation_results = {}
        
        # Check collection counts
        for collection_name in database_schema.collections.keys():
            count = self.db[collection_name].count_documents({})
            validation_results[f"{collection_name}_count"] = count
        
        # Basic validation checks
        validation_results.update(self.validate_references())
        validation_results.update(self.validate_aviation_data_patterns())
        
        return validation_results

    # Helper methods for testing and validation
    def get_object_id(self):
        """Generate a new ObjectId"""
        from bson import ObjectId
        return ObjectId()

    def test_connection(self):
        """Test database connection"""
        self.db_client.admin.command('ping')

    def drop_database(self):
        """Drop the entire database"""
        self.db_client.drop_database(self.database_name)

    def get_collection_stats(self) -> Dict[str, int]:
        """Get document counts for all collections"""
        stats = {}
        for collection_name in database_schema.collections.keys():
            stats[collection_name] = self.db[collection_name].count_documents({})
        return stats

    def validate_references(self) -> Dict[str, Dict[str, Any]]:
        """Validate referential integrity"""
        results = {}
        
        # Check flight offers reference valid search requests
        valid_search_refs = self.db.flight_offers.count_documents({
            "search_request_id": {"$in": self.search_request_ids}
        }) if self.search_request_ids else 0
        total_offers_with_refs = self.db.flight_offers.count_documents({
            "search_request_id": {"$ne": None}
        })
        
        results["flight_offer_search_refs"] = {
            "valid": valid_search_refs == total_offers_with_refs,
            "message": f"{valid_search_refs}/{total_offers_with_refs} flight offers have valid search references"
        }
        
        # Check bookings reference valid flight offers
        valid_offer_refs = self.db.bookings.count_documents({
            "flight_offer_id": {"$in": self.flight_offer_ids}
        }) if self.flight_offer_ids else 0
        total_bookings = self.db.bookings.count_documents({})
        
        results["booking_offer_refs"] = {
            "valid": valid_offer_refs == total_bookings,
            "message": f"{valid_offer_refs}/{total_bookings} bookings have valid flight offer references"
        }
        
        return results

    def validate_aviation_data_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Validate aviation-specific data patterns"""
        results = {}
        
        # Check IATA code formats
        invalid_airline_codes = self.db.airlines.count_documents({
            "iata_code": {"$not": {"$regex": "^[A-Z0-9]{2}$"}}
        })
        total_airlines = self.db.airlines.count_documents({})
        
        results["airline_iata_codes"] = {
            "valid": invalid_airline_codes == 0,
            "message": f"{total_airlines - invalid_airline_codes}/{total_airlines} airlines have valid IATA codes"
        }
        
        # Check airport code formats
        invalid_airport_codes = self.db.airports.count_documents({
            "iata_code": {"$not": {"$regex": "^[A-Z]{3}$"}}
        })
        total_airports = self.db.airports.count_documents({})
        
        results["airport_iata_codes"] = {
            "valid": invalid_airport_codes == 0,
            "message": f"{total_airports - invalid_airport_codes}/{total_airports} airports have valid IATA codes"
        }
        
        # Check currency code formats
        invalid_currency_codes = self.db.currencies.count_documents({
            "code": {"$not": {"$regex": "^[A-Z]{3}$"}}
        })
        total_currencies = self.db.currencies.count_documents({})
        
        results["currency_codes"] = {
            "valid": invalid_currency_codes == 0,
            "message": f"{total_currencies - invalid_currency_codes}/{total_currencies} currencies have valid codes"
        }
        
        return results

    def get_masked_connection_string(self) -> str:
        """Get a masked version of the connection string for display"""
        if "@" in self.connection_string:
            return self.connection_string.split("@")[-1]
        return self.connection_string

    def analyze_popular_routes(self) -> Dict[str, Any]:
        """Analyze popular flight routes"""
        pipeline = [
            {"$group": {
                "_id": {"origin": "$origin_code", "destination": "$destination_code"},
                "search_count": {"$sum": 1}
            }},
            {"$sort": {"search_count": -1}},
            {"$limit": 1}
        ]
        
        result = list(self.db.search_requests.aggregate(pipeline))
        most_popular = result[0] if result else {"_id": {"origin": "JFK", "destination": "LHR"}, "search_count": 0}
        
        unique_routes = self.db.search_requests.distinct("origin_code")
        total_searches = self.db.search_requests.count_documents({})
        
        return {
            "most_popular_route": f"{most_popular['_id']['origin']}-{most_popular['_id']['destination']}",
            "unique_routes": len(unique_routes),
            "avg_searches_per_route": total_searches / max(len(unique_routes), 1)
        }

    def analyze_airline_performance(self) -> Dict[str, Any]:
        """Analyze airline performance metrics"""
        pipeline = [
            {"$group": {
                "_id": "$validating_airline_codes",
                "offer_count": {"$sum": 1},
                "avg_price": {"$avg": "$total_price"}
            }},
            {"$sort": {"offer_count": -1}},
            {"$limit": 1}
        ]
        
        result = list(self.db.flight_offers.aggregate(pipeline))
        top_airline = result[0] if result else {"_id": ["AA"], "offer_count": 0}
        
        active_airlines = self.db.airlines.count_documents({"is_active": True})
        
        price_stats = list(self.db.flight_offers.aggregate([
            {"$group": {
                "_id": None,
                "min_price": {"$min": "$total_price"},
                "max_price": {"$max": "$total_price"}
            }}
        ]))
        
        return {
            "active_airlines": active_airlines,
            "top_airline_by_offers": top_airline["_id"][0] if top_airline["_id"] else "AA",
            "avg_price_low": price_stats[0]["min_price"] if price_stats else 200,
            "avg_price_high": price_stats[0]["max_price"] if price_stats else 2000
        }

    def analyze_booking_conversions(self) -> Dict[str, Any]:
        """Analyze booking conversion metrics"""
        total_searches = self.db.search_requests.count_documents({})
        total_bookings = self.db.bookings.count_documents({})
        
        avg_booking = list(self.db.bookings.aggregate([
            {"$group": {
                "_id": None,
                "avg_value": {"$avg": "$total_amount_paid"}
            }}
        ]))
        
        # Mock travel class analysis (would need to join with flight offers in real scenario)
        return {
            "total_bookings": total_bookings,
            "avg_booking_value": avg_booking[0]["avg_value"] if avg_booking else 800,
            "conversion_rate": total_bookings / max(total_searches, 1),
            "popular_travel_class": "Economy"
        }

    def analyze_aircraft_utilization(self) -> Dict[str, Any]:
        """Analyze aircraft utilization"""
        active_aircraft = self.db.aircraft.count_documents({"in_production": True})
        
        # Mock most used aircraft
        avg_capacity = list(self.db.aircraft.aggregate([
            {"$group": {
                "_id": None,
                "avg_capacity": {"$avg": "$capacity_total"}
            }}
        ]))
        
        return {
            "active_aircraft_types": active_aircraft,
            "most_used_aircraft": "Boeing 737-800",
            "avg_capacity": avg_capacity[0]["avg_capacity"] if avg_capacity else 180
        }

    def analyze_geographic_patterns(self) -> Dict[str, Any]:
        """Analyze geographic distribution patterns"""
        countries_served = self.db.countries.count_documents({})
        airports_count = self.db.airports.count_documents({"is_active": True})
        
        # Mock continent analysis
        return {
            "countries_served": countries_served,
            "busiest_continent": "Europe",
            "avg_airports_per_country": airports_count / max(countries_served, 1)
        }

    def run_seeding(self) -> Dict[str, Any]:
        """Execute the complete seeding process"""
        print("🚀 Starting Amadeus Flight Booking database seeding...")
        
        start_time = datetime.utcnow()
        results = {}
        
        # Seed reference data first
        results["countries"] = len(self.seed_countries(50))
        results["currencies"] = len(self.seed_currencies(20))
        results["airlines"] = len(self.seed_airlines(100))
        results["aircraft"] = len(self.seed_aircraft(50))
        results["airports"] = len(self.seed_airports(200))
        
        # Seed transaction data
        results["search_requests"] = len(self.seed_search_requests(10000))
        results["flight_offers"] = len(self.seed_flight_offers(50000))
        results["bookings"] = len(self.seed_bookings(5000))
        
        # Calculate totals
        results["total_documents"] = sum(results.values())
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        results["duration_seconds"] = duration
        
        print(f"\n✅ Seeding completed in {duration:.1f} seconds")
        print(f"📊 Total documents created: {results['total_documents']:,}")
        
        return results


# Create seeder instance
seeder = AmadeusFlightSeeder()