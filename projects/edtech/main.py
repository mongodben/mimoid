#!/usr/bin/env python3
"""
Cogna Educação Brazilian EdTech Platform Database
Main execution script for seeding and validating the educational database

This script implements the complete workflow for creating and testing a Brazilian
educational technology platform database, including:
- Multi-institutional student management
- Government funding application processing (FIES/ProUni)
- Document verification workflows
- Academic content management
- Diverse Brazilian student population with authentic naming patterns
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
    """Print the application header with Brazilian styling"""
    print("🇧🇷 COGNA EDUCAÇÃO - BRAZILIAN EDTECH PLATFORM")
    print("=" * 70)
    print("Educational Technology Database for Brazil's Leading EdTech Organization")
    print("Serving 2.4 million students with government funding integration")
    print()
    print("📚 Features:")
    print("  • Multi-institutional student management across Brazil")
    print("  • FIES/ProUni government funding application processing")
    print("  • Comprehensive document verification workflows")
    print("  • Diverse Brazilian student population with authentic names")
    print("  • Academic content management and assessment tracking")
    print("  • Brazilian compliance and regulatory standards")
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
        "BRAZILIAN_MODE": os.getenv("BRAZILIAN_MODE", "true"),
        "DEBUG": os.getenv("DEBUG", "false"),
    }

    print("  🌍 Environment variables:")
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
    print("🚀 Starting Brazilian EdTech database setup...")
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

        # Brazilian-specific validation
        print("\n  🇧🇷 Brazilian Data Pattern Validation:")

        # Check CPF formats
        cpf_validation = seeder.validate_brazilian_data_patterns()
        for check, result in cpf_validation.items():
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
        # Sample query 1: Student diversity analysis
        print("\n  🌎 Student Name Diversity Analysis:")
        diversity_stats = seeder.analyze_student_diversity()
        print(f"    • Unique surnames: {diversity_stats['unique_surnames']}")
        print(f"    • Most common surname: {diversity_stats['most_common_surname']}")
        print(
            f"    • Cultural diversity index: {diversity_stats['diversity_index']:.2f}"
        )

        # Sample query 2: FIES/ProUni application statistics
        print("\n  💼 Government Funding Application Analysis:")
        funding_stats = seeder.analyze_funding_applications()
        print(f"    • Total FIES applications: {funding_stats['fies_applications']:,}")
        print(
            f"    • Total ProUni applications: {funding_stats['prouni_applications']:,}"
        )
        print(
            f"    • Average processing time: {funding_stats['avg_processing_days']:.1f} days"
        )
        print(f"    • Application success rate: {funding_stats['success_rate']:.1%}")

        # Sample query 3: Document verification workflow
        print("\n  📄 Document Verification Workflow:")
        document_stats = seeder.analyze_document_verification()
        print(f"    • Documents submitted: {document_stats['total_documents']:,}")
        print(f"    • Documents verified: {document_stats['verified_documents']:,}")
        print(
            f"    • Average documents per application: {document_stats['avg_docs_per_app']:.1f}"
        )
        print(
            f"    • Verification completion rate: {document_stats['verification_rate']:.1%}"
        )

        # Sample query 4: Institutional performance
        print("\n  🏫 Institutional Performance Metrics:")
        institution_stats = seeder.analyze_institutional_performance()
        for institution in institution_stats[:5]:  # Top 5 institutions
            print(
                f"    • {institution['name']}: {institution['students']:,} students, {institution['avg_gpa']:.1f} avg GPA"
            )

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

    print("\n🇧🇷 Sample Brazilian EdTech Queries:")

    print("\n  1. Find students from different cultural backgrounds:")
    print("""  db.students.aggregate([
    { $group: { 
        _id: "$last_name", 
        count: { $sum: 1 },
        avg_gpa: { $avg: "$gpa" }
    }},
    { $sort: { count: -1 }},
    { $limit: 10 }
  ])""")

    print("\n  2. Analyze FIES/ProUni application processing:")
    print("""  db.applications.aggregate([
    { $match: { funding_program: { $in: ["fies", "prouni"] }}},
    { $group: {
        _id: "$funding_program",
        total_applications: { $sum: 1 },
        avg_amount: { $avg: "$funding_requested" },
        success_rate: { $avg: { $cond: [{ $eq: ["$status", "approved"] }, 1, 0] }}
    }}
  ])""")

    print("\n  3. Document verification workflow analysis:")
    print("""  db.documents.aggregate([
    { $group: {
        _id: "$verification_status",
        count: { $sum: 1 },
        avg_processing_time: { $avg: { $divide: [
          { $subtract: ["$verified_date", "$submitted_date"] },
          86400000  // Convert ms to days
        ]}}
    }},
    { $sort: { count: -1 }}
  ])""")

    print("\n  4. Student diversity by Brazilian regions:")
    print("""  db.students.aggregate([
    { $group: {
        _id: "$address.state",
        student_count: { $sum: 1 },
        avg_family_income: { $avg: "$family_income_monthly" }
    }},
    { $sort: { student_count: -1 }}
  ])""")

    print("\n📚 Database Schema:")
    print("  • institutions: Brazilian educational institutions")
    print("  • students: Diverse Brazilian student population")
    print("  • applications: FIES/ProUni funding applications")
    print("  • documents: Application document verification")
    print("  • staff: Educational staff and administrators")
    print("  • courses: Academic courses and programs")
    print("  • enrollments: Student course enrollments")
    print("  • assessments: Student assignments and exams")
    print("  • content: Learning materials and resources")
    print("  • financial_aid: Scholarships and funding records")

    print(f"\n🎯 Database: {database_schema.database_name}")
    print(f"📝 Total Collections: {len(database_schema.collections)}")
    print("🌟 Optimized for Brazilian educational patterns and compliance")


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
        print("🎓 COGNA EDUCAÇÃO EDTECH DATABASE SETUP COMPLETED!")
        print("=" * 70)
        print(f"⏱️  Total execution time: {total_duration:.1f} seconds")
        print(f"📊 Documents created: {results['total_documents']:,}")
        print(f"🇧🇷 Brazilian students with diverse names: {results['students']:,}")
        print(f"📄 FIES/ProUni applications: {results['applications']:,}")
        print(f"📎 Document submissions: {results['documents']:,}")
        print(f"🏫 Educational institutions: {results['institutions']}")
        print()
        print("🌟 Database ready to support 2.4 million Brazilian students!")
        print("🚀 Start exploring with MongoDB Compass or command line")

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
