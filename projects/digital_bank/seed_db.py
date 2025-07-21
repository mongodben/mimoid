"""Seed script for NeoLend Bank Digital Lending Platform"""

from faker import Faker
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Optional, List
import uuid
import math

# Import the database schema
from db_schema import (
    database_schema,
    ApplicationStatus,
    LoanStatus,
    PaymentStatus,
    PaymentMethod,
    RiskLevel,
    DataSourceType,
)
from mimoid import DatabaseSeeder


class NeoLendBankSeeder(DatabaseSeeder):
    def __init__(self, connection_string: str):
        super().__init__(connection_string, database_schema)
        self.client = MongoClient(connection_string)
        self.db = self.client[database_schema.database_name]
        self.fake = Faker(["en_US", "id_ID"])  # English and Indonesian locales

        # Seed data storage for referential integrity
        self.customer_ids = []
        self.application_ids = []
        self.loan_ids = []
        self.active_loan_ids = []

        # Define realistic distributions for digital lending
        self.loan_amounts = [
            (100, 0.3),
            (250, 0.25),
            (500, 0.2),
            (750, 0.15),
            (1000, 0.07),
            (1500, 0.03),
        ]
        self.loan_purposes = [
            "Business expansion",
            "Equipment repair",
            "Working capital",
            "Inventory purchase",
            "Medical expenses",
            "Education",
            "Home improvement",
            "Emergency funds",
            "Debt consolidation",
            "Vehicle repair",
        ]

        self.employment_types = [
            "Self-employed",
            "Small business owner",
            "Freelancer",
            "Part-time worker",
            "Unemployed",
            "Student",
        ]
        self.risk_distributions = [
            (RiskLevel.VERY_LOW, 0.05),
            (RiskLevel.LOW, 0.25),
            (RiskLevel.MEDIUM, 0.45),
            (RiskLevel.HIGH, 0.20),
            (RiskLevel.VERY_HIGH, 0.05),
        ]

    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None):
        """Seed all collections with sample data"""
        if num_records is None:
            num_records = {
                "customers": 2500,
                "loan_applications": 4000,
                "loans": 2800,
                "payments": 15000,
                "credit_scores": 5000,
                "collection_cases": 300,
                "compliance_records": 800,
            }

        print("Starting NeoLend Bank database seeding...")

        # Seed in dependency order
        print("Seeding customers...")
        self.seed_customers(num_records["customers"])

        print("Seeding loan applications...")
        self.seed_loan_applications(num_records["loan_applications"])

        print("Seeding loans...")
        self.seed_loans(num_records["loans"])

        print("Seeding payments...")
        self.seed_payments(num_records["payments"])

        print("Seeding credit scores...")
        self.seed_credit_scores(num_records["credit_scores"])

        print("Seeding collection cases...")
        self.seed_collection_cases(num_records["collection_cases"])

        print("Seeding compliance records...")
        self.seed_compliance_records(num_records["compliance_records"])

        print("Seeding completed!")

    def generate_phone_number(self, country_code="+62"):
        """Generate Indonesian phone numbers"""
        # Indonesian mobile numbers typically start with 8 after country code
        return f"{country_code}8{random.randint(1000000000, 9999999999)}"

    def generate_alternative_data(self):
        """Generate realistic alternative credit data"""
        social_media_data = {}
        behavioral_data = {}
        device_data = {}
        network_data = {}

        if random.random() < 0.7:  # 70% have social media data
            social_media_data = {
                "facebook_profile_age_months": random.randint(6, 120),
                "facebook_friends_count": random.randint(50, 2000),
                "posts_per_month": random.randint(0, 50),
                "business_related_posts": random.random() < 0.3,
                "financial_keywords_count": random.randint(0, 10),
            }

        if random.random() < 0.8:  # 80% have behavioral data
            behavioral_data = {
                "app_usage_hours_per_day": round(random.uniform(1, 8), 1),
                "financial_apps_installed": random.randint(1, 5),
                "loan_form_completion_time_seconds": random.randint(120, 1200),
                "form_corrections_made": random.randint(0, 5),
                "application_attempts": random.randint(1, 3),
            }

        if random.random() < 0.9:  # 90% have device data
            device_data = {
                "device_age_months": random.randint(1, 48),
                "device_value_usd": random.randint(100, 1200),
                "device_model": random.choice(
                    ["Samsung Galaxy", "iPhone", "Xiaomi", "Oppo", "Vivo"]
                ),
                "operating_system": random.choice(["Android", "iOS"]),
                "apps_installed_count": random.randint(20, 200),
                "location_accuracy": random.choice(["GPS", "Network", "Approximate"]),
            }

        if random.random() < 0.4:  # 40% have network data
            network_data = {
                "contacts_with_loans": random.randint(0, 10),
                "contact_list_size": random.randint(50, 500),
                "avg_call_duration_minutes": round(random.uniform(1, 15), 1),
                "frequent_contact_patterns": random.choice(
                    ["Family", "Business", "Mixed"]
                ),
            }

        return social_media_data, behavioral_data, device_data, network_data

    def calculate_credit_score(
        self, customer_data, social_data, behavioral_data, device_data
    ):
        """Calculate AI-based credit score using alternative data"""
        base_score = 500

        # Traditional factors
        monthly_income = customer_data.get("monthly_income", 0)
        if monthly_income and monthly_income > 500:
            base_score += 50
        if customer_data.get("bank_account_verified"):
            base_score += 30
        if customer_data.get("employment_status") == "Self-employed":
            base_score += 20

        # Social media factors
        if social_data:
            profile_age = social_data.get("facebook_profile_age_months", 0)
            if profile_age and profile_age > 24:
                base_score += 25
            if social_data.get("business_related_posts"):
                base_score += 15
            friends_count = social_data.get("facebook_friends_count", 0)
            if friends_count and friends_count > 200:
                base_score += 10

        # Behavioral factors
        if behavioral_data:
            completion_time = behavioral_data.get(
                "loan_form_completion_time_seconds", 600
            )
            if completion_time and completion_time < 300:
                base_score += 20  # Quick, confident completion
            apps_installed = behavioral_data.get("financial_apps_installed", 0)
            if apps_installed and apps_installed > 2:
                base_score += 15
            corrections = behavioral_data.get("form_corrections_made", 0)
            if corrections is not None and corrections < 2:
                base_score += 10

        # Device factors
        if device_data:
            device_value = device_data.get("device_value_usd", 0)
            if device_value and device_value > 400:
                base_score += 20
            device_age = device_data.get("device_age_months", 48)
            if device_age and device_age < 12:
                base_score += 15

        # Add randomness for realistic distribution
        score = base_score + random.randint(-50, 50)
        return max(300, min(850, score))

    def seed_customers(self, count: int):
        """Generate and insert customer documents"""
        customers = []

        for i in range(count):
            social_data, behavioral_data, device_data, network_data = (
                self.generate_alternative_data()
            )

            # Generate basic customer info
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            monthly_income = (
                random.uniform(200, 2000) if random.random() < 0.6 else None
            )
            employment_status = random.choice(self.employment_types)

            customer_data = {
                "first_name": first_name,
                "last_name": last_name,
                "monthly_income": monthly_income,
                "employment_status": employment_status,
                "bank_account_verified": random.choice([True, False]),
            }

            credit_score = self.calculate_credit_score(
                customer_data, social_data, behavioral_data, device_data
            )

            # Determine risk level based on credit score
            if credit_score >= 750:
                risk_level = RiskLevel.VERY_LOW
            elif credit_score >= 650:
                risk_level = RiskLevel.LOW
            elif credit_score >= 550:
                risk_level = RiskLevel.MEDIUM
            elif credit_score >= 450:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.VERY_HIGH

            customer = {
                "_id": ObjectId(),
                "phone_number": self.generate_phone_number(),
                "email": self.fake.email() if random.random() < 0.4 else None,
                "national_id": f"ID{random.randint(1000000000, 9999999999)}"
                if random.random() < 0.3
                else None,
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": self.fake.date_time_between(
                    start_date="-65y", end_date="-18y"
                )
                if random.random() < 0.5
                else None,
                "gender": random.choice(["Male", "Female", "Other"])
                if random.random() < 0.6
                else None,
                "address": {
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "province": self.fake.state(),
                    "postal_code": self.fake.postcode(),
                    "country": "Indonesia",
                }
                if random.random() < 0.7
                else {},
                "location_data": {
                    "latitude": float(self.fake.latitude()),
                    "longitude": float(self.fake.longitude()),
                    "accuracy_radius_km": random.uniform(0.1, 10),
                }
                if random.random() < 0.8
                else {},
                "monthly_income": monthly_income,
                "employment_status": employment_status,
                "employer_name": self.fake.company()
                if employment_status not in ["Unemployed", "Student"]
                and random.random() < 0.6
                else None,
                "bank_account_verified": customer_data["bank_account_verified"],
                "social_media_data": social_data,
                "behavioral_data": behavioral_data,
                "device_data": device_data,
                "network_data": network_data,
                "current_credit_score": credit_score,
                "risk_level": risk_level.value,
                "fraud_score": random.uniform(
                    0, 20
                ),  # Most customers have low fraud scores
                "registration_date": self.fake.date_time_between(
                    start_date="-3y", end_date="-1d"
                ),
                "last_activity": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                )
                if random.random() < 0.8
                else None,
                "kyc_completed": random.choice(
                    [True, True, True, False]
                ),  # 75% completed KYC
                "kyc_completion_date": self.fake.date_time_between(
                    start_date="-2y", end_date="now"
                )
                if random.random() < 0.7
                else None,
                "data_consent": {
                    "social_media": random.choice([True, False]),
                    "device_data": random.choice([True, True, False]),  # 67% consent
                    "behavioral_analysis": random.choice([True, False]),
                    "location_tracking": random.choice([True, False]),
                },
                "marketing_consent": random.choice([True, False]),
                "total_loans": 0,  # Will be updated after loan creation
                "total_loan_amount": 0.0,
                "repayment_rate": None,  # Will be calculated after payments
                "days_since_last_loan": None,
                "created_at": self.fake.date_time_between(
                    start_date="-3y", end_date="-1d"
                ),
                "updated_at": self.fake.date_time_between(
                    start_date="-30d", end_date="now"
                )
                if random.random() < 0.6
                else None,
                "data_sources": [
                    source.value
                    for source in random.sample(
                        list(DataSourceType), k=random.randint(2, 4)
                    )
                ],
            }
            customers.append(customer)

        self.db.customers.insert_many(customers)
        self.customer_ids = [customer["_id"] for customer in customers]

    def seed_loan_applications(self, count: int):
        """Generate and insert loan application documents"""
        applications = []

        # Ensure we have enough customers
        if count > len(self.customer_ids) * 2:
            print(
                f"Warning: Generating {count} applications for {len(self.customer_ids)} customers"
            )

        for i in range(count):
            customer_id = random.choice(self.customer_ids)

            # Get customer's credit score for realistic approval decisions
            customer = self.db.customers.find_one({"_id": customer_id})
            credit_score = customer.get("current_credit_score", 500)

            # Generate application
            requested_amount = random.choices(
                [amount[0] for amount in self.loan_amounts],
                weights=[amount[1] for amount in self.loan_amounts],
            )[0]

            # Application status based on credit score
            if credit_score >= 650:
                status = random.choices(
                    [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED],
                    weights=[0.8, 0.2],
                )[0]
            elif credit_score >= 500:
                status = random.choices(
                    [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED],
                    weights=[0.5, 0.5],
                )[0]
            else:
                status = random.choices(
                    [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED],
                    weights=[0.2, 0.8],
                )[0]

            submitted_date = self.fake.date_time_between(
                start_date="-2y", end_date="now"
            )

            application = {
                "_id": ObjectId(),
                "customer_id": customer_id,
                "requested_amount": requested_amount,
                "loan_purpose": random.choice(self.loan_purposes),
                "requested_term_days": random.choice([30, 45, 60, 90]),
                "application_data": {
                    "monthly_income_declared": random.uniform(300, 1500),
                    "existing_debts": random.uniform(0, 500),
                    "family_size": random.randint(1, 6),
                    "housing_status": random.choice(["Own", "Rent", "Family"]),
                    "education_level": random.choice(
                        ["Primary", "Secondary", "University", "None"]
                    ),
                },
                "supporting_documents": [
                    {
                        "type": "id_photo",
                        "status": "verified",
                        "uploaded_at": submitted_date,
                    },
                    {
                        "type": "selfie",
                        "status": "verified",
                        "uploaded_at": submitted_date,
                    },
                ]
                if random.random() < 0.8
                else [],
                "device_fingerprint": {
                    "ip_address": self.fake.ipv4(),
                    "user_agent": self.fake.user_agent(),
                    "screen_resolution": random.choice(
                        ["1080x1920", "720x1280", "1440x2560"]
                    ),
                    "timezone": "Asia/Jakarta",
                    "language": random.choice(["id-ID", "en-US"]),
                },
                "session_data": {
                    "session_duration_seconds": random.randint(300, 1800),
                    "pages_visited": random.randint(3, 15),
                    "form_focus_time_seconds": random.randint(120, 600),
                    "copy_paste_detected": random.choice([True, False]),
                },
                "geolocation": {
                    "latitude": float(self.fake.latitude()),
                    "longitude": float(self.fake.longitude()),
                    "accuracy_meters": random.randint(5, 100),
                },
                "status": status.value,
                "submitted_at": submitted_date,
                "reviewed_at": submitted_date + timedelta(hours=random.randint(1, 48))
                if status != ApplicationStatus.SUBMITTED
                else None,
                "decision_date": submitted_date + timedelta(hours=random.randint(2, 72))
                if status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]
                else None,
                "credit_score": credit_score
                + random.randint(-50, 50),  # Slight variation from customer score
                "risk_assessment": {
                    "debt_to_income_ratio": random.uniform(0.1, 0.8),
                    "alternative_data_score": random.uniform(0.3, 0.9),
                    "device_trust_score": random.uniform(0.5, 1.0),
                    "behavioral_consistency": random.uniform(0.4, 1.0),
                },
                "decision_factors": [
                    {"factor": "Credit Score", "weight": 0.3, "value": credit_score},
                    {
                        "factor": "Income Verification",
                        "weight": 0.2,
                        "value": random.uniform(0.5, 1.0),
                    },
                    {
                        "factor": "Alternative Data",
                        "weight": 0.25,
                        "value": random.uniform(0.3, 0.9),
                    },
                    {
                        "factor": "Device Trust",
                        "weight": 0.15,
                        "value": random.uniform(0.6, 1.0),
                    },
                    {
                        "factor": "Application Quality",
                        "weight": 0.1,
                        "value": random.uniform(0.7, 1.0),
                    },
                ],
                "model_version": random.choice(["v2.1.0", "v2.2.0", "v2.3.0"]),
                "approved_amount": requested_amount * random.uniform(0.8, 1.0)
                if status == ApplicationStatus.APPROVED
                else None,
                "approved_term_days": random.choice([30, 45, 60])
                if status == ApplicationStatus.APPROVED
                else None,
                "interest_rate": random.uniform(15, 35)
                if status == ApplicationStatus.APPROVED
                else None,
                "rejection_reason": random.choice(
                    [
                        "Insufficient credit history",
                        "High debt-to-income ratio",
                        "Inconsistent application data",
                        "Failed device verification",
                        "Regulatory restrictions",
                    ]
                )
                if status == ApplicationStatus.REJECTED
                else None,
                "processed_by": "ai_system_v2",
                "notes": self.fake.sentence() if random.random() < 0.3 else None,
            }
            applications.append(application)

        self.db.loan_applications.insert_many(applications)
        self.application_ids = [app["_id"] for app in applications]

    def seed_loans(self, count: int):
        """Generate and insert loan documents"""
        # Get approved applications to create loans from
        approved_apps = list(self.db.loan_applications.find({"status": "approved"}))

        if len(approved_apps) < count:
            print(
                f"Warning: Only {len(approved_apps)} approved applications available for {count} loans"
            )
            count = len(approved_apps)

        loans = []

        # Create loans from approved applications
        for i in range(count):
            app = (
                approved_apps[i]
                if i < len(approved_apps)
                else random.choice(approved_apps)
            )

            principal = app["approved_amount"]
            interest_rate = app["interest_rate"]
            term_days = app["approved_term_days"]

            # Calculate loan amounts
            daily_interest_rate = interest_rate / 365 / 100
            total_amount = principal * (1 + daily_interest_rate * term_days)
            daily_interest = (total_amount - principal) / term_days

            # Determine loan status and payment progress
            status_weights = [
                (LoanStatus.ACTIVE, 0.6),
                (LoanStatus.PAID_OFF, 0.25),
                (LoanStatus.DEFAULTED, 0.08),
                (LoanStatus.IN_COLLECTIONS, 0.05),
                (LoanStatus.CHARGED_OFF, 0.02),
            ]

            status = random.choices(
                [s[0] for s in status_weights], weights=[s[1] for s in status_weights]
            )[0]

            # Calculate payment progress based on status
            disbursed_date = app["decision_date"] + timedelta(
                hours=random.randint(4, 48)
            )
            due_date = disbursed_date + timedelta(days=term_days)

            if status == LoanStatus.PAID_OFF:
                payment_progress = 1.0
                total_paid = total_amount
                outstanding_balance = 0.0
                closed_date = disbursed_date + timedelta(
                    days=random.randint(term_days - 10, term_days)
                )
            elif status in [
                LoanStatus.DEFAULTED,
                LoanStatus.CHARGED_OFF,
                LoanStatus.IN_COLLECTIONS,
            ]:
                payment_progress = random.uniform(0.1, 0.7)
                total_paid = total_amount * payment_progress
                outstanding_balance = total_amount - total_paid
                closed_date = None
            else:  # Active loans
                days_elapsed = min((datetime.now() - disbursed_date).days, term_days)
                expected_progress = days_elapsed / term_days
                actual_progress = expected_progress * random.uniform(
                    0.8, 1.2
                )  # Some variance
                payment_progress = min(actual_progress, 1.0)
                total_paid = total_amount * payment_progress
                outstanding_balance = total_amount - total_paid
                closed_date = None

            # Calculate days past due
            if status == LoanStatus.ACTIVE:
                if datetime.now() > due_date:
                    days_past_due = (datetime.now() - due_date).days
                else:
                    days_past_due = 0
            elif status in [LoanStatus.DEFAULTED, LoanStatus.IN_COLLECTIONS]:
                days_past_due = random.randint(30, 180)
            else:
                days_past_due = 0

            loan = {
                "_id": ObjectId(),
                "customer_id": app["customer_id"],
                "application_id": app["_id"],
                "principal_amount": principal,
                "interest_rate": interest_rate,
                "term_days": term_days,
                "total_amount": total_amount,
                "daily_interest": daily_interest,
                "due_date": due_date,
                "payment_schedule": self.generate_payment_schedule(
                    principal, total_amount, term_days, disbursed_date
                ),
                "status": status.value,
                "disbursed_at": disbursed_date,
                "disbursed_amount": principal,
                "disbursement_method": random.choice(list(PaymentMethod)).value,
                "total_paid": round(total_paid, 2),
                "principal_paid": round(min(total_paid, principal), 2),
                "interest_paid": round(max(0, total_paid - principal), 2),
                "fees_paid": round(
                    random.uniform(0, 20) if status != LoanStatus.PAID_OFF else 0, 2
                ),
                "outstanding_balance": round(outstanding_balance, 2),
                "days_past_due": days_past_due,
                "payment_count": int(
                    payment_progress * random.randint(term_days // 7, term_days // 3)
                ),
                "missed_payments": random.randint(0, 3)
                if status != LoanStatus.PAID_OFF
                else 0,
                "last_payment_date": disbursed_date
                + timedelta(days=int(payment_progress * term_days))
                if total_paid > 0
                else None,
                "current_risk_level": self.assess_loan_risk(
                    days_past_due, payment_progress
                ).value,
                "in_collections": status == LoanStatus.IN_COLLECTIONS,
                "collections_start_date": due_date + timedelta(days=30)
                if status in [LoanStatus.IN_COLLECTIONS, LoanStatus.DEFAULTED]
                else None,
                "closed_at": closed_date,
                "closure_reason": status.value if closed_date else None,
                "created_at": disbursed_date,
                "updated_at": self.fake.date_time_between(
                    start_date=disbursed_date, end_date="now"
                )
                if random.random() < 0.7
                else None,
            }
            loans.append(loan)

        self.db.loans.insert_many(loans)
        self.loan_ids = [loan["_id"] for loan in loans]
        self.active_loan_ids = [
            loan["_id"] for loan in loans if loan["status"] == LoanStatus.ACTIVE.value
        ]

    def generate_payment_schedule(self, principal, total_amount, term_days, start_date):
        """Generate a payment schedule for a loan"""
        # Simple daily payment schedule
        daily_payment = total_amount / term_days
        schedule = []

        for day in range(term_days):
            schedule.append(
                {
                    "day": day + 1,
                    "due_date": start_date + timedelta(days=day + 1),
                    "amount": round(daily_payment, 2),
                    "principal_portion": round(principal / term_days, 2),
                    "interest_portion": round(
                        (total_amount - principal) / term_days, 2
                    ),
                }
            )

        return schedule

    def assess_loan_risk(self, days_past_due, payment_progress):
        """Assess current risk level of a loan"""
        if days_past_due > 90:
            return RiskLevel.VERY_HIGH
        elif days_past_due > 30:
            return RiskLevel.HIGH
        elif days_past_due > 7:
            return RiskLevel.MEDIUM
        elif payment_progress < 0.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def seed_payments(self, count: int):
        """Generate and insert payment documents"""
        if not self.loan_ids:
            print("No loans available for payment generation")
            return

        payments = []

        for i in range(count):
            loan_id = random.choice(self.loan_ids)

            # Get loan details
            loan = self.db.loans.find_one({"_id": loan_id})
            if not loan:
                continue

            # Generate payment amount based on loan
            if loan["status"] == "paid_off":
                # For paid off loans, payments should be realistic historical payments
                max_amount = loan["total_amount"] / max(1, loan["payment_count"])
                amount = random.uniform(10, max_amount)
            else:
                # For active loans, generate various payment amounts
                suggested_daily = loan["total_amount"] / loan["term_days"]
                amount = random.uniform(suggested_daily * 0.5, suggested_daily * 3)

            # Payment method distribution based on regional preferences
            payment_method = random.choices(
                list(PaymentMethod),
                weights=[
                    0.1,
                    0.4,
                    0.3,
                    0.15,
                    0.05,
                ],  # bank_transfer, digital_wallet, mobile_money, cash_agent, debit_card
            )[0]

            # Payment status - most payments are completed
            status = random.choices(
                list(PaymentStatus),
                weights=[0.05, 0.9, 0.04, 0.01],  # pending, completed, failed, reversed
            )[0]

            # Payment timing
            scheduled_date = self.fake.date_time_between(
                start_date=loan["disbursed_at"],
                end_date=min(datetime.now(), loan["due_date"]),
            )

            processed_date = (
                scheduled_date + timedelta(minutes=random.randint(1, 1440))
                if status == PaymentStatus.COMPLETED
                else None
            )

            # Calculate payment breakdown
            remaining_principal = max(
                0, loan["principal_amount"] - loan["principal_paid"]
            )
            if remaining_principal > 0:
                principal_portion = min(amount * 0.7, remaining_principal)
                interest_portion = amount - principal_portion
                fees_portion = 0.0
            else:
                principal_portion = 0.0
                interest_portion = amount
                fees_portion = 0.0

            payment = {
                "_id": ObjectId(),
                "loan_id": loan_id,
                "customer_id": loan["customer_id"],
                "amount": round(amount, 2),
                "payment_method": payment_method.value,
                "payment_reference": f"PAY{random.randint(100000, 999999)}"
                if random.random() < 0.8
                else None,
                "principal_portion": round(principal_portion, 2),
                "interest_portion": round(interest_portion, 2),
                "fees_portion": round(fees_portion, 2),
                "status": status.value,
                "scheduled_date": scheduled_date if random.random() < 0.6 else None,
                "processed_date": processed_date,
                "value_date": processed_date,
                "payment_processor": random.choice(
                    ["GoPay", "OVO", "DANA", "BankTransfer", "Indomaret"]
                )
                if payment_method != PaymentMethod.CASH_AGENT
                else None,
                "transaction_id": f"TXN{uuid.uuid4().hex[:12].upper()}"
                if status == PaymentStatus.COMPLETED
                else None,
                "failure_reason": random.choice(
                    [
                        "Insufficient funds",
                        "Invalid account",
                        "Network timeout",
                        "Declined by bank",
                    ]
                )
                if status == PaymentStatus.FAILED
                else None,
                "created_at": scheduled_date,
                "created_by": "customer_app",
                "notes": self.fake.sentence() if random.random() < 0.1 else None,
            }
            payments.append(payment)

        self.db.payments.insert_many(payments)

    def seed_credit_scores(self, count: int):
        """Generate and insert credit score documents"""
        if not self.customer_ids:
            print("No customers available for credit score generation")
            return

        credit_scores = []

        for i in range(count):
            customer_id = random.choice(self.customer_ids)

            # Get customer data for realistic scoring
            customer = self.db.customers.find_one({"_id": customer_id})
            if not customer:
                continue

            base_score = customer.get("current_credit_score", 500)
            # Add variation to simulate score changes over time
            score = max(300, min(850, base_score + random.randint(-50, 50)))

            # Determine risk level from score
            if score >= 750:
                risk_level = RiskLevel.VERY_LOW
            elif score >= 650:
                risk_level = RiskLevel.LOW
            elif score >= 550:
                risk_level = RiskLevel.MEDIUM
            elif score >= 450:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.VERY_HIGH

            # Generate model features
            model_features = {
                "traditional_credit_weight": random.uniform(0.2, 0.4),
                "alternative_data_weight": random.uniform(0.4, 0.6),
                "behavioral_score": random.uniform(0.3, 0.9),
                "social_network_score": random.uniform(0.2, 0.8),
                "device_trust_score": random.uniform(0.5, 1.0),
                "financial_behavior_score": random.uniform(0.4, 0.9),
            }

            created_date = self.fake.date_time_between(start_date="-1y", end_date="now")

            credit_score = {
                "_id": ObjectId(),
                "customer_id": customer_id,
                "score": score,
                "confidence_level": random.uniform(0.7, 0.95),
                "risk_level": risk_level.value,
                "model_version": random.choice(["v2.1.0", "v2.2.0", "v2.3.0"]),
                "model_features": model_features,
                "data_completeness": random.uniform(0.6, 0.95),
                "data_sources_used": [
                    source.value
                    for source in random.sample(
                        list(DataSourceType), k=random.randint(2, 5)
                    )
                ],
                "alternative_data_weight": model_features["alternative_data_weight"],
                "top_risk_factors": random.sample(
                    [
                        "Limited credit history",
                        "High debt utilization",
                        "Inconsistent income",
                        "Recent defaults",
                        "Insufficient collateral",
                    ],
                    k=random.randint(1, 3),
                ),
                "protective_factors": random.sample(
                    [
                        "Stable employment",
                        "Long banking relationship",
                        "Low debt-to-income ratio",
                        "Consistent payment history",
                        "Diverse income sources",
                    ],
                    k=random.randint(1, 3),
                ),
                "trigger_event": random.choice(
                    [
                        "loan_application",
                        "periodic_review",
                        "risk_reassessment",
                        "customer_update",
                        "manual_request",
                    ]
                ),
                "application_id": random.choice(self.application_ids)
                if random.random() < 0.4 and self.application_ids
                else None,
                "valid_until": created_date + timedelta(days=random.randint(30, 180)),
                "is_current": random.choice([True, False]),
                "created_at": created_date,
                "processing_time_ms": random.randint(100, 2000),
            }
            credit_scores.append(credit_score)

        self.db.credit_scores.insert_many(credit_scores)

    def seed_collection_cases(self, count: int):
        """Generate and insert collection case documents"""
        # Get overdue loans for collection cases
        overdue_loans = list(
            self.db.loans.find(
                {
                    "$or": [
                        {"status": "in_collections"},
                        {"status": "defaulted"},
                        {"days_past_due": {"$gt": 30}},
                    ]
                }
            )
        )

        if len(overdue_loans) < count:
            print(
                f"Warning: Only {len(overdue_loans)} overdue loans available for {count} collection cases"
            )
            count = len(overdue_loans)

        collection_cases = []

        for i in range(count):
            loan = (
                overdue_loans[i]
                if i < len(overdue_loans)
                else random.choice(overdue_loans)
            )

            opened_date = loan.get("collections_start_date") or (
                loan["due_date"] + timedelta(days=30)
            )
            case_number = (
                f"COL{datetime.now().year}{str(i).zfill(5)}{random.randint(10, 99)}"
            )

            # Collection activities
            contact_attempts = []
            num_attempts = random.randint(1, 10)
            for attempt in range(num_attempts):
                contact_attempts.append(
                    {
                        "date": opened_date + timedelta(days=random.randint(0, 90)),
                        "method": random.choice(["phone", "sms", "email", "visit"]),
                        "outcome": random.choice(
                            [
                                "no_answer",
                                "promised_payment",
                                "payment_plan",
                                "disputed",
                                "contact_made",
                            ]
                        ),
                        "notes": self.fake.sentence(),
                        "agent": f"agent_{random.randint(1, 20)}",
                    }
                )

            # Payments during collection
            payments_during_collection = []
            if random.random() < 0.4:  # 40% make some payment during collection
                num_payments = random.randint(1, 3)
                for payment in range(num_payments):
                    payments_during_collection.append(
                        {
                            "date": opened_date + timedelta(days=random.randint(5, 60)),
                            "amount": random.uniform(
                                10, loan["outstanding_balance"] * 0.5
                            ),
                            "method": random.choice(
                                ["digital_wallet", "bank_transfer", "cash_agent"]
                            ),
                        }
                    )

            collection_case = {
                "_id": ObjectId(),
                "loan_id": loan["_id"],
                "customer_id": loan["customer_id"],
                "case_number": case_number,
                "opened_date": opened_date,
                "case_status": random.choice(
                    ["open", "in_progress", "settled", "charged_off"]
                ),
                "original_debt": loan["total_amount"],
                "current_debt": loan["outstanding_balance"],
                "fees_added": random.uniform(0, 50),
                "contact_attempts": contact_attempts,
                "payments_received": payments_during_collection,
                "collection_strategy": random.choice(
                    ["phone_first", "sms_campaign", "field_visit", "legal_notice"]
                ),
                "assigned_agent": f"agent_{random.randint(1, 20)}"
                if random.random() < 0.8
                else None,
                "assigned_date": opened_date + timedelta(days=random.randint(0, 7))
                if random.random() < 0.8
                else None,
                "resolution_date": opened_date + timedelta(days=random.randint(30, 180))
                if random.random() < 0.3
                else None,
                "resolution_type": random.choice(
                    [
                        "paid_in_full",
                        "payment_plan",
                        "partial_settlement",
                        "charged_off",
                    ]
                )
                if random.random() < 0.3
                else None,
                "recovery_amount": sum(p["amount"] for p in payments_during_collection)
                if payments_during_collection
                else 0,
                "created_at": opened_date,
                "updated_at": self.fake.date_time_between(
                    start_date=opened_date, end_date="now"
                )
                if random.random() < 0.8
                else None,
                "notes": [
                    {
                        "date": opened_date + timedelta(days=random.randint(0, 30)),
                        "agent": f"agent_{random.randint(1, 20)}",
                        "note": self.fake.paragraph(),
                        "category": random.choice(
                            ["contact", "payment", "dispute", "update"]
                        ),
                    }
                    for _ in range(random.randint(1, 5))
                ],
            }
            collection_cases.append(collection_case)

        self.db.collection_cases.insert_many(collection_cases)

    def seed_compliance_records(self, count: int):
        """Generate and insert compliance record documents"""
        compliance_records = []

        # Reference all existing documents for compliance tracking
        all_refs = (
            [(ref, "customer") for ref in self.customer_ids]
            + [(ref, "loan_application") for ref in self.application_ids]
            + [(ref, "loan") for ref in self.loan_ids]
        )

        regulations = [
            "Central Bank Lending Regulation 2023",
            "Consumer Protection Act",
            "Anti-Money Laundering Law",
            "Data Protection Regulation",
            "Financial Services Authority Guidelines",
        ]

        for i in range(count):
            ref_id, ref_type = (
                random.choice(all_refs) if all_refs else (ObjectId(), "customer")
            )
            regulation = random.choice(regulations)

            # Generate reporting period (YYYY-MM format)
            period_date = self.fake.date_between(start_date="-2y", end_date="now")
            reporting_period = period_date.strftime("%Y-%m")

            # Generate compliance data based on regulation type
            if "Lending" in regulation:
                compliance_data = {
                    "loan_amount": random.uniform(50, 1500),
                    "interest_rate": random.uniform(15, 35),
                    "customer_category": random.choice(
                        ["unbanked", "underbanked", "returning"]
                    ),
                    "risk_assessment_completed": True,
                    "affordability_check": random.choice([True, False]),
                }
            elif "Consumer Protection" in regulation:
                compliance_data = {
                    "disclosure_provided": True,
                    "terms_explained": random.choice([True, False]),
                    "cooling_off_period": random.choice([True, False]),
                    "complaint_resolution_time_hours": random.randint(1, 72),
                }
            elif "Anti-Money Laundering" in regulation:
                compliance_data = {
                    "kyc_completed": random.choice([True, False]),
                    "source_of_funds_verified": random.choice([True, False]),
                    "suspicious_activity_flagged": random.choice([True, False]),
                    "reporting_threshold_exceeded": random.choice([True, False]),
                }
            else:
                compliance_data = {
                    "regulation_met": random.choice([True, False]),
                    "documentation_complete": random.choice([True, False]),
                    "audit_score": random.uniform(0.7, 1.0),
                }

            compliance_record = {
                "_id": ObjectId(),
                "record_type": regulation.lower().replace(" ", "_"),
                "reference_id": ref_id,
                "reference_type": ref_type,
                "regulation_name": regulation,
                "compliance_data": compliance_data,
                "reporting_period": reporting_period,
                "report_generated": random.choice([True, False]),
                "report_submitted": random.choice([True, False])
                if random.choice([True, False])
                else False,
                "submission_date": self.fake.date_time_between(
                    start_date=period_date, end_date="now"
                )
                if random.choice([True, False])
                else None,
                "created_at": self.fake.date_time_between(
                    start_date=period_date, end_date="now"
                ),
                "created_by": random.choice(
                    ["compliance_system", "audit_bot", "regulatory_agent"]
                ),
                "data_hash": f"hash_{uuid.uuid4().hex[:16]}"
                if random.random() < 0.8
                else None,
            }
            compliance_records.append(compliance_record)

        self.db.compliance_records.insert_many(compliance_records)

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
            # Check loan applications reference valid customers
            invalid_apps = self.db.loan_applications.count_documents(
                {"customer_id": {"$nin": self.customer_ids}}
            )
            if invalid_apps > 0:
                validation_results["referential_integrity"] = False
                validation_results["errors"].append(
                    f"Found {invalid_apps} applications with invalid customer references"
                )

            # Check loans reference valid applications and customers
            invalid_loans = self.db.loans.count_documents(
                {
                    "$or": [
                        {"customer_id": {"$nin": self.customer_ids}},
                        {"application_id": {"$nin": self.application_ids}},
                    ]
                }
            )
            if invalid_loans > 0:
                validation_results["referential_integrity"] = False
                validation_results["errors"].append(
                    f"Found {invalid_loans} loans with invalid references"
                )

        except Exception as e:
            validation_results["errors"].append(
                f"Error checking referential integrity: {e}"
            )

        # Validate indexes exist
        for (
            collection_name,
            collection_schema,
        ) in self.database_schema.collections.items():
            collection = self.db[collection_name]
            existing_indexes = {idx["name"] for idx in collection.list_indexes()}

            for index_def in collection_schema.indexes:
                if index_def.name not in existing_indexes:
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
    seeder = NeoLendBankSeeder(connection_string)

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
            "customers": 1500,
            "loan_applications": 2500,
            "loans": 1800,
            "payments": 8000,
            "credit_scores": 3000,
            "collection_cases": 200,
            "compliance_records": 500,
        },
    )
