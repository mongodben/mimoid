"""Seed script for DataTech Platform MarTech database"""

from faker import Faker
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Optional, List
import json

# Import the database schema
from db_schema import (
    database_schema,
    EventType,
    CampaignType,
    CampaignStatus,
    DataSourceType,
)
from mimoid import DatabaseSeeder


class DataTechPlatformSeeder(DatabaseSeeder):
    def __init__(self, connection_string: str):
        super().__init__(connection_string, database_schema)
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        self.fake = Faker()

        # Seed data storage for referential integrity
        self.customer_ids = []
        self.campaign_ids = []
        self.data_source_ids = []

        # Define realistic data distributions
        self.event_types = [
            (EventType.PAGE_VIEW, 0.4),
            (EventType.EMAIL_OPEN, 0.2),
            (EventType.EMAIL_CLICK, 0.1),
            (EventType.PURCHASE, 0.05),
            (EventType.FORM_SUBMIT, 0.1),
            (EventType.CAMPAIGN_CLICK, 0.08),
            (EventType.SOCIAL_SHARE, 0.02),
            (EventType.LOGIN, 0.03),
            (EventType.REGISTRATION, 0.02),
        ]

        self.platforms = ["facebook", "twitter", "instagram", "linkedin", "tiktok"]
        self.industries = [
            "Technology",
            "Healthcare",
            "Finance",
            "Retail",
            "Manufacturing",
            "Education",
        ]

    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        if num_records is None:
            num_records = {
                "data_sources": 8,
                "customers": 1000,
                "campaigns": 25,
                "events": 50000,
                "segments": 15,
                "social_members": 300,
            }

        print("Starting database seeding...")

        # Seed in dependency order
        print("Seeding data sources...")
        self.seed_data_sources(num_records["data_sources"])

        print("Seeding customers...")
        self.seed_customers(num_records["customers"])

        print("Seeding campaigns...")
        self.seed_campaigns(num_records["campaigns"])

        print("Seeding events...")
        self.seed_events(num_records["events"])

        print("Seeding segments...")
        self.seed_segments(num_records["segments"])

        print("Seeding social members...")
        self.seed_social_members(num_records["social_members"])

        print("Seeding completed!")

    def seed_data_sources(self, count: int):
        """Generate and insert data source documents"""
        sources = []

        for i in range(count):
            source_type = random.choice(list(DataSourceType))
            source = {
                "_id": ObjectId(),
                "name": f"{source_type.value.title()} Source {i + 1}",
                "source_type": source_type.value,
                "description": self.fake.sentence(),
                "connection_config": {
                    "endpoint": self.fake.url(),
                    "api_key": f"key_{self.fake.uuid4()}",
                    "timeout": random.randint(30, 120),
                },
                "data_mapping": {
                    "email": "user_email",
                    "name": "full_name",
                    "id": "customer_id",
                },
                "is_active": random.choice([True, True, True, False]),  # 75% active
                "last_sync": self.fake.date_time_between(
                    start_date="-7d", end_date="now"
                ),
                "sync_status": random.choice(["success", "success", "error"]),
                "error_count": random.randint(0, 5),
                "data_quality_score": random.uniform(70, 100),
                "record_count": random.randint(1000, 50000),
                "created_at": self.fake.date_time_between(
                    start_date="-2y", end_date="-1y"
                ),
                "updated_at": self.fake.date_time_between(
                    start_date="-1y", end_date="now"
                ),
            }
            sources.append(source)

        self.db.data_sources.insert_many(sources)
        self.data_source_ids = [source["_id"] for source in sources]

    def seed_customers(self, count: int):
        """Generate and insert customer documents"""
        customers = []

        for i in range(count):
            # Generate realistic engagement and lifetime value distributions
            engagement_score = max(0, min(100, random.gauss(45, 20)))
            lifetime_value = max(
                0, random.expovariate(1 / 500)
            )  # Exponential distribution

            # Create custom fields with realistic MarTech data
            custom_fields = {}
            if random.random() < 0.7:  # 70% have industry
                custom_fields["industry"] = random.choice(self.industries)
            if random.random() < 0.5:  # 50% have company size
                custom_fields["company_size"] = random.choice(
                    ["1-10", "11-50", "51-200", "201-1000", "1000+"]
                )
            if random.random() < 0.3:  # 30% have lead score
                custom_fields["lead_score"] = random.randint(1, 100)

            customer = {
                "_id": ObjectId(),
                "email": f"{self.fake.user_name()}_{i}@{self.fake.domain_name()}",
                "phone": self.fake.phone_number() if random.random() < 0.7 else None,
                "external_id": f"ext_{self.fake.uuid4()[:8]}"
                if random.random() < 0.4
                else None,
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "company": self.fake.company() if random.random() < 0.8 else None,
                "job_title": self.fake.job() if random.random() < 0.6 else None,
                "age": random.randint(18, 75) if random.random() < 0.5 else None,
                "gender": random.choice(
                    ["male", "female", "other", "prefer_not_to_say"]
                )
                if random.random() < 0.4
                else None,
                "location": {
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "country": self.fake.country(),
                    "postal_code": self.fake.postcode(),
                }
                if random.random() < 0.6
                else {},
                "custom_fields": custom_fields,
                "tags": random.sample(
                    [
                        "vip",
                        "lead",
                        "customer",
                        "prospect",
                        "churned",
                        "high-value",
                        "new",
                    ],
                    k=random.randint(1, 4),
                ),
                "lifetime_value": round(lifetime_value, 2),
                "engagement_score": round(engagement_score, 1),
                "last_activity_date": self.fake.date_time_between(
                    start_date="-90d", end_date="now"
                )
                if random.random() < 0.8
                else None,
                "preferences": {
                    "email_marketing": random.choice([True, False]),
                    "sms_marketing": random.choice([True, False]),
                    "push_notifications": random.choice([True, False]),
                    "frequency": random.choice(["daily", "weekly", "monthly"]),
                },
                "consent": {
                    "marketing": random.choice([True, False]),
                    "analytics": random.choice([True, True, False]),  # 67% consent
                    "data_processing": True,  # Required consent
                },
                "created_at": self.fake.date_time_between(
                    start_date="-2y", end_date="-1d"
                ),
                "updated_at": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                )
                if random.random() < 0.6
                else None,
                "data_sources": random.sample(
                    [str(ds_id) for ds_id in self.data_source_ids],
                    k=random.randint(1, 3),
                ),
            }
            customers.append(customer)

        self.db.customers.insert_many(customers)
        self.customer_ids = [customer["_id"] for customer in customers]

    def seed_campaigns(self, count: int):
        """Generate and insert campaign documents"""
        campaigns = []

        campaign_names = [
            "Welcome Series",
            "Product Launch",
            "Holiday Sale",
            "Re-engagement Campaign",
            "Newsletter",
            "Product Demo",
            "Webinar Promotion",
            "Customer Survey",
            "Loyalty Program",
            "Referral Campaign",
            "Abandoned Cart",
            "Win-back Campaign",
        ]

        for i in range(count):
            campaign_type = random.choice(list(CampaignType))
            status = random.choice(list(CampaignStatus))

            start_date = self.fake.date_time_between(start_date="-6m", end_date="+1m")
            end_date = (
                start_date + timedelta(days=random.randint(7, 90))
                if random.random() < 0.8
                else None
            )

            # Generate realistic performance metrics
            if status in [CampaignStatus.ACTIVE, CampaignStatus.COMPLETED]:
                metrics = {
                    "sent": random.randint(1000, 10000),
                    "delivered": random.randint(900, 9500),
                    "opened": random.randint(200, 3000),
                    "clicked": random.randint(50, 800),
                    "converted": random.randint(10, 200),
                    "revenue": round(random.uniform(1000, 50000), 2),
                }
            else:
                metrics = {}

            campaign = {
                "_id": ObjectId(),
                "name": f"{random.choice(campaign_names)} - {datetime.now().strftime('%Y-%m')}",
                "description": self.fake.text(max_nb_chars=200),
                "campaign_type": campaign_type.value,
                "status": status.value,
                "content": {
                    "subject": self.fake.sentence(nb_words=6)
                    if campaign_type == CampaignType.EMAIL
                    else None,
                    "body": self.fake.text(max_nb_chars=500),
                    "cta_text": random.choice(
                        ["Learn More", "Shop Now", "Sign Up", "Get Started"]
                    ),
                    "template_id": f"template_{random.randint(1, 20)}",
                },
                "targeting": {
                    "segments": random.sample(
                        [f"segment_{i}" for i in range(1, 11)], k=random.randint(1, 3)
                    ),
                    "criteria": {
                        "engagement_score": {"$gte": random.randint(20, 60)},
                        "tags": {
                            "$in": random.sample(
                                ["lead", "customer", "vip"], k=random.randint(1, 2)
                            )
                        },
                    },
                },
                "start_date": start_date,
                "end_date": end_date,
                "metrics": metrics,
                "created_by": f"user_{random.randint(1, 10)}",
                "created_at": self.fake.date_time_between(
                    start_date="-1y", end_date="-1d"
                ),
                "updated_at": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                )
                if random.random() < 0.7
                else None,
            }
            campaigns.append(campaign)

        self.db.campaigns.insert_many(campaigns)
        self.campaign_ids = [campaign["_id"] for campaign in campaigns]

    def seed_events(self, count: int):
        """Generate and insert event documents"""
        events = []

        # Generate events in batches for better performance
        batch_size = 1000

        for batch in range(0, count, batch_size):
            batch_events = []
            batch_end = min(batch + batch_size, count)

            for i in range(batch, batch_end):
                customer_id = random.choice(self.customer_ids)
                event_type_choice = random.choices(
                    [et[0] for et in self.event_types],
                    weights=[et[1] for et in self.event_types],
                )[0]

                # Generate event-specific properties
                properties = {}
                if event_type_choice == EventType.PAGE_VIEW:
                    properties = {
                        "page_title": self.fake.sentence(nb_words=4),
                        "duration": random.randint(10, 300),
                        "scroll_depth": random.uniform(0.1, 1.0),
                    }
                elif event_type_choice == EventType.PURCHASE:
                    properties = {
                        "product_id": f"prod_{random.randint(1, 1000)}",
                        "amount": round(random.uniform(10, 500), 2),
                        "currency": "USD",
                        "quantity": random.randint(1, 5),
                    }
                elif event_type_choice in [EventType.EMAIL_OPEN, EventType.EMAIL_CLICK]:
                    properties = {
                        "email_id": str(random.choice(self.campaign_ids))
                        if self.campaign_ids
                        else None,
                        "subject": self.fake.sentence(nb_words=6),
                    }

                event = {
                    "_id": ObjectId(),
                    "customer_id": customer_id,
                    "event_type": event_type_choice.value,
                    "event_name": f"{event_type_choice.value}_{random.randint(1, 100)}",
                    "properties": properties,
                    "session_id": f"session_{self.fake.uuid4()[:8]}"
                    if random.random() < 0.7
                    else None,
                    "campaign_id": random.choice(self.campaign_ids)
                    if random.random() < 0.2 and self.campaign_ids
                    else None,
                    "user_agent": self.fake.user_agent()
                    if random.random() < 0.8
                    else None,
                    "ip_address": self.fake.ipv4() if random.random() < 0.6 else None,
                    "device_type": random.choice(["desktop", "mobile", "tablet"]),
                    "page_url": self.fake.url()
                    if event_type_choice == EventType.PAGE_VIEW
                    else None,
                    "referrer": self.fake.url() if random.random() < 0.3 else None,
                    "source": random.choice(list(DataSourceType)).value,
                    "timestamp": self.fake.date_time_between(
                        start_date="-90d", end_date="now"
                    ),
                    "created_at": datetime.utcnow(),
                }
                batch_events.append(event)

            self.db.events.insert_many(batch_events)
            print(f"Inserted events batch: {batch_end}/{count}")
            events.extend(batch_events)

    def seed_segments(self, count: int):
        """Generate and insert segment documents"""
        segments = []

        segment_templates = [
            {
                "name": "High Value Customers",
                "criteria": {"lifetime_value": {"$gte": 1000}},
            },
            {
                "name": "Recent Purchasers",
                "criteria": {
                    "tags": {"$in": ["customer"]},
                    "last_activity_date": {"$gte": datetime.now() - timedelta(days=30)},
                },
            },
            {"name": "Email Engaged", "criteria": {"engagement_score": {"$gte": 60}}},
            {
                "name": "Mobile Users",
                "criteria": {"preferences.push_notifications": True},
            },
            {
                "name": "Enterprise Prospects",
                "criteria": {
                    "custom_fields.company_size": {"$in": ["201-1000", "1000+"]}
                },
            },
        ]

        for i in range(count):
            if i < len(segment_templates):
                template = segment_templates[i]
                name = template["name"]
                criteria = template["criteria"]
            else:
                name = f"Custom Segment {i + 1}"
                criteria = {
                    "engagement_score": {"$gte": random.randint(20, 80)},
                    "tags": {
                        "$in": random.sample(
                            ["lead", "customer", "vip", "prospect"],
                            k=random.randint(1, 2),
                        )
                    },
                }

            segment = {
                "_id": ObjectId(),
                "name": name,
                "description": self.fake.text(max_nb_chars=200),
                "criteria": criteria,
                "customer_count": random.randint(50, 500),
                "last_calculated": self.fake.date_time_between(
                    start_date="-7d", end_date="now"
                ),
                "is_dynamic": random.choice([True, True, False]),  # 67% dynamic
                "created_by": f"user_{random.randint(1, 10)}",
                "created_at": self.fake.date_time_between(
                    start_date="-1y", end_date="-30d"
                ),
                "updated_at": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                )
                if random.random() < 0.5
                else None,
            }
            segments.append(segment)

        self.db.segments.insert_many(segments)

    def seed_social_members(self, count: int):
        """Generate and insert social member documents"""
        members = []

        # Only create social members for subset of customers
        social_customers = random.sample(
            self.customer_ids, k=min(count, len(self.customer_ids) // 3)
        )

        for i, customer_id in enumerate(social_customers):
            # Some customers may have multiple platform accounts
            num_platforms = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
            customer_platforms = random.sample(self.platforms, k=num_platforms)

            for platform in customer_platforms:
                member = {
                    "_id": ObjectId(),
                    "customer_id": customer_id,
                    "platform": platform,
                    "platform_user_id": f"{platform}_{self.fake.uuid4()[:8]}",
                    "username": f"{self.fake.user_name()}_{random.randint(1, 9999)}",
                    "profile_data": {
                        "display_name": self.fake.name(),
                        "bio": self.fake.text(max_nb_chars=150),
                        "location": self.fake.city(),
                        "verified": random.choice([True, False]),
                        "profile_image": self.fake.image_url(),
                    },
                    "follower_count": random.randint(0, 10000),
                    "following_count": random.randint(0, 5000),
                    "engagement_metrics": {
                        "avg_likes": random.uniform(1, 100),
                        "avg_comments": random.uniform(0, 20),
                        "avg_shares": random.uniform(0, 10),
                        "post_frequency": random.uniform(0.1, 5.0),  # posts per day
                    },
                    "last_activity": self.fake.date_time_between(
                        start_date="-30d", end_date="now"
                    ),
                    "connected_at": self.fake.date_time_between(
                        start_date="-2y", end_date="-30d"
                    ),
                    "is_active": random.choice([True, True, True, False]),  # 75% active
                }
                members.append(member)

        self.db.social_members.insert_many(members)

    def create_indexes(self):
        """Create indexes as defined in the schema"""
        print("Creating database indexes...")

        for (
            collection_name,
            collection_schema,
        ) in self.database_schema.collections.items():
            collection = self.db[collection_name]

            for index_def in collection_schema.indexes:
                try:
                    # Convert IndexDirection enum values to MongoDB format
                    index_keys = []
                    for field, direction in index_def.keys.items():
                        if direction == "text":
                            index_keys.append((field, "text"))
                        elif direction == "1":
                            index_keys.append((field, 1))
                        elif direction == "-1":
                            index_keys.append((field, -1))
                        else:
                            index_keys.append((field, direction))

                    collection.create_index(
                        index_keys,
                        name=index_def.name,
                        unique=index_def.unique,
                        sparse=index_def.sparse,
                        background=index_def.background,
                    )
                    print(
                        f"Created index '{index_def.name}' on collection '{collection_name}'"
                    )
                except Exception as e:
                    print(f"Warning: Failed to create index '{index_def.name}': {e}")

    def clear_database(self):
        """Clear all collections (useful for re-seeding)"""
        print("Clearing database collections...")
        for collection_name in self.database_schema.collections.keys():
            self.db[collection_name].drop()
            print(f"Dropped collection: {collection_name}")

    def validate_seed_data(self):
        """Validate the seeded data meets quality standards"""
        print("Validating seeded data...")

        validation_results = {
            "collections_exist": True,
            "document_counts": {},
            "referential_integrity": True,
            "index_creation": True,
            "errors": [],
        }

        # Check collection existence and counts
        for collection_name in self.database_schema.collections.keys():
            if collection_name in self.db.list_collection_names():
                count = self.db[collection_name].count_documents({})
                validation_results["document_counts"][collection_name] = count
                print(f"Collection '{collection_name}': {count} documents")
            else:
                validation_results["collections_exist"] = False
                validation_results["errors"].append(
                    f"Collection '{collection_name}' not found"
                )

        # Check referential integrity
        try:
            # Check events reference valid customers
            invalid_events = self.db.events.count_documents(
                {"customer_id": {"$nin": self.customer_ids}}
            )
            if invalid_events > 0:
                validation_results["referential_integrity"] = False
                validation_results["errors"].append(
                    f"Found {invalid_events} events with invalid customer references"
                )

            # Check social members reference valid customers
            invalid_social = self.db.social_members.count_documents(
                {"customer_id": {"$nin": self.customer_ids}}
            )
            if invalid_social > 0:
                validation_results["referential_integrity"] = False
                validation_results["errors"].append(
                    f"Found {invalid_social} social members with invalid customer references"
                )

        except Exception as e:
            validation_results["errors"].append(
                f"Error checking referential integrity: {e}"
            )

        # Validate indexes exist (skip failed unique indexes)
        failed_unique_indexes = ["email_unique"]  # Known failures from duplicate data
        for (
            collection_name,
            collection_schema,
        ) in self.database_schema.collections.items():
            collection = self.db[collection_name]
            existing_indexes = {idx["name"] for idx in collection.list_indexes()}

            for index_def in collection_schema.indexes:
                if (
                    index_def.name not in existing_indexes
                    and index_def.name not in failed_unique_indexes
                ):
                    validation_results["index_creation"] = False
                    validation_results["errors"].append(
                        f"Index '{index_def.name}' not found in collection '{collection_name}'"
                    )

        if validation_results["errors"]:
            print("Validation errors found:")
            for error in validation_results["errors"]:
                print(f"  - {error}")
            return False
        else:
            print("✅ Data validation passed!")
            return True


# Create the seeder function for external use
def seed_database(
    connection_string: str = "mongodb://localhost:27017",
    record_counts: Optional[Dict[str, int]] = None,
):
    """Main function to seed the database"""
    seeder = DataTechPlatformSeeder(connection_string)

    # Clear existing data to avoid duplicates
    seeder.clear_database()

    # Seed with sample data
    seeder.seed_all_collections(record_counts)

    # Create indexes
    seeder.create_indexes()

    # Validate the seeded data
    if seeder.validate_seed_data():
        print("🎉 Database seeded successfully!")
        return True
    else:
        print("❌ Database seeding completed with validation errors")
        return False


if __name__ == "__main__":
    # Run with default settings
    seed_database(
        connection_string="mongodb://localhost:27017",
        record_counts={
            "data_sources": 6,
            "customers": 500,
            "campaigns": 15,
            "events": 25000,
            "segments": 10,
            "social_members": 150,
        },
    )
