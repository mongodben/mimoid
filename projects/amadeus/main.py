#!/usr/bin/env python3
"""
Amadeus Flight Booking Database
Main execution script for seeding and validating the flight booking database

This script implements the complete workflow for creating and testing an 
Amadeus-style flight booking database, including:
- Airlines, aircraft, and airport reference data
- Realistic flight search requests and offers
- Booking transactions with traveler details
- Comprehensive pricing and route information
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any
import traceback
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Add the mimoid package to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from seed_db import seeder
from db_schema import database_schema


def print_header():
    """Print the application header with aviation theme"""
    print("✈️ AMADEUS FLIGHT BOOKING DATABASE")
    print("=" * 70)
    print("Comprehensive Flight Search and Booking Database System")
    print("Based on Amadeus Flight Offers Search API v2.2.0")
    print()
    print("🌍 Features:")
    print("  • Global airline and airport reference data")
    print("  • Realistic flight search requests and offers")
    print("  • Complete booking transactions with traveler details")
    print("  • Multi-currency pricing and fare calculations")
    print("  • Aircraft specifications and route optimization")
    print("  • Travel agency and corporate booking workflows")
    print()


def validate_environment():
    """Validate the environment and database connection"""
    print("🔍 Validating environment...")

    # Check MongoDB connection
    try:
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        print(f"  📡 MongoDB URI: {mongo_uri}")

        # Test database connection
        seeder.test_connection()
        print("  ✅ Database connection successful")

    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

    # Check required environment variables
    optional_vars = {
        "MONGODB_URI": os.getenv("MONGODB_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME", database_schema.database_name),
        "AVIATION_MODE": os.getenv("AVIATION_MODE", "true"),
        "DEBUG": os.getenv("DEBUG", "false"),
    }

    print("  🌐 Environment variables:")
    for var, value in optional_vars.items():
        if value is None:
            masked_value = "None"
        elif "URI" not in var:
            masked_value = value
        elif "@" in value:
            masked_value = value.split("@")[-1]
        else:
            masked_value = value
        print(f"    {var}: {masked_value}")

    return True


def run_database_setup():
    """Execute the complete database setup process"""
    print("🚀 Starting Amadeus flight booking database setup...")
    print()

    try:
        # Drop existing database if it exists
        print("🗑️  Preparing clean database environment...")
        seeder.drop_database()
        print("  ✅ Previous database cleared")

        # Create database schema
        print("🏗️  Creating database schema...")
        seeder.create_database_schema()
        print("  ✅ Database schema created with indexes")

        # Run the seeding process
        print()
        results = seeder.run_seeding()

        return results

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        if os.getenv("DEBUG") == "true":
            traceback.print_exc()
        raise


def run_validation_checks():
    """Run comprehensive validation checks on the seeded data"""
    print("🔍 Running validation checks...")

    try:
        # Check collection counts
        collection_counts = seeder.get_collection_stats()

        print("  📊 Collection Statistics:")
        for collection, count in collection_counts.items():
            print(f"    {collection}: {count:,} documents")

        # Validate data integrity
        print("\n  🔗 Data Integrity Checks:")

        # Check for orphaned references
        validation_results = seeder.validate_references()
        for check, result in validation_results.items():
            status = "✅" if result["valid"] else "⚠️"
            print(f"    {status} {check}: {result['message']}")

        # Aviation-specific validation
        print("\n  ✈️ Aviation Data Pattern Validation:")

        # Check IATA code formats
        aviation_validation = seeder.validate_aviation_data_patterns()
        for check, result in aviation_validation.items():
            status = "✅" if result["valid"] else "⚠️"
            print(f"    {status} {check}: {result['message']}")

        print("\n  ✅ All validation checks completed")
        return True

    except Exception as e:
        print(f"  ❌ Validation failed: {e}")
        if os.getenv("DEBUG") == "true":
            traceback.print_exc()
        return False


def generate_sample_queries():
    """Generate and execute sample queries to demonstrate the database"""
    print("📈 Executing sample queries...")

    try:
        # Sample query 1: Popular flight routes analysis
        print("\n  🌍 Popular Flight Routes Analysis:")
        route_stats = seeder.analyze_popular_routes()
        print(f"    • Most searched route: {route_stats['most_popular_route']}")
        print(f"    • Total unique routes: {route_stats['unique_routes']:,}")
        print(f"    • Average searches per route: {route_stats['avg_searches_per_route']:.1f}")

        # Sample query 2: Airline performance metrics
        print("\n  🏢 Airline Performance Analysis:")
        airline_stats = seeder.analyze_airline_performance()
        print(f"    • Total active airlines: {airline_stats['active_airlines']:,}")
        print(f"    • Top airline by offers: {airline_stats['top_airline_by_offers']}")
        print(f"    • Average price range: ${airline_stats['avg_price_low']:.0f} - ${airline_stats['avg_price_high']:.0f}")

        # Sample query 3: Booking conversion analysis
        print("\n  💳 Booking Conversion Analysis:")
        booking_stats = seeder.analyze_booking_conversions()
        print(f"    • Total bookings: {booking_stats['total_bookings']:,}")
        print(f"    • Average booking value: ${booking_stats['avg_booking_value']:.2f}")
        print(f"    • Conversion rate: {booking_stats['conversion_rate']:.2%}")
        print(f"    • Most popular travel class: {booking_stats['popular_travel_class']}")

        # Sample query 4: Aircraft utilization
        print("\n  🛩️ Aircraft Fleet Analysis:")
        aircraft_stats = seeder.analyze_aircraft_utilization()
        print(f"    • Aircraft types in use: {aircraft_stats['active_aircraft_types']:,}")
        print(f"    • Most utilized aircraft: {aircraft_stats['most_used_aircraft']}")
        print(f"    • Average fleet capacity: {aircraft_stats['avg_capacity']:.0f} passengers")

        # Sample query 5: Geographic distribution
        print("\n  🗺️ Geographic Distribution:")
        geo_stats = seeder.analyze_geographic_patterns()
        print(f"    • Countries served: {geo_stats['countries_served']:,}")
        print(f"    • Busiest continent: {geo_stats['busiest_continent']}")
        print(f"    • Average airports per country: {geo_stats['avg_airports_per_country']:.1f}")

        print("\n  ✅ Sample queries completed successfully")
        return True

    except Exception as e:
        print(f"  ❌ Sample query execution failed: {e}")
        if os.getenv("DEBUG") == "true":
            traceback.print_exc()
        return False


def print_usage_examples():
    """Print usage examples and next steps"""
    print("📋 NEXT STEPS AND USAGE EXAMPLES")
    print("=" * 50)

    print("\n🔌 MongoDB Connection:")
    print(f"  mongo {seeder.get_masked_connection_string()}/{database_schema.database_name}")
    print("  # Or with MongoDB Compass:")
    print(f"  {seeder.get_masked_connection_string()}")

    print("\n✈️ Sample Flight Booking Queries:")

    print("\n  1. Find cheapest flights between popular routes:")
    print("""  db.flight_offers.aggregate([
    { $match: { 
        "itineraries.segments.departure.iataCode": "JFK",
        "itineraries.segments.arrival.iataCode": "LHR",
        currency_code: "USD"
    }},
    { $sort: { total_price: 1 }},
    { $limit: 10 },
    { $project: {
        offer_id: 1,
        total_price: 1,
        validating_airline_codes: 1,
        "itineraries.duration": 1
    }}
  ])""")

    print("\n  2. Analyze booking patterns by travel class:")
    print("""  db.bookings.aggregate([
    { $unwind: "$travelers" },
    { $group: {
        _id: "$travelers.type",
        total_bookings: { $sum: 1 },
        avg_amount: { $avg: "$total_amount_paid" },
        total_revenue: { $sum: "$total_amount_paid" }
    }},
    { $sort: { total_revenue: -1 }}
  ])""")

    print("\n  3. Popular aircraft types by route distance:")
    print("""  db.flight_offers.aggregate([
    { $lookup: {
        from: "aircraft",
        localField: "itineraries.segments.aircraft.code",
        foreignField: "iata_code",
        as: "aircraft_info"
    }},
    { $group: {
        _id: "$aircraft_info.name",
        total_flights: { $sum: 1 },
        avg_price: { $avg: "$total_price" },
        routes: { $addToSet: {
            origin: { $arrayElemAt: ["$itineraries.segments.departure.iataCode", 0] },
            destination: { $arrayElemAt: ["$itineraries.segments.arrival.iataCode", -1] }
        }}
    }},
    { $sort: { total_flights: -1 }},
    { $limit: 10 }
  ])""")

    print("\n  4. Search request trends and conversion rates:")
    print("""  db.search_requests.aggregate([
    { $group: {
        _id: {
            origin: "$origin_code",
            destination: "$destination_code"
        },
        search_count: { $sum: 1 },
        avg_response_time: { $avg: "$response_time_ms" },
        success_rate: { $avg: { $cond: [{ $gt: ["$results_count", 0] }, 1, 0] }}
    }},
    { $sort: { search_count: -1 }},
    { $limit: 20 }
  ])""")

    print("\n  5. Revenue analysis by airline and currency:")
    print("""  db.bookings.aggregate([
    { $group: {
        _id: {
            airline: "$validating_carrier",
            currency: "$payment_currency"
        },
        total_bookings: { $sum: 1 },
        total_revenue: { $sum: "$total_amount_paid" },
        avg_booking_value: { $avg: "$total_amount_paid" }
    }},
    { $sort: { total_revenue: -1 }},
    { $limit: 15 }
  ])""")

    print("\n📚 Database Schema:")
    print("  • airlines: Airline carriers with operational details")
    print("  • aircraft: Aircraft types and specifications")
    print("  • airports: Global airport directory with coordinates")
    print("  • countries: Geographic reference data")
    print("  • currencies: Exchange rates and formatting")
    print("  • search_requests: Flight search patterns and analytics")
    print("  • flight_offers: Available flights with pricing")
    print("  • bookings: Completed reservations and transactions")

    print(f"\n🎯 Database: {database_schema.database_name}")
    print(f"📝 Total Collections: {len(database_schema.collections)}")
    print("🌟 Optimized for high-volume flight booking operations")


def main():
    """Main execution function"""
    start_time = datetime.utcnow()

    try:
        # Print header
        print_header()

        # Validate environment
        if not validate_environment():
            sys.exit(1)
        print()

        # Run database setup
        results = run_database_setup()
        print()

        # Run validation checks
        if not run_validation_checks():
            print("⚠️ Some validations failed, but database was created successfully")
        print()

        # Execute sample queries
        generate_sample_queries()
        print()

        # Print usage examples
        print_usage_examples()

        # Final summary
        end_time = datetime.utcnow()
        total_duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("🎉 AMADEUS FLIGHT BOOKING DATABASE SETUP COMPLETED!")
        print("=" * 70)
        print(f"⏱️  Total execution time: {total_duration:.1f} seconds")
        print(f"📊 Documents created: {results['total_documents']:,}")
        print(f"✈️ Airlines: {results['airlines']:,}")
        print(f"🛩️ Aircraft types: {results['aircraft']:,}")
        print(f"🏢 Airports: {results['airports']:,}")
        print(f"🔍 Search requests: {results['search_requests']:,}")
        print(f"💺 Flight offers: {results['flight_offers']:,}")
        print(f"📋 Bookings: {results['bookings']:,}")
        print()
        print("🌟 Database ready for high-volume flight booking operations!")
        print("🚀 Start exploring with MongoDB Compass or API integration")

        return 0

    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        return 1

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        if os.getenv("DEBUG") == "true":
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())