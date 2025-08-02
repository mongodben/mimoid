"""
1Password Events Database Seeder
Generates realistic security event data for testing and development
"""

import random
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker
from pymongo import MongoClient

from mimoid import DatabaseSeeder
from db_schema import (
    OnePasswordEventsDatabase,
    UserSchema, DeviceSchema, VaultSchema, ItemSchema,
    AuditEventSchema, ItemUsageSchema, SignInAttemptSchema,
    LocationSchema, ClientSchema, SessionSchema, UserRefSchema, DetailsSchema
)

class OnePasswordSeeder(DatabaseSeeder):
    def __init__(self, connection_string: str):
        from db_schema import database_schema
        super().__init__(connection_string, database_schema)
        self.fake = Faker()
        Faker.seed(42)
        random.seed(42)
        
        # Configuration
        self.num_users = 500
        self.num_devices = 1200
        self.num_vaults = 150
        self.num_items = 5000
        self.num_audit_events = 50000
        self.num_item_usages = 25000
        self.num_sign_in_attempts = 15000
        
        # 1Password-specific data
        self.app_names = [
            "1Password 8", "1Password 7", "1Password Extension", "1Password CLI",
            "1Password X", "1Password Safari Extension", "1Password Chrome Extension",
            "1Password Firefox Extension", "1Password Edge Extension", "1Password Desktop",
            "1Password iOS", "1Password Android", "1Password macOS", "1Password Windows"
        ]
        
        self.os_names = [
            "macOS", "Windows", "iOS", "Android", "Linux", "Chrome OS"
        ]
        
        self.platforms = [
            "Chrome", "Safari", "Firefox", "Edge", "Desktop App", "Mobile App"
        ]
        
        self.item_categories = [
            "Login", "Credit Card", "Secure Note", "Identity", "Password",
            "Software License", "Bank Account", "Database", "Driver License",
            "Passport", "Server", "Email Account", "API Credential", "SSH Key"
        ]
        
        self.vault_types = [
            "Personal", "Shared", "Team", "Admin", "Development", "Production",
            "Marketing", "Finance", "HR", "IT Security", "Customer Support"
        ]
        
        # Cache for relationships
        self.users = []
        self.devices = []
        self.vaults = []
        self.items = []
        self.sessions = []

    def get_database(self):
        """Get database connection"""
        client = MongoClient(self.connection_string)
        return client[self.database_schema.database_name], client

    def generate_uuid(self) -> str:
        """Generate 1Password-style UUID"""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        return ''.join(random.choices(chars, k=26))

    def generate_location(self) -> LocationSchema:
        """Generate realistic geolocation data"""
        locations = [
            {"city": "New York", "country": "US", "region": "New York", "lat": 40.7128, "lng": -74.0060},
            {"city": "London", "country": "GB", "region": "England", "lat": 51.5074, "lng": -0.1278},
            {"city": "Toronto", "country": "CA", "region": "Ontario", "lat": 43.6532, "lng": -79.3832},
            {"city": "Sydney", "country": "AU", "region": "New South Wales", "lat": -33.8688, "lng": 151.2093},
            {"city": "San Francisco", "country": "US", "region": "California", "lat": 37.7749, "lng": -122.4194},
            {"city": "Berlin", "country": "DE", "region": "Berlin", "lat": 52.5200, "lng": 13.4050},
            {"city": "Tokyo", "country": "JP", "region": "Tokyo", "lat": 35.6762, "lng": 139.6503},
            {"city": "Mumbai", "country": "IN", "region": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
            {"city": "São Paulo", "country": "BR", "region": "São Paulo", "lat": -23.5505, "lng": -46.6333},
            {"city": "Amsterdam", "country": "NL", "region": "North Holland", "lat": 52.3676, "lng": 4.9041},
        ]
        
        loc_data = random.choice(locations)
        return LocationSchema(
            city=loc_data["city"],
            country=loc_data["country"],
            region=loc_data["region"],
            latitude=loc_data["lat"] + random.uniform(-0.1, 0.1),
            longitude=loc_data["lng"] + random.uniform(-0.1, 0.1)
        )

    def generate_client(self) -> ClientSchema:
        """Generate realistic client information"""
        return ClientSchema(
            app_name=random.choice(self.app_names),
            app_version=f"{random.randint(8, 12)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
            ip_address=self.fake.ipv4(),
            os_name=random.choice(self.os_names),
            os_version=f"{random.randint(10, 14)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            platform_name=random.choice(self.platforms),
            platform_version=f"{random.randint(90, 120)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"
        )

    def seed_users(self) -> None:
        """Generate user data"""
        print("Seeding users...")
        users_data = []
        
        for _ in range(self.num_users):
            user = UserSchema(
                uuid=self.generate_uuid(),
                email=self.fake.email(),
                name=self.fake.name(),
                is_active=random.choice([True, True, True, False]),  # 75% active
                created_at=self.fake.date_time_between(start_date='-2y', end_date='now'),
                last_seen=self.fake.date_time_between(start_date='-30d', end_date='now') if random.random() > 0.1 else None,
                role=random.choice(["admin", "member", "guest", "owner"]),
                custom_fields={
                    "department": random.choice(["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]),
                    "employee_id": f"EMP{random.randint(1000, 9999)}",
                    "security_clearance": random.choice(["basic", "elevated", "admin"])
                }
            )
            users_data.append(user.model_dump())
            self.users.append(user)
        
        db, client = self.get_database()
        db.users.insert_many(users_data, ordered=False)
        client.close()
        print(f"Inserted {len(users_data)} users")

    def seed_devices(self) -> None:
        """Generate device data"""
        print("Seeding devices...")
        devices_data = []
        
        for _ in range(self.num_devices):
            user = random.choice(self.users)
            device = DeviceSchema(
                uuid=self.generate_uuid(),
                user_uuid=user.uuid,
                name=f"{self.fake.first_name()}'s {random.choice(['MacBook', 'iPhone', 'iPad', 'Windows PC', 'Android'])}",
                os_name=random.choice(self.os_names),
                os_version=f"{random.randint(10, 14)}.{random.randint(0, 9)}",
                platform=random.choice(self.platforms),
                is_trusted=random.choice([True, True, True, False]),  # 75% trusted
                registered_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                last_used=self.fake.date_time_between(start_date='-7d', end_date='now') if random.random() > 0.2 else None,
                custom_fields={
                    "device_model": self.fake.word().title(),
                    "serial_number": self.fake.bothify(text='###-???-####').upper(),
                    "managed": random.choice([True, False])
                }
            )
            devices_data.append(device.model_dump())
            self.devices.append(device)
        
        db, client = self.get_database()
        db.devices.insert_many(devices_data, ordered=False)
        client.close()
        print(f"Inserted {len(devices_data)} devices")

    def seed_vaults(self) -> None:
        """Generate vault data"""
        print("Seeding vaults...")
        vaults_data = []
        
        for _ in range(self.num_vaults):
            creator = random.choice(self.users)
            vault_type = random.choice(self.vault_types)
            vault = VaultSchema(
                uuid=self.generate_uuid(),
                name=f"{vault_type} Vault - {self.fake.company()}",
                description=f"Vault for {vault_type.lower()} access and credentials",
                is_shared=random.choice([True, False]),
                created_by=creator.uuid,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                permissions=[
                    {
                        "user_uuid": random.choice(self.users).uuid,
                        "role": random.choice(["owner", "admin", "member", "viewer"]),
                        "granted_at": self.fake.date_time_between(start_date='-6m', end_date='now')
                    } for _ in range(random.randint(1, 5))
                ],
                custom_fields={
                    "vault_type": vault_type,
                    "compliance_level": random.choice(["standard", "enhanced", "maximum"]),
                    "auto_lock": random.choice([True, False])
                }
            )
            vaults_data.append(vault.model_dump())
            self.vaults.append(vault)
        
        db, client = self.get_database()
        db.vaults.insert_many(vaults_data, ordered=False)
        client.close()
        print(f"Inserted {len(vaults_data)} vaults")

    def seed_items(self) -> None:
        """Generate item data"""
        print("Seeding items...")
        items_data = []
        
        for _ in range(self.num_items):
            vault = random.choice(self.vaults)
            creator = random.choice(self.users)
            category = random.choice(self.item_categories)
            
            item = ItemSchema(
                uuid=self.generate_uuid(),
                vault_uuid=vault.uuid,
                title=f"{category} - {self.fake.company() if category == 'Login' else self.fake.word().title()}",
                category=category,
                created_by=creator.uuid,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-30d', end_date='now'),
                version=random.randint(1, 10),
                is_trashed=random.choice([False, False, False, True]),  # 25% trashed
                tags=[self.fake.word() for _ in range(random.randint(0, 3))],
                custom_fields={
                    "website": self.fake.url() if category == "Login" else None,
                    "last_modified_by": random.choice(self.users).uuid,
                    "security_score": random.randint(1, 100),
                    "expiry_date": self.fake.future_datetime(end_date='+1y') if category in ["Credit Card", "Identity"] else None
                }
            )
            items_data.append(item.model_dump())
            self.items.append(item)
        
        db, client = self.get_database()
        db.items.insert_many(items_data, ordered=False)
        client.close()
        print(f"Inserted {len(items_data)} items")

    def seed_audit_events(self) -> None:
        """Generate audit event data"""
        print("Seeding audit events...")
        audit_events_data = []
        
        actions = [
            "create", "update", "delete", "view", "export", "share", "grant", "revoke",
            "activate", "join", "leave", "role", "verify", "suspend", "begin", "complete",
            "cancel", "hide", "unhide", "replace", "purge", "unknown"
        ]
        object_types = [
            "user", "device", "vault", "item", "group", "invite", "account", "sso"
        ]
        
        for _ in range(self.num_audit_events):
            actor = random.choice(self.users)
            target_object = random.choice(object_types)
            
            # Generate related session
            device = random.choice([d for d in self.devices if d.user_uuid == actor.uuid] or self.devices)
            session = SessionSchema(
                uuid=self.generate_uuid(),
                device_uuid=device.uuid,
                ip=self.fake.ipv4(),
                login_time=self.fake.date_time_between(start_date='-1d', end_date='now')
            )
            self.sessions.append(session)
            
            event = AuditEventSchema(
                uuid=self.generate_uuid(),
                timestamp=self.fake.date_time_between(start_date='-30d', end_date='now'),
                action=random.choice(actions),
                object_type=target_object,
                object_uuid=self.generate_uuid(),
                actor_uuid=actor.uuid,
                aux_id=random.randint(1, 1000) if random.random() > 0.7 else None,
                aux_info=self.fake.sentence() if random.random() > 0.8 else None,
                aux_uuid=self.generate_uuid() if random.random() > 0.9 else None,
                location=self.generate_location(),
                session=session
            )
            audit_events_data.append(event.model_dump())
        
        # Insert in batches
        batch_size = 1000
        db, client = self.get_database()
        for i in range(0, len(audit_events_data), batch_size):
            batch = audit_events_data[i:i + batch_size]
            db.audit_events.insert_many(batch, ordered=False)
        client.close()
        
        print(f"Inserted {len(audit_events_data)} audit events")

    def seed_item_usages(self) -> None:
        """Generate item usage data"""
        print("Seeding item usages...")
        usage_data = []
        
        usage_actions = [
            "fill", "reveal", "secure-copy", "export", "share",
            "enter-item-edit-mode", "server-fetch", "select-sso-provider"
        ]
        
        for _ in range(self.num_item_usages):
            item = random.choice(self.items)
            user = random.choice(self.users)
            
            usage = ItemUsageSchema(
                uuid=self.generate_uuid(),
                timestamp=self.fake.date_time_between(start_date='-30d', end_date='now'),
                action=random.choice(usage_actions),
                item_uuid=item.uuid,
                vault_uuid=item.vault_uuid,
                user=UserRefSchema(
                    uuid=user.uuid,
                    email=user.email,
                    name=user.name
                ),
                client=self.generate_client(),
                location=self.generate_location(),
                used_version=random.randint(1, item.version)
            )
            usage_data.append(usage.model_dump())
        
        # Insert in batches
        batch_size = 1000
        db, client = self.get_database()
        for i in range(0, len(usage_data), batch_size):
            batch = usage_data[i:i + batch_size]
            db.item_usages.insert_many(batch, ordered=False)
        client.close()
        
        print(f"Inserted {len(usage_data)} item usages")

    def seed_sign_in_attempts(self) -> None:
        """Generate sign-in attempt data"""
        print("Seeding sign-in attempts...")
        attempts_data = []
        
        categories = [
            "success", "credentials_failed", "mfa_failed", "firewall_failed"
        ]
        
        attempt_types = [
            "credentials_ok", "mfa_ok", "password_secret_bad", "mfa_missing",
            "totp_bad", "ip_blocked", "country_blocked", "continent_blocked"
        ]
        
        for _ in range(self.num_sign_in_attempts):
            user = random.choice(self.users)
            category = random.choice(categories)
            
            # Determine type based on category
            if category == "success":
                attempt_type = random.choice(["credentials_ok", "mfa_ok"])
            elif category == "credentials_failed":
                attempt_type = random.choice(["password_secret_bad", "mfa_missing"])
            elif category == "mfa_failed":
                attempt_type = random.choice(["totp_bad", "totp_timeout", "duo_bad"])
            else:  # firewall_failed
                attempt_type = random.choice(["ip_blocked", "country_blocked", "continent_blocked"])
            
            attempt = SignInAttemptSchema(
                uuid=self.generate_uuid(),
                timestamp=self.fake.date_time_between(start_date='-30d', end_date='now'),
                category=category,
                type=attempt_type,
                target_user=UserRefSchema(
                    uuid=user.uuid,
                    email=user.email,
                    name=user.name
                ),
                session_uuid=self.generate_uuid() if category == "success" else None,
                client=self.generate_client(),
                location=self.generate_location(),
                country=random.choice(["US", "CA", "GB", "DE", "FR", "JP", "AU", "BR", "IN", "NL"]),
                details=DetailsSchema(
                    value=random.choice(["Europe", "Asia", "North America"]) if "blocked" in attempt_type else None
                ) if random.random() > 0.5 else None
            )
            attempts_data.append(attempt.model_dump())
        
        # Insert in batches
        batch_size = 1000
        db, client = self.get_database()
        for i in range(0, len(attempts_data), batch_size):
            batch = attempts_data[i:i + batch_size]
            db.sign_in_attempts.insert_many(batch, ordered=False)
        client.close()
        
        print(f"Inserted {len(attempts_data)} sign-in attempts")

    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None) -> None:
        """Main seeding method"""
        print(f"Starting database seeding for {self.database_schema.database_name}")
        
        # Create database and collections with indexes
        self.create_indexes()
        
        # Seed data in dependency order
        self.seed_users()
        self.seed_devices()
        self.seed_vaults()
        self.seed_items()
        self.seed_audit_events()
        self.seed_item_usages()
        self.seed_sign_in_attempts()
        
        print("Database seeding completed successfully!")

    def create_indexes(self) -> None:
        """Create indexes as defined in the schema"""
        client = MongoClient(self.connection_string)
        db = client[self.database_schema.database_name]
        
        for collection_name, collection_schema in self.database_schema.collections.items():
            collection = db[collection_name]
            for index_def in collection_schema.indexes:
                try:
                    collection.create_index(
                        [(field, direction.value if hasattr(direction, 'value') else direction) 
                         for field, direction in index_def.keys.items()],
                        name=index_def.name,
                        unique=index_def.unique,
                        sparse=index_def.sparse,
                        background=index_def.background
                    )
                except Exception as e:
                    if "duplicate key" not in str(e).lower():
                        print(f"Warning: Could not create index {index_def.name}: {e}")
        
        client.close()

    def clear_database(self) -> None:
        """Clear all collections"""
        client = MongoClient(self.connection_string)
        db = client[self.database_schema.database_name]
        
        for collection_name in self.database_schema.collections.keys():
            db[collection_name].delete_many({})
        
        client.close()

    def validate_seed_data(self) -> Dict[str, Any]:
        """Validate the seeded data"""
        return self.validate_data()

    def validate_data(self) -> Dict[str, Any]:
        """Validate the seeded data"""
        print("Validating seeded data...")
        
        validation_results = {}
        
        db, client = self.get_database()
        
        # Count documents in each collection
        for collection_name in self.database_schema.collections:
            count = db[collection_name].count_documents({})
            validation_results[collection_name] = {
                "count": count,
                "expected_min": getattr(self, f"num_{collection_name.rstrip('s')}", 0),
                "status": "✓" if count > 0 else "✗"
            }
        
        # Check referential integrity
        integrity_checks = {
            "devices_with_valid_users": db.devices.count_documents({
                "user_uuid": {"$in": [u.uuid for u in self.users]}
            }),
            "items_with_valid_vaults": db.items.count_documents({
                "vault_uuid": {"$in": [v.uuid for v in self.vaults]}
            }),
            "audit_events_with_valid_actors": db.audit_events.count_documents({
                "actor_uuid": {"$in": [u.uuid for u in self.users]}
            })
        }
        
        validation_results["integrity_checks"] = integrity_checks
        
        client.close()
        return validation_results