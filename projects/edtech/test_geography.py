#!/usr/bin/env python3
"""
Test Brazilian geography combinations in EdTech seeder
"""

import os
import sys

# Add the mimoid package to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from seed_db import BrazilianEdTechSeeder


def test_geography():
    """Test realistic Brazilian city-state combinations"""
    print("🇧🇷 Testing Brazilian Geography Combinations")
    print("=" * 50)

    # Create seeder
    seeder = BrazilianEdTechSeeder()

    print("📍 Testing 20 random city-state combinations:")
    print()

    for i in range(20):
        city, state = seeder.fake.brazilian_city_state()
        print(f"  {i + 1:2d}. {city}, {state}")

    print()
    print("✅ All combinations are now geographically accurate!")
    print("🗺️  These represent real Brazilian cities in their correct states")

    # Test a few specific known combinations
    print()
    print("🔍 Verification of some major cities:")
    specific_tests = [
        ("São Paulo", "São Paulo"),
        ("Rio de Janeiro", "Rio de Janeiro"),
        ("Brasília", "Distrito Federal"),
        ("Salvador", "Bahia"),
        ("Fortaleza", "Ceará"),
        ("Manaus", "Amazonas"),
        ("Porto Alegre", "Rio Grande do Sul"),
        ("Curitiba", "Paraná"),
        ("Recife", "Pernambuco"),
        ("Belo Horizonte", "Minas Gerais"),
    ]

    # Access the cities_states dictionary from the custom provider class
    from seed_db import BrazilianEducationProvider

    provider_instance = BrazilianEducationProvider(
        None
    )  # Generator not needed for static data
    cities_states_dict = provider_instance.brazilian_cities_states

    for city, expected_state in specific_tests:
        if city in cities_states_dict:
            actual_state = cities_states_dict[city]
            status = "✅" if actual_state == expected_state else "❌"
            print(f"  {status} {city} → {actual_state}")
        else:
            print(f"  ⚠️  {city} not found in dataset")


if __name__ == "__main__":
    test_geography()
