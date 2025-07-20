"""Database seeder for MetaSteel Industries - Global Product Quality System"""

from faker import Faker
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Optional, List, Any
import logging
from decimal import Decimal
import math

# Import the database schema and base types
from db_schema import (
    database_schema,
    FacilityType,
    ProductionLineStatus,
    ProductType,
    QualityGrade,
    DefectSeverity,
    DefectType,
    CheckpointType,
    TestMethod
)
from mimiod import DatabaseSeeder as BaseDatabaseSeeder, PyObjectId

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SteelProductionSeeder(BaseDatabaseSeeder):
    """Database seeder for steel production quality system"""
    
    def __init__(self, connection_string: str):
        super().__init__(connection_string, database_schema)
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        self.fake = Faker()
        
        # Steel-specific data for realistic generation
        self.steel_grades = [
            "A36", "A572", "A992", "S355", "S275", "Q345", "Q235",
            "HSLA-50", "HSLA-65", "DP590", "DP780", "TRIP690"
        ]
        
        self.chemical_elements = {
            "C": (0.05, 0.25),  # Carbon
            "Mn": (0.3, 1.5),   # Manganese
            "Si": (0.1, 0.5),   # Silicon
            "P": (0.01, 0.04),  # Phosphorus
            "S": (0.005, 0.05), # Sulfur
            "Cr": (0.05, 0.3),  # Chromium
            "Ni": (0.02, 0.2),  # Nickel
            "Mo": (0.01, 0.1),  # Molybdenum
            "Al": (0.02, 0.08), # Aluminum
            "Cu": (0.02, 0.3),  # Copper
        }
        
        self.defect_subtypes = {
            DefectType.SURFACE_DEFECT: ["scratches", "pits", "scale", "roll_marks", "edge_cracks"],
            DefectType.DIMENSIONAL_DEFECT: ["thickness_variation", "width_deviation", "camber", "flatness"],
            DefectType.CHEMICAL_DEFECT: ["carbon_high", "manganese_low", "sulfur_high", "inclusion"],
            DefectType.MECHANICAL_DEFECT: ["low_strength", "poor_ductility", "hardness_variation"],
            DefectType.COATING_DEFECT: ["uneven_coating", "bare_spots", "coating_defects"]
        }
        
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        if num_records is None:
            num_records = {
                'facilities': 8,
                'production_lines': 40,
                'products': 25,
                'production_batches': 500,
                'quality_checkpoints': 50000,
                'defects': 2500,
                'test_results': 5000,
                'customer_specifications': 15
            }
            
        logger.info("Starting database seeding process...")
        
        # Seed in dependency order
        facility_ids = self.seed_facilities(num_records['facilities'])
        line_ids = self.seed_production_lines(num_records['production_lines'], facility_ids)
        product_ids = self.seed_products(num_records['products'])
        batch_ids = self.seed_production_batches(num_records['production_batches'], facility_ids, line_ids, product_ids)
        
        # High-volume time-series data
        self.seed_quality_checkpoints(num_records['quality_checkpoints'], facility_ids, line_ids, batch_ids)
        self.seed_defects(num_records['defects'], facility_ids, line_ids, batch_ids)
        self.seed_test_results(num_records['test_results'], facility_ids, batch_ids, product_ids)
        self.seed_customer_specifications(num_records['customer_specifications'], product_ids)
        
        logger.info("Database seeding completed successfully!")
        
    def seed_facilities(self, count: int) -> List[ObjectId]:
        """Generate and insert facility documents"""
        logger.info(f"Seeding {count} facilities...")
        
        facilities = []
        countries = ["United States", "Germany", "China", "Brazil", "India", "South Korea", "Japan", "Canada"]
        
        for i in range(count):
            country = random.choice(countries)
            facility = {
                '_id': ObjectId(),
                'facility_name': f"{self.fake.company()} Steel Plant {i+1}",
                'facility_code': f"MSI-{i+1:03d}",
                'facility_type': random.choice(list(FacilityType)),
                'country': country,
                'city': self.fake.city(),
                'address': {
                    'street': self.fake.street_address(),
                    'postal_code': self.fake.postcode(),
                    'state_province': self.fake.state()
                },
                'coordinates': {
                    'latitude': float(self.fake.latitude()),
                    'longitude': float(self.fake.longitude())
                },
                'annual_capacity_tons': random.randint(500000, 12000000),
                'operational_since': self.fake.date_time_between(start_date='-30y', end_date='-2y'),
                'iso_certifications': random.sample(['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 50001'], k=random.randint(2, 4)),
                'quality_standards': random.sample(['ASTM', 'EN', 'JIS', 'GB', 'API'], k=random.randint(2, 4)),
                'plant_manager': self.fake.name(),
                'quality_manager': self.fake.name(),
                'contact_info': {
                    'phone': self.fake.phone_number(),
                    'email': self.fake.company_email(),
                    'website': self.fake.url()
                },
                'is_active': True,
                'last_audit_date': self.fake.date_time_between(start_date='-1y', end_date='now'),
                'created_at': datetime.utcnow(),
                'updated_at': None
            }
            facilities.append(facility)
            
        self.db.facilities.insert_many(facilities)
        logger.info(f"Inserted {len(facilities)} facilities")
        return [facility['_id'] for facility in facilities]
        
    def seed_production_lines(self, count: int, facility_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert production line documents"""
        logger.info(f"Seeding {count} production lines...")
        
        lines = []
        for i in range(count):
            facility_id = random.choice(facility_ids)
            line_number = (i % 8) + 1  # 1-8 lines per facility
            
            # Equipment list for a typical steel production line
            equipment_list = [
                {'type': 'reheating_furnace', 'id': f'RF-{i+1}', 'status': 'operational'},
                {'type': 'roughing_mill', 'id': f'RM-{i+1}', 'status': 'operational'},
                {'type': 'finishing_mill', 'id': f'FM-{i+1}', 'status': 'operational'},
                {'type': 'cooling_system', 'id': f'CS-{i+1}', 'status': 'operational'},
                {'type': 'coiling_station', 'id': f'COI-{i+1}', 'status': 'operational'}
            ]
            
            # Quality checkpoint locations along the line
            checkpoint_locations = [
                {'position_km': 0.2, 'type': 'temperature_measurement', 'equipment': 'pyrometer_1'},
                {'position_km': 0.8, 'type': 'dimensional_check', 'equipment': 'gauge_1'},
                {'position_km': 1.4, 'type': 'surface_inspection', 'equipment': 'camera_1'},
                {'position_km': 1.9, 'type': 'chemical_analysis', 'equipment': 'spectrometer_1'},
                {'position_km': 2.0, 'type': 'final_inspection', 'equipment': 'multi_sensor_1'}
            ]
            
            line = {
                '_id': ObjectId(),
                'facility_id': facility_id,
                'line_name': f"Production Line {line_number}",
                'line_code': f"PL-{i+1:03d}",
                'line_number': line_number,
                'product_types': random.sample(list(ProductType), k=random.randint(2, 4)),
                'max_width_mm': random.choice([1200, 1500, 1800, 2100]),
                'max_thickness_mm': random.uniform(3.0, 25.0),
                'production_speed_mpm': random.uniform(8.0, 15.0),
                'annual_capacity_tons': random.randint(800000, 2500000),
                'equipment_list': equipment_list,
                'checkpoint_locations': checkpoint_locations,
                'status': random.choice([ProductionLineStatus.OPERATIONAL] * 8 + [ProductionLineStatus.MAINTENANCE]),
                'current_product': random.choice(self.steel_grades) if random.random() > 0.2 else None,
                'current_speed_mpm': random.uniform(6.0, 12.0) if random.random() > 0.3 else None,
                'current_temperature_c': random.uniform(1100, 1250) if random.random() > 0.3 else None,
                'efficiency_percent': random.uniform(78, 96),
                'quality_score': random.uniform(92, 99.5),
                'downtime_hours_monthly': random.uniform(8, 48),
                'last_maintenance_date': self.fake.date_time_between(start_date='-3m', end_date='-1w'),
                'next_maintenance_date': self.fake.date_time_between(start_date='now', end_date='+2m'),
                'created_at': datetime.utcnow(),
                'updated_at': None
            }
            lines.append(line)
            
        self.db.production_lines.insert_many(lines)
        logger.info(f"Inserted {len(lines)} production lines")
        return [line['_id'] for line in lines]
        
    def seed_products(self, count: int) -> List[ObjectId]:
        """Generate and insert product documents"""
        logger.info(f"Seeding {count} products...")
        
        products = []
        applications = [
            "automotive", "construction", "shipbuilding", "energy", "appliances",
            "packaging", "agriculture", "machinery", "infrastructure", "aerospace"
        ]
        
        for i in range(count):
            grade = random.choice(self.steel_grades)
            product_type = random.choice(list(ProductType))
            
            # Generate realistic chemical composition
            composition = {}
            for element, (min_val, max_val) in self.chemical_elements.items():
                composition[element] = round(random.uniform(min_val, max_val), 3)
            
            product = {
                '_id': ObjectId(),
                'product_code': f"MSI-{product_type.value.upper()}-{grade}-{i+1:03d}",
                'product_name': f"{grade} {product_type.value.replace('_', ' ').title()}",
                'product_type': product_type,
                'grade': grade,
                'nominal_thickness_mm': random.uniform(1.0, 20.0) if product_type in [ProductType.HOT_ROLLED_COIL, ProductType.COLD_ROLLED_COIL] else None,
                'nominal_width_mm': random.choice([1000, 1200, 1500, 1800, 2000]) if 'coil' in product_type.value else None,
                'nominal_length_mm': random.randint(6000, 12000) if product_type == ProductType.STEEL_PLATE else None,
                'nominal_weight_kg': random.uniform(5000, 25000),
                'chemical_composition': composition,
                'yield_strength_mpa': random.randint(250, 690),
                'tensile_strength_mpa': random.randint(400, 800),
                'elongation_percent': random.uniform(15, 35),
                'hardness_hv': random.randint(150, 300),
                'surface_quality': random.choice(["commercial", "drawing", "structural", "exposed"]),
                'tolerance_class': random.choice(["normal", "special", "precision"]),
                'application_areas': random.sample(applications, k=random.randint(2, 5)),
                'applicable_standards': random.sample(['ASTM A36', 'EN 10025', 'JIS G3101', 'API 5L'], k=random.randint(1, 3)),
                'target_markets': random.sample(['North America', 'Europe', 'Asia', 'South America'], k=random.randint(1, 3)),
                'customer_specifications': {},
                'is_active': True,
                'development_stage': random.choice(["production"] * 8 + ["development", "pilot"]),
                'created_at': datetime.utcnow(),
                'updated_at': None
            }
            products.append(product)
            
        self.db.products.insert_many(products)
        logger.info(f"Inserted {len(products)} products")
        return [product['_id'] for product in products]
        
    def seed_production_batches(self, count: int, facility_ids: List[ObjectId], 
                               line_ids: List[ObjectId], product_ids: List[ObjectId]) -> List[ObjectId]:
        """Generate and insert production batch documents"""
        logger.info(f"Seeding {count} production batches...")
        
        batches = []
        batch_counter = 1
        
        for i in range(count):
            facility_id = random.choice(facility_ids)
            line_id = random.choice(line_ids)
            product_id = random.choice(product_ids)
            
            production_start = self.fake.date_time_between(start_date='-1y', end_date='-1d')
            production_duration = timedelta(hours=random.uniform(4, 24))
            production_end = production_start + production_duration
            
            planned_quantity = random.uniform(50, 500)  # tons
            actual_quantity = planned_quantity * random.uniform(0.92, 1.08)  # Some variation
            
            batch = {
                '_id': ObjectId(),
                'facility_id': facility_id,
                'production_line_id': line_id,
                'product_id': product_id,
                'batch_number': f"B{batch_counter:06d}",
                'lot_number': f"L{self.fake.year()}{batch_counter:04d}",
                'production_start': production_start,
                'production_end': production_end,
                'planned_quantity_tons': planned_quantity,
                'actual_quantity_tons': actual_quantity,
                'raw_material_batches': [
                    {'material': 'iron_ore', 'batch_id': f"IO-{random.randint(1000, 9999)}"},
                    {'material': 'coal', 'batch_id': f"C-{random.randint(1000, 9999)}"},
                    {'material': 'limestone', 'batch_id': f"LS-{random.randint(1000, 9999)}"}
                ],
                'heat_number': f"H{random.randint(100000, 999999)}",
                'process_parameters': {
                    'heating_temp_c': random.uniform(1150, 1280),
                    'rolling_force_kn': random.uniform(8000, 15000),
                    'cooling_rate_c_per_s': random.uniform(10, 30),
                    'final_temp_c': random.uniform(600, 800)
                },
                'average_temperature_c': random.uniform(1180, 1250),
                'rolling_speed_mpm': random.uniform(8, 14),
                'quality_grade': random.choice([QualityGrade.PRIME] * 6 + [QualityGrade.COMMERCIAL] * 3 + [QualityGrade.SECONDARY]),
                'overall_quality_score': random.uniform(85, 99.5),
                'defect_count': random.randint(0, 12),
                'checkpoint_count': random.randint(150, 250),
                'customer_order_id': f"CO-{random.randint(10000, 99999)}" if random.random() > 0.3 else None,
                'shipping_destination': self.fake.city() if random.random() > 0.2 else None,
                'batch_status': random.choice(["completed"] * 7 + ["in_production", "quality_check"]),
                'is_shipped': random.choice([True, False]),
                'shipped_date': production_end + timedelta(days=random.randint(1, 14)) if random.random() > 0.4 else None,
                'created_at': production_start,
                'updated_at': production_end
            }
            batches.append(batch)
            batch_counter += 1
            
        self.db.production_batches.insert_many(batches)
        logger.info(f"Inserted {len(batches)} production batches")
        return [batch['_id'] for batch in batches]
        
    def seed_quality_checkpoints(self, count: int, facility_ids: List[ObjectId], 
                                line_ids: List[ObjectId], batch_ids: List[ObjectId]):
        """Generate and insert quality checkpoint documents"""
        logger.info(f"Seeding {count} quality checkpoints...")
        
        # Process in batches to handle large volumes
        batch_size = 1000
        checkpoints_inserted = 0
        
        while checkpoints_inserted < count:
            current_batch_size = min(batch_size, count - checkpoints_inserted)
            checkpoints = []
            
            for i in range(current_batch_size):
                facility_id = random.choice(facility_ids)
                line_id = random.choice(line_ids)
                batch_id = random.choice(batch_ids)
                
                checkpoint_type = random.choice(list(CheckpointType))
                measurement_time = self.fake.date_time_between(start_date='-1y', end_date='now')
                
                # Generate realistic sensor readings based on checkpoint type
                sensor_readings = self._generate_sensor_readings(checkpoint_type)
                
                checkpoint = {
                    '_id': ObjectId(),
                    'facility_id': facility_id,
                    'production_line_id': line_id,
                    'batch_id': batch_id,
                    'checkpoint_id': f"CP-{checkpoints_inserted + i + 1:08d}",
                    'checkpoint_type': checkpoint_type,
                    'location_km': random.uniform(0.1, 2.0),
                    'measurement_timestamp': measurement_time,
                    'sensor_readings': sensor_readings,
                    'thickness_mm': random.uniform(2.5, 15.0) if checkpoint_type == CheckpointType.DIMENSIONAL_CHECK else None,
                    'width_mm': random.uniform(1180, 1520) if checkpoint_type == CheckpointType.DIMENSIONAL_CHECK else None,
                    'temperature_c': random.uniform(1100, 1280) if checkpoint_type == CheckpointType.TEMPERATURE_MEASUREMENT else None,
                    'weight_kg': random.uniform(4800, 26000) if checkpoint_type == CheckpointType.WEIGHT_CHECK else None,
                    'chemical_analysis': self._generate_chemical_analysis() if checkpoint_type == CheckpointType.CHEMICAL_ANALYSIS else {},
                    'yield_strength_mpa': random.randint(280, 650) if checkpoint_type == CheckpointType.MECHANICAL_TEST else None,
                    'tensile_strength_mpa': random.randint(420, 750) if checkpoint_type == CheckpointType.MECHANICAL_TEST else None,
                    'hardness_hv': random.randint(160, 290) if checkpoint_type == CheckpointType.MECHANICAL_TEST else None,
                    'elongation_percent': random.uniform(18, 32) if checkpoint_type == CheckpointType.MECHANICAL_TEST else None,
                    'quality_score': random.uniform(88, 99.8),
                    'pass_fail_status': random.choice(["pass"] * 9 + ["fail"]),
                    'deviation_from_spec': self._generate_deviation_data(),
                    'equipment_id': f"EQ-{random.randint(1, 100):03d}",
                    'operator_id': f"OP-{random.randint(1, 200):03d}",
                    'confidence_level': random.uniform(92, 99.5),
                    'calibration_date': self.fake.date_time_between(start_date='-6m', end_date='-1d'),
                    'created_at': measurement_time
                }
                checkpoints.append(checkpoint)
                
            self.db.quality_checkpoints.insert_many(checkpoints)
            checkpoints_inserted += len(checkpoints)
            
            if checkpoints_inserted % 10000 == 0:
                logger.info(f"Inserted {checkpoints_inserted} quality checkpoints...")
                
        logger.info(f"Inserted {checkpoints_inserted} total quality checkpoints")
        
    def seed_defects(self, count: int, facility_ids: List[ObjectId], 
                    line_ids: List[ObjectId], batch_ids: List[ObjectId]):
        """Generate and insert defect documents"""
        logger.info(f"Seeding {count} defects...")
        
        defects = []
        for i in range(count):
            facility_id = random.choice(facility_ids)
            line_id = random.choice(line_ids)
            batch_id = random.choice(batch_ids)
            
            defect_type = random.choice(list(DefectType))
            defect_subtype = random.choice(self.defect_subtypes[defect_type])
            
            detection_time = self.fake.date_time_between(start_date='-1y', end_date='now')
            
            # Severity influences other characteristics
            severity = random.choice([DefectSeverity.MINOR] * 4 + [DefectSeverity.MAJOR] * 2 + [DefectSeverity.CRITICAL])
            
            defect = {
                '_id': ObjectId(),
                'facility_id': facility_id,
                'production_line_id': line_id,
                'batch_id': batch_id,
                'checkpoint_id': ObjectId() if random.random() > 0.2 else None,  # Some defects detected at checkpoints
                'defect_id': f"DEF-{i+1:06d}",
                'defect_type': defect_type,
                'defect_subtype': defect_subtype,
                'detection_timestamp': detection_time,
                'location_km': random.uniform(0.1, 2.0),
                'location_width_mm': random.uniform(100, 1400) if random.random() > 0.5 else None,
                'severity': severity,
                'size_length_mm': self._generate_defect_size(severity, 'length'),
                'size_width_mm': self._generate_defect_size(severity, 'width'),
                'depth_mm': self._generate_defect_size(severity, 'depth') if defect_type == DefectType.SURFACE_DEFECT else None,
                'detection_method': random.choice(["visual_inspection", "automated_vision", "ultrasonic", "magnetic_particle"]),
                'automated_detection': random.choice([True] * 7 + [False] * 3),
                'ai_confidence': random.uniform(75, 98) if random.random() > 0.3 else None,
                'image_path': f"/images/defects/{i+1:06d}.jpg" if random.random() > 0.4 else None,
                'image_analysis': self._generate_image_analysis() if random.random() > 0.6 else {},
                'probable_cause': random.choice([
                    "roll_wear", "temperature_variation", "material_segregation", 
                    "equipment_misalignment", "contamination", "improper_cooling"
                ]) if random.random() > 0.3 else None,
                'process_correlation': self._generate_process_correlation(),
                'affected_area_m2': random.uniform(0.01, 2.5),
                'quality_impact_score': self._calculate_quality_impact(severity),
                'economic_impact_usd': self._calculate_economic_impact(severity),
                'corrective_action': self._generate_corrective_action(defect_type) if random.random() > 0.2 else None,
                'resolution_timestamp': detection_time + timedelta(hours=random.uniform(1, 48)) if random.random() > 0.3 else None,
                'resolved_by': self.fake.name() if random.random() > 0.3 else None,
                'material_disposition': random.choice(["accept", "rework", "scrap"]) if severity != DefectSeverity.COSMETIC else "accept",
                'customer_notification_required': severity in [DefectSeverity.MAJOR, DefectSeverity.CRITICAL],
                'created_at': detection_time,
                'updated_at': detection_time + timedelta(hours=random.uniform(0.5, 24)) if random.random() > 0.4 else None
            }
            defects.append(defect)
            
        self.db.defects.insert_many(defects)
        logger.info(f"Inserted {len(defects)} defects")
        
    def seed_test_results(self, count: int, facility_ids: List[ObjectId], 
                         batch_ids: List[ObjectId], product_ids: List[ObjectId]):
        """Generate and insert test result documents"""
        logger.info(f"Seeding {count} test results...")
        
        test_results = []
        for i in range(count):
            facility_id = random.choice(facility_ids)
            batch_id = random.choice(batch_ids)
            product_id = random.choice(product_ids)
            
            test_method = random.choice(list(TestMethod))
            test_date = self.fake.date_time_between(start_date='-1y', end_date='now')
            
            # Generate test results based on method
            results = self._generate_test_results(test_method)
            spec_limits = self._generate_specification_limits(test_method)
            
            test_result = {
                '_id': ObjectId(),
                'facility_id': facility_id,
                'batch_id': batch_id,
                'product_id': product_id,
                'test_id': f"TEST-{i+1:06d}",
                'test_method': test_method,
                'test_standard': random.choice(['ASTM E8', 'ISO 6892', 'EN 10025', 'JIS Z2201']),
                'test_date': test_date,
                'laboratory': random.choice(['Central Lab', 'Quality Lab A', 'Quality Lab B', 'External Lab']),
                'technician': self.fake.name(),
                'sample_location': random.choice(['head_end', 'middle', 'tail_end', 'edge', 'center']),
                'sample_preparation': "Standard preparation as per test method specification",
                'test_temperature_c': random.uniform(20, 25),
                'test_environment': {
                    'humidity_percent': random.uniform(45, 65),
                    'atmospheric_pressure_kpa': random.uniform(98, 102)
                },
                'test_results': results,
                'specification_limits': spec_limits,
                'pass_fail_status': self._determine_pass_fail(results, spec_limits),
                'measurement_uncertainty': self._generate_measurement_uncertainty(test_method),
                'confidence_interval': self._generate_confidence_intervals(results),
                'compliant_standards': random.sample(['ASTM', 'ISO', 'EN', 'JIS'], k=random.randint(1, 3)),
                'deviations': self._generate_test_deviations(results, spec_limits),
                'certificate_number': f"CERT-{i+1:06d}" if random.random() > 0.3 else None,
                'certificate_issued': random.choice([True, False]),
                'certificate_valid_until': test_date + timedelta(days=365) if random.random() > 0.2 else None,
                'created_at': test_date,
                'updated_at': None
            }
            test_results.append(test_result)
            
        self.db.test_results.insert_many(test_results)
        logger.info(f"Inserted {len(test_results)} test results")
        
    def seed_customer_specifications(self, count: int, product_ids: List[ObjectId]):
        """Generate and insert customer specification documents"""
        logger.info(f"Seeding {count} customer specifications...")
        
        customers = [
            "Ford Motor Company", "General Motors", "Tesla", "BMW Group", "Toyota",
            "Caterpillar", "John Deere", "Hyundai Heavy Industries", "Samsung Heavy Industries",
            "Maersk", "Shell", "ExxonMobil", "General Electric", "Siemens", "ABB"
        ]
        
        specifications = []
        for i in range(count):
            customer = random.choice(customers)
            customer_code = f"CUST-{i+1:03d}"
            
            applicable_products = random.sample(product_ids, k=random.randint(1, 5))
            
            spec = {
                '_id': ObjectId(),
                'customer_name': customer,
                'customer_code': customer_code,
                'product_family': random.choice(["automotive_steel", "structural_steel", "energy_steel", "marine_steel"]),
                'applicable_products': applicable_products,
                'specification_name': f"{customer} Steel Specification v{random.randint(1, 5)}",
                'specification_version': f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
                'effective_date': self.fake.date_time_between(start_date='-2y', end_date='now'),
                'expiry_date': self.fake.date_time_between(start_date='now', end_date='+3y'),
                'chemical_requirements': self._generate_chemical_requirements(),
                'mechanical_requirements': self._generate_mechanical_requirements(),
                'dimensional_tolerances': self._generate_dimensional_tolerances(),
                'surface_requirements': {
                    'surface_finish': random.choice(["mill_scale", "pickled", "oiled", "galvanized"]),
                    'surface_quality': random.choice(["commercial", "drawing", "structural"]),
                    'defect_limits': "As per specification document"
                },
                'required_tests': random.sample(list(TestMethod), k=random.randint(2, 5)),
                'sampling_plan': {
                    'sample_frequency': random.choice(["per_coil", "per_batch", "per_heat"]),
                    'sample_size': random.randint(1, 5),
                    'test_locations': random.choice(["head_tail", "random", "specified_positions"])
                },
                'acceptance_criteria': {
                    'quality_level': "AQL 2.5",
                    'pass_rate_required': random.uniform(95, 99),
                    'critical_defect_tolerance': 0,
                    'major_defect_tolerance': random.randint(0, 2)
                },
                'quality_level': random.choice(["premium", "standard", "commercial"]),
                'certificate_required': True,
                'test_report_required': True,
                'traceability_required': True,
                'is_active': True,
                'approval_status': "approved",
                'approved_by': self.fake.name(),
                'created_at': datetime.utcnow(),
                'updated_at': None
            }
            specifications.append(spec)
            
        self.db.customer_specifications.insert_many(specifications)
        logger.info(f"Inserted {len(specifications)} customer specifications")
        
    def create_indexes(self):
        """Create indexes as defined in the schema"""
        logger.info("Creating database indexes...")
        
        for collection_name, collection_schema in database_schema.collections.items():
            collection = self.db[collection_name]
            for index_def in collection_schema.indexes:
                try:
                    # Convert direction enum values to proper MongoDB index direction integers
                    index_keys = []
                    for field, direction in index_def.keys.items():
                        if hasattr(direction, 'value'):
                            # Handle IndexDirection enum
                            dir_value = direction.value
                            if dir_value == "1":
                                dir_value = 1
                            elif dir_value == "-1":
                                dir_value = -1
                        else:
                            # Handle raw string/int values
                            dir_value = direction
                            if dir_value == "1":
                                dir_value = 1
                            elif dir_value == "-1":
                                dir_value = -1
                        index_keys.append((field, dir_value))
                    
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
        
    def _generate_sensor_readings(self, checkpoint_type: CheckpointType) -> Dict[str, float]:
        """Generate realistic sensor readings based on checkpoint type"""
        if checkpoint_type == CheckpointType.TEMPERATURE_MEASUREMENT:
            return {
                'pyrometer_1': random.uniform(1100, 1280),
                'pyrometer_2': random.uniform(1100, 1280),
                'ambient_temp': random.uniform(35, 55)
            }
        elif checkpoint_type == CheckpointType.DIMENSIONAL_CHECK:
            return {
                'thickness_gauge': random.uniform(2.5, 15.0),
                'width_gauge': random.uniform(1180, 1520),
                'flatness_meter': random.uniform(-2.0, 2.0)
            }
        elif checkpoint_type == CheckpointType.CHEMICAL_ANALYSIS:
            return {element: random.uniform(min_val, max_val) 
                   for element, (min_val, max_val) in list(self.chemical_elements.items())[:5]}
        else:
            return {
                'sensor_1': random.uniform(0, 100),
                'sensor_2': random.uniform(0, 100),
                'sensor_3': random.uniform(0, 100)
            }
            
    def _generate_chemical_analysis(self) -> Dict[str, float]:
        """Generate chemical analysis results"""
        return {element: round(random.uniform(min_val, max_val), 3)
               for element, (min_val, max_val) in self.chemical_elements.items()}
        
    def _generate_deviation_data(self) -> Dict[str, float]:
        """Generate deviation from specification data"""
        return {
            'thickness_deviation_mm': random.uniform(-0.1, 0.1),
            'width_deviation_mm': random.uniform(-5, 5),
            'strength_deviation_mpa': random.uniform(-10, 10)
        }
        
    def _generate_defect_size(self, severity: DefectSeverity, dimension: str) -> Optional[float]:
        """Generate defect size based on severity"""
        if dimension == 'length':
            if severity == DefectSeverity.MINOR:
                return random.uniform(1, 10)
            elif severity == DefectSeverity.MAJOR:
                return random.uniform(10, 50)
            else:  # CRITICAL
                return random.uniform(50, 200)
        elif dimension == 'width':
            if severity == DefectSeverity.MINOR:
                return random.uniform(0.5, 5)
            elif severity == DefectSeverity.MAJOR:
                return random.uniform(5, 25)
            else:  # CRITICAL
                return random.uniform(25, 100)
        else:  # depth
            if severity == DefectSeverity.MINOR:
                return random.uniform(0.01, 0.1)
            elif severity == DefectSeverity.MAJOR:
                return random.uniform(0.1, 0.5)
            else:  # CRITICAL
                return random.uniform(0.5, 2.0)
                
    def _generate_image_analysis(self) -> Dict[str, Any]:
        """Generate AI image analysis results"""
        return {
            'defect_area_pixels': random.randint(100, 50000),
            'defect_intensity': random.uniform(0.1, 0.9),
            'edge_sharpness': random.uniform(0.3, 1.0),
            'classification_confidence': random.uniform(0.7, 0.98)
        }
        
    def _generate_process_correlation(self) -> Dict[str, Any]:
        """Generate process parameter correlation data"""
        return {
            'temperature_at_defect': random.uniform(1100, 1300),
            'rolling_force_kn': random.uniform(8000, 16000),
            'speed_mpm': random.uniform(6, 15),
            'cooling_rate': random.uniform(8, 35)
        }
        
    def _calculate_quality_impact(self, severity: DefectSeverity) -> float:
        """Calculate quality impact score based on severity"""
        if severity == DefectSeverity.MINOR:
            return random.uniform(5, 20)
        elif severity == DefectSeverity.MAJOR:
            return random.uniform(20, 60)
        else:  # CRITICAL
            return random.uniform(60, 95)
            
    def _calculate_economic_impact(self, severity: DefectSeverity) -> float:
        """Calculate economic impact in USD"""
        if severity == DefectSeverity.MINOR:
            return random.uniform(100, 1000)
        elif severity == DefectSeverity.MAJOR:
            return random.uniform(1000, 10000)
        else:  # CRITICAL
            return random.uniform(10000, 100000)
            
    def _generate_corrective_action(self, defect_type: DefectType) -> str:
        """Generate appropriate corrective action based on defect type"""
        actions = {
            DefectType.SURFACE_DEFECT: [
                "Roll maintenance scheduled", "Surface cleaning intensified", 
                "Cooling system adjustment", "Scale removal optimization"
            ],
            DefectType.DIMENSIONAL_DEFECT: [
                "Gauge calibration", "Roll gap adjustment", "Speed control optimization",
                "Temperature profile adjustment"
            ],
            DefectType.CHEMICAL_DEFECT: [
                "Raw material quality check", "Alloy addition adjustment",
                "Melting parameters review", "Contamination source investigation"
            ],
            DefectType.MECHANICAL_DEFECT: [
                "Heat treatment optimization", "Cooling rate adjustment",
                "Chemical composition review", "Processing parameter adjustment"
            ],
            DefectType.COATING_DEFECT: [
                "Coating line maintenance", "Surface preparation improvement",
                "Coating material quality check", "Application parameters adjustment"
            ]
        }
        return random.choice(actions[defect_type])
        
    def _generate_test_results(self, test_method: TestMethod) -> Dict[str, float]:
        """Generate test results based on test method"""
        if test_method == TestMethod.TENSILE_TEST:
            return {
                'yield_strength_mpa': random.randint(250, 690),
                'tensile_strength_mpa': random.randint(400, 800),
                'elongation_percent': random.uniform(15, 35),
                'reduction_of_area_percent': random.uniform(40, 70)
            }
        elif test_method == TestMethod.HARDNESS_TEST:
            return {
                'hardness_hv': random.randint(150, 350),
                'hardness_hb': random.randint(140, 320),
                'hardness_hrc': random.randint(15, 45)
            }
        elif test_method == TestMethod.IMPACT_TEST:
            return {
                'impact_energy_j': random.uniform(20, 250),
                'lateral_expansion_mm': random.uniform(0.5, 2.5),
                'fracture_appearance_percent': random.uniform(60, 95)
            }
        else:
            return {
                'test_value_1': random.uniform(100, 1000),
                'test_value_2': random.uniform(50, 500),
                'test_value_3': random.uniform(10, 100)
            }
            
    def _generate_specification_limits(self, test_method: TestMethod) -> Dict[str, Dict[str, float]]:
        """Generate specification limits for test method"""
        if test_method == TestMethod.TENSILE_TEST:
            return {
                'yield_strength_mpa': {'min': 250, 'max': 700},
                'tensile_strength_mpa': {'min': 400, 'max': 850},
                'elongation_percent': {'min': 15, 'max': 40}
            }
        elif test_method == TestMethod.HARDNESS_TEST:
            return {
                'hardness_hv': {'min': 140, 'max': 360},
                'hardness_hb': {'min': 130, 'max': 330}
            }
        else:
            return {
                'test_value_1': {'min': 90, 'max': 1100},
                'test_value_2': {'min': 45, 'max': 550}
            }
            
    def _determine_pass_fail(self, results: Dict[str, float], 
                           spec_limits: Dict[str, Dict[str, float]]) -> str:
        """Determine if test results pass or fail specifications"""
        for param, value in results.items():
            if param in spec_limits:
                limits = spec_limits[param]
                if 'min' in limits and value < limits['min']:
                    return "fail"
                if 'max' in limits and value > limits['max']:
                    return "fail"
        return "pass"
        
    def _generate_measurement_uncertainty(self, test_method: TestMethod) -> Dict[str, float]:
        """Generate measurement uncertainty values"""
        if test_method == TestMethod.TENSILE_TEST:
            return {
                'yield_strength_uncertainty_mpa': random.uniform(2, 8),
                'tensile_strength_uncertainty_mpa': random.uniform(3, 10),
                'elongation_uncertainty_percent': random.uniform(0.5, 2.0)
            }
        else:
            return {
                'measurement_uncertainty_percent': random.uniform(1, 5)
            }
            
    def _generate_confidence_intervals(self, results: Dict[str, float]) -> Dict[str, List[float]]:
        """Generate confidence intervals for test results"""
        intervals = {}
        for param, value in results.items():
            uncertainty = value * random.uniform(0.02, 0.05)  # 2-5% uncertainty
            intervals[param] = [value - uncertainty, value + uncertainty]
        return intervals
        
    def _generate_test_deviations(self, results: Dict[str, float], 
                                spec_limits: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Generate deviations from specifications"""
        deviations = []
        for param, value in results.items():
            if param in spec_limits:
                limits = spec_limits[param]
                if 'min' in limits and value < limits['min']:
                    deviations.append({
                        'parameter': param,
                        'deviation_type': 'below_minimum',
                        'deviation_value': limits['min'] - value,
                        'severity': 'major'
                    })
                elif 'max' in limits and value > limits['max']:
                    deviations.append({
                        'parameter': param,
                        'deviation_type': 'above_maximum', 
                        'deviation_value': value - limits['max'],
                        'severity': 'major'
                    })
        return deviations
        
    def _generate_chemical_requirements(self) -> Dict[str, Dict[str, float]]:
        """Generate customer chemical requirements"""
        requirements = {}
        for element in random.sample(list(self.chemical_elements.keys()), k=random.randint(4, 8)):
            min_val, max_val = self.chemical_elements[element]
            # Customer requirements are typically tighter than general ranges
            cust_min = random.uniform(min_val, min_val + (max_val - min_val) * 0.3)
            cust_max = random.uniform(max_val - (max_val - min_val) * 0.3, max_val)
            requirements[element] = {'min': round(cust_min, 3), 'max': round(cust_max, 3)}
        return requirements
        
    def _generate_mechanical_requirements(self) -> Dict[str, Dict[str, float]]:
        """Generate customer mechanical requirements"""
        return {
            'yield_strength_mpa': {'min': random.randint(300, 450), 'max': random.randint(500, 650)},
            'tensile_strength_mpa': {'min': random.randint(450, 550), 'max': random.randint(600, 750)},
            'elongation_percent': {'min': random.uniform(18, 25), 'max': random.uniform(30, 40)},
            'hardness_hv': {'min': random.randint(160, 200), 'max': random.randint(250, 320)}
        }
        
    def _generate_dimensional_tolerances(self) -> Dict[str, Dict[str, float]]:
        """Generate customer dimensional tolerances"""
        return {
            'thickness_tolerance_mm': {'min': -0.1, 'max': 0.1},
            'width_tolerance_mm': {'min': -5.0, 'max': 5.0},
            'length_tolerance_mm': {'min': -10.0, 'max': 10.0},
            'flatness_tolerance_mm': {'min': -2.0, 'max': 2.0}
        }
        
    def _validate_referential_integrity(self):
        """Validate referential integrity across collections"""
        logger.info("Checking referential integrity...")
        
        # Check facility references
        facility_ids = set(doc['_id'] for doc in self.db.facilities.find({}, {'_id': 1}))
        
        invalid_line_facilities = self.db.production_lines.count_documents({
            'facility_id': {'$nin': list(facility_ids)}
        })
        if invalid_line_facilities > 0:
            raise ValueError(f"Found {invalid_line_facilities} production lines with invalid facility references")
            
        # Check production line references
        line_ids = set(doc['_id'] for doc in self.db.production_lines.find({}, {'_id': 1}))
        
        invalid_batch_lines = self.db.production_batches.count_documents({
            'production_line_id': {'$nin': list(line_ids)}
        })
        if invalid_batch_lines > 0:
            raise ValueError(f"Found {invalid_batch_lines} batches with invalid production line references")
            
        logger.info("Referential integrity check passed")
        
    def _validate_data_distribution(self):
        """Validate data distribution patterns"""
        logger.info("Checking data distribution...")
        
        # Check quality grade distribution
        grade_dist = {}
        for doc in self.db.production_batches.find({}, {'quality_grade': 1}):
            grade = doc['quality_grade']
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
            
        total_batches = sum(grade_dist.values())
        if total_batches > 0:
            prime_ratio = grade_dist.get('prime', 0) / total_batches
            if prime_ratio < 0.5:  # Expect majority to be prime quality
                logger.warning(f"Prime quality ratio is low: {prime_ratio:.2%}")
                
        # Check defect severity distribution
        severity_dist = {}
        for doc in self.db.defects.find({}, {'severity': 1}):
            severity = doc['severity']
            severity_dist[severity] = severity_dist.get(severity, 0) + 1
            
        total_defects = sum(severity_dist.values())
        if total_defects > 0:
            critical_ratio = severity_dist.get('critical', 0) / total_defects
            if critical_ratio > 0.1:  # Critical defects should be rare
                logger.warning(f"Critical defect ratio is high: {critical_ratio:.2%}")
                
        logger.info("Data distribution check completed")


def seed_database(connection_string: str = "mongodb://localhost:27017", 
                 num_records: Optional[Dict[str, int]] = None):
    """
    Seed the steel production database with realistic sample data
    
    Args:
        connection_string: MongoDB connection string
        num_records: Dictionary specifying number of records per collection
    """
    seeder = SteelProductionSeeder(connection_string)
    
    # Clear existing data
    seeder.clear_database()
    
    # Create indexes first (before seeding data for better performance)
    seeder.create_indexes()
    
    # Seed with sample data
    seeder.seed_all_collections(num_records)
    
    # Validate the seeded data
    seeder.validate_seed_data()
    
    return seeder


if __name__ == "__main__":
    import os
    
    # Get connection string from environment or use default
    connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Default record counts for a substantial but manageable dataset
    record_counts = {
        'facilities': 8,              # Global facilities
        'production_lines': 40,       # 5 lines per facility average
        'products': 25,               # Product catalog
        'production_batches': 500,    # Recent production batches
        'quality_checkpoints': 50000, # High-volume sensor data
        'defects': 2500,             # Quality issues detected
        'test_results': 5000,         # Laboratory test results
        'customer_specifications': 15 # Customer quality specs
    }
    
    try:
        print(f"🔥 Seeding database '{database_schema.database_name}'...")
        seeder = seed_database(connection_string, record_counts)
        print(f"✅ Successfully seeded database '{database_schema.database_name}'")
        print("📊 Database ready for use with realistic steel production data!")
        
        # Verify indexes were created
        print("\n🗂️  Index verification:")
        for collection_name in database_schema.collections.keys():
            indexes = list(seeder.db[collection_name].list_indexes())
            print(f"  • {collection_name}: {len(indexes)} indexes")
        
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        raise