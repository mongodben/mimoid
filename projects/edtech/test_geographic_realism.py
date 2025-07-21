#!/usr/bin/env python3
"""
Test geographic realism in Brazilian EdTech seeder
"""

import os
import sys

# Add the mimoid package to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from seed_db import BrazilianEdTechSeeder


def test_geographic_realism():
    """Test that generated student data has realistic city-state combinations"""
    print("🇧🇷 Testing Geographic Realism in Student Data")
    print("=" * 55)

    # Create seeder
    seeder = BrazilianEdTechSeeder()

    try:
        # Clear database
        print("🗑️  Clearing database...")
        seeder.clear_database()

        # Create institutions
        print("🏫 Creating institutions...")
        seeder.seed_institutions(3)

        # Create students
        print("👨‍🎓 Creating 20 students...")
        seeder.seed_students(20)

        # Check the geographic data
        from pymongo import MongoClient

        client = MongoClient(seeder.connection_string)
        db = client[seeder.database_schema.database_name]

        print("\n📍 Student Geographic Distribution:")
        print(
            "   #  Name                          Birth Place                        Residence"
        )
        print("   " + "=" * 85)

        students = list(
            db.students.find(
                {},
                {
                    "first_name": 1,
                    "last_name": 1,
                    "birth_place": 1,
                    "city": 1,
                    "state": 1,
                    "_id": 0,
                },
            ).limit(20)
        )

        for i, student in enumerate(students, 1):
            name = f"{student['first_name']} {student['last_name']}"
            birth = student.get("birth_place", "N/A")
            residence = f"{student.get('city', 'N/A')}, {student.get('state', 'N/A')}"

            print(f"   {i:2d}  {name:<30} {birth:<30} {residence}")

        print("\n🔍 Geographic Validation:")

        # Validate city-state combinations
        from seed_db import BrazilianEducationProvider

        provider = BrazilianEducationProvider(None)
        cities_states = provider.brazilian_cities_states

        valid_combinations = 0
        total_combinations = 0

        for student in students:
            city = student.get("city")
            state = student.get("state")

            if city and state:
                total_combinations += 1
                if city in cities_states and cities_states[city] == state:
                    valid_combinations += 1
                else:
                    print(f"   ❌ Invalid: {city}, {state}")

        validation_rate = (
            (valid_combinations / total_combinations * 100)
            if total_combinations > 0
            else 0
        )

        print(f"\n📊 Geographic Accuracy Results:")
        print(f"   • Total students: {len(students)}")
        print(f"   • City-state combinations checked: {total_combinations}")
        print(f"   • Valid combinations: {valid_combinations}")
        print(f"   • Accuracy rate: {validation_rate:.1f}%")

        if validation_rate == 100.0:
            print(
                f"   ✅ Perfect! All city-state combinations are geographically accurate"
            )
        else:
            print(f"   ⚠️  Some combinations need fixing")

        # Show state distribution
        print(f"\n🗺️  State Distribution:")
        state_counts = {}
        for student in students:
            state = student.get("state")
            if state:
                state_counts[state] = state_counts.get(state, 0) + 1

        for state, count in sorted(
            state_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"   • {state}: {count} student{'s' if count != 1 else ''}")

        client.close()

        print(f"\n🎉 Geographic realism test completed!")
        return validation_rate == 100.0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_geographic_realism()
    sys.exit(0 if success else 1)
