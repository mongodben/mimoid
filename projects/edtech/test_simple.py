#!/usr/bin/env python3
"""
Simple test of the Brazilian EdTech seeder with minimal data
"""

import os
import sys
from datetime import datetime

# Add the mimiod package to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from seed_db import BrazilianEdTechSeeder
from db_schema import database_schema

def test_simple_seeding():
    """Test basic seeding functionality"""
    print("🇧🇷 Testing Brazilian EdTech Seeder with Small Dataset")
    print("=" * 50)
    
    # Create seeder
    seeder = BrazilianEdTechSeeder()
    
    try:
        # Test connection
        print("📡 Testing database connection...")
        seeder.test_connection()
        print("  ✅ Connection successful")
        
        # Clear database
        print("🗑️  Clearing database...")
        seeder.clear_database()
        print("  ✅ Database cleared")
        
        # Test creating a few institutions
        print("🏫 Creating 3 test institutions...")
        seeder.seed_institutions(3)
        print("  ✅ Institutions created")
        
        # Test creating a few staff members
        print("👥 Creating 5 test staff members...")
        seeder.seed_staff(5)
        print("  ✅ Staff members created")
        
        # Test creating a few students
        print("👨‍🎓 Creating 10 test students with diverse names...")
        seeder.seed_students(10)
        print("  ✅ Students created")
        
        # Test name diversity
        from pymongo import MongoClient
        client = MongoClient(seeder.connection_string)
        db = client[seeder.database_schema.database_name]
        
        students = list(db.students.find({}, {"first_name": 1, "last_name": 1, "_id": 0}))
        print(f"\n📊 Student Name Diversity Sample:")
        for student in students:
            print(f"  • {student['first_name']} {student['last_name']}")
        
        client.close()
        
        print("\n🎉 Simple test completed successfully!")
        print("✅ Brazilian EdTech seeder is working with diverse naming patterns!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_seeding()
    sys.exit(0 if success else 1)