"""
Main execution script for NeoLend Bank Digital Lending Platform
Runs seeding and validation with error handling and iteration support
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Add current directory and parent mimiod directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from seed_db import NeoLendBankSeeder, seed_database
from db_schema import database_schema


def test_mongodb_connection(connection_string: str) -> bool:
    """Test MongoDB connection before proceeding"""
    try:
        print("Testing MongoDB connection...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        print("✅ MongoDB connection successful")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Unexpected connection error: {e}")
        return False


def validate_schema_import() -> bool:
    """Validate that the database schema can be imported and instantiated"""
    try:
        print("Validating database schema...")
        # Try to access schema properties
        db_name = database_schema.database_name
        collections = list(database_schema.collections.keys())
        print(f"✅ Schema validation passed - Database: {db_name}, Collections: {len(collections)}")
        print(f"   Collections: {', '.join(collections)}")
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False


def run_pre_execution_checks(connection_string: str) -> bool:
    """Run all pre-execution validation checks"""
    print("=" * 60)
    print("NEOLEND BANK DIGITAL LENDING PLATFORM")
    print("=" * 60)
    
    # Check 1: Schema validation
    if not validate_schema_import():
        return False
    
    # Check 2: Database connection
    if not test_mongodb_connection(connection_string):
        return False
    
    print("✅ All pre-execution checks passed!\n")
    return True


def generate_summary_report(connection_string: str):
    """Generate a summary report of the seeded database"""
    try:
        client = MongoClient(connection_string)
        db = client[database_schema.database_name]
        
        print("\n" + "=" * 60)
        print("DATABASE SUMMARY REPORT")
        print("=" * 60)
        print(f"Database: {database_schema.database_name}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        total_documents = 0
        for collection_name in database_schema.collections.keys():
            count = db[collection_name].count_documents({})
            total_documents += count
            print(f"{collection_name:20}: {count:,} documents")
        
        print("-" * 60)
        print(f"{'Total Documents':20}: {total_documents:,}")
        
        # Sample some data to show what was generated
        print("\n📊 Sample Data:")
        print("-" * 60)
        
        # Show sample customer with alternative credit data
        sample_customer = db.customers.find_one({}, {
            'first_name': 1, 'last_name': 1, 'phone_number': 1, 
            'current_credit_score': 1, 'risk_level': 1, 'monthly_income': 1,
            'social_media_data': 1, 'device_data': 1
        })
        if sample_customer:
            print(f"Sample Customer: {sample_customer.get('first_name')} {sample_customer.get('last_name')}")
            print(f"  Phone: {sample_customer.get('phone_number')}")
            print(f"  Credit Score: {sample_customer.get('current_credit_score')}")
            print(f"  Risk Level: {sample_customer.get('risk_level', 'N/A')}")
            print(f"  Monthly Income: ${sample_customer.get('monthly_income', 0):.2f}")
            
            # Show alternative data presence
            alt_data_sources = []
            if sample_customer.get('social_media_data'):
                alt_data_sources.append('Social Media')
            if sample_customer.get('device_data'):
                alt_data_sources.append('Device Data')
            print(f"  Alternative Data: {', '.join(alt_data_sources) if alt_data_sources else 'None'}")
        
        # Show loan application approval rates
        total_applications = db.loan_applications.count_documents({})
        approved_applications = db.loan_applications.count_documents({'status': 'approved'})
        if total_applications > 0:
            approval_rate = (approved_applications / total_applications) * 100
            print(f"\n📈 Loan Applications:")
            print(f"  Total Applications: {total_applications:,}")
            print(f"  Approved: {approved_applications:,} ({approval_rate:.1f}%)")
        
        # Show active loans and collection cases
        active_loans = db.loans.count_documents({'status': 'active'})
        overdue_loans = db.loans.count_documents({'days_past_due': {'$gt': 0}})
        collection_cases = db.collection_cases.count_documents({'case_status': 'open'})
        
        print(f"\n💰 Loan Portfolio:")
        print(f"  Active Loans: {active_loans:,}")
        print(f"  Overdue Loans: {overdue_loans:,}")
        print(f"  Active Collection Cases: {collection_cases:,}")
        
        # Show payment statistics
        total_payments = db.payments.count_documents({})
        completed_payments = db.payments.count_documents({'status': 'completed'})
        if total_payments > 0:
            success_rate = (completed_payments / total_payments) * 100
            print(f"\n💳 Payments:")
            print(f"  Total Payments: {total_payments:,}")
            print(f"  Completed: {completed_payments:,} ({success_rate:.1f}%)")
        
        # Show alternative credit scoring metrics
        credit_scores = list(db.credit_scores.find({}, {
            'alternative_data_weight': 1,
            'confidence_level': 1
        }).limit(100))
        
        if credit_scores:
            avg_alt_weight = sum(score.get('alternative_data_weight', 0) for score in credit_scores) / len(credit_scores)
            avg_confidence = sum(score.get('confidence_level', 0) for score in credit_scores) / len(credit_scores)
            print(f"\n🤖 AI Credit Scoring:")
            print(f"  Average Alternative Data Weight: {avg_alt_weight:.1%}")
            print(f"  Average Model Confidence: {avg_confidence:.1%}")
        
        print("\n🎉 Digital lending database ready for microfinance operations!")
        
    except Exception as e:
        print(f"❌ Error generating summary report: {e}")


def main():
    """Main execution function"""
    # Configuration
    CONNECTION_STRING = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    
    # Custom record counts for digital lending platform
    RECORD_COUNTS = {
        'customers': 2500,          # Digital lending customers
        'loan_applications': 4000,   # More applications than approvals
        'loans': 2800,              # Approved loans
        'payments': 15000,          # Multiple payments per loan
        'credit_scores': 5000,      # AI scoring events
        'collection_cases': 300,    # Overdue loan collection
        'compliance_records': 800   # Regulatory compliance
    }
    
    print("Starting NeoLend Bank digital lending platform setup...")
    
    # Step 1: Pre-execution validation
    if not run_pre_execution_checks(CONNECTION_STRING):
        print("\n❌ Pre-execution checks failed. Please fix issues and try again.")
        sys.exit(1)
    
    # Step 2: Execute seeding
    try:
        print("🚀 Starting database seeding process...")
        print("🏦 Generating digital lending platform with AI-powered credit scoring")
        print(f"Target record counts: {RECORD_COUNTS}")
        print("-" * 60)
        
        success = seed_database(
            connection_string=CONNECTION_STRING,
            record_counts=RECORD_COUNTS
        )
        
        if not success:
            print("\n❌ Database seeding completed with validation errors")
            print("Check the output above for specific issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during seeding: {e}")
        print("Please check your MongoDB connection and schema configuration")
        sys.exit(1)
    
    # Step 3: Generate final report
    generate_summary_report(CONNECTION_STRING)
    
    print(f"\n💡 Connection string: {CONNECTION_STRING}")
    print(f"💡 Database name: {database_schema.database_name}")
    print("\n✨ Setup complete! Your digital lending platform is ready for microfinance operations.")
    print("\n🔍 Key Features:")
    print("   • AI-powered alternative credit scoring")
    print("   • Flexible unstructured data handling")
    print("   • Comprehensive loan lifecycle management")
    print("   • Automated collections and compliance tracking")


if __name__ == "__main__":
    main()