"""
DocuSign Database Seeder

This module implements the database seeding logic for the DocuSign MongoDB database,
generating realistic sample data for accounts, users, envelopes, documents, and
complete signing workflows.
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from faker import Faker

from mimoid import DatabaseSeeder, PyObjectId
from db_schema import (
    DocuSignMongoDbSchema,
    Account,
    User,
    Template,
    Document,
    Recipient,
    Envelope,
    AuditEvent,
    Brand,
    Folder,
    AccountSettings,
    BillingInfo,
    UserPermissions,
    TemplateRecipient,
    DocumentTab,
    EnvelopeNotification,
    EnvelopeCustomField,
    AccountPlan,
    EnvelopeStatus,
    RecipientType,
    RecipientStatus,
    TabType,
    AuthenticationMethod,
    EventType,
)


logger = logging.getLogger(__name__)


class DocuSignDatabaseSeeder(DatabaseSeeder):
    """Database seeder for DocuSign MongoDB database"""
    
    def __init__(self, connection_string: str, schema: DocuSignMongoDbSchema):
        super().__init__(connection_string, schema)
        self.schema = schema
        self.fake = Faker()
        Faker.seed(42)  # For reproducible data
        
        # Get database connection
        from pymongo import MongoClient
        client = MongoClient(connection_string)
        self.db = client[schema.database_name]
        
        # Data caches
        self.accounts: List[Account] = []
        self.users: List[User] = []
        self.templates: List[Template] = []
        self.envelopes: List[Envelope] = []
        self.documents: List[Document] = []
        self.recipients: List[Recipient] = []
        self.brands: List[Brand] = []
        self.folders: List[Folder] = []
        
        # Industry-specific data
        self.industries = [
            "Real Estate", "Financial Services", "Healthcare", "Legal",
            "Insurance", "Technology", "Education", "Government",
            "Manufacturing", "Retail", "Construction", "Consulting",
            "Non-Profit", "Human Resources", "Sales"
        ]
        
        self.company_sizes = [
            "1-10", "11-50", "51-200", "201-500", "501-1000",
            "1001-5000", "5001-10000", "10000+"
        ]
        
        self.document_types = {
            "Real Estate": ["Purchase Agreement", "Lease Agreement", "Property Disclosure", "Listing Agreement"],
            "Financial Services": ["Loan Application", "Investment Agreement", "Account Opening", "Wire Transfer"],
            "Healthcare": ["Patient Consent", "HIPAA Authorization", "Treatment Plan", "Insurance Form"],
            "Legal": ["Service Agreement", "NDA", "Power of Attorney", "Settlement Agreement"],
            "Insurance": ["Policy Application", "Claim Form", "Beneficiary Designation", "Coverage Change"],
            "Technology": ["Software License", "SaaS Agreement", "Terms of Service", "Data Processing Agreement"],
            "Human Resources": ["Employment Contract", "Offer Letter", "I-9 Form", "Benefits Enrollment"],
            "Sales": ["Sales Contract", "Purchase Order", "Quote", "Service Agreement"],
        }
        
        self.tab_layouts = {
            "signature_simple": [
                {"type": TabType.SIGN_HERE, "page": 1, "x": 100, "y": 600},
                {"type": TabType.DATE_SIGNED, "page": 1, "x": 300, "y": 600},
            ],
            "signature_initials": [
                {"type": TabType.INITIAL_HERE, "page": 1, "x": 500, "y": 200},
                {"type": TabType.INITIAL_HERE, "page": 2, "x": 500, "y": 200},
                {"type": TabType.SIGN_HERE, "page": -1, "x": 100, "y": 600},
                {"type": TabType.DATE_SIGNED, "page": -1, "x": 300, "y": 600},
            ],
            "form_fields": [
                {"type": TabType.TEXT, "page": 1, "x": 100, "y": 200, "label": "Full Name"},
                {"type": TabType.EMAIL, "page": 1, "x": 100, "y": 250, "label": "Email"},
                {"type": TabType.TEXT, "page": 1, "x": 100, "y": 300, "label": "Phone"},
                {"type": TabType.DATE, "page": 1, "x": 100, "y": 350, "label": "Date of Birth"},
                {"type": TabType.CHECKBOX, "page": 1, "x": 100, "y": 400, "label": "I agree"},
                {"type": TabType.SIGN_HERE, "page": 1, "x": 100, "y": 500},
            ],
        }
    
    def seed_all_collections(self, num_records: Optional[Dict[str, int]] = None) -> Dict[str, int]:
        """Seed all collections with sample data - implements abstract method"""
        return self.seed_all()
    
    def create_indexes(self):
        """Create indexes as defined in the schema - implements abstract method"""
        # Indexes are created in main.py, so this is a no-op
        pass
    
    def clear_database(self):
        """Clear all collections - implements abstract method"""
        self._clear_all_collections()
    
    def validate_seed_data(self):
        """Validate the seeded data meets quality standards - implements abstract method"""
        # Basic validation - check counts
        for collection_name in self.schema.collections:
            count = self.db[collection_name].count_documents({})
            if count == 0 and collection_name != "audit_events":
                raise ValueError(f"Collection {collection_name} is empty after seeding")
    
    def seed_all(self) -> Dict[str, int]:
        """Seed all collections with sample data"""
        logger.info("Starting DocuSign database seeding...")
        
        # Clear existing data
        self._clear_all_collections()
        
        # Seed in dependency order
        self._seed_accounts(account_count=50)
        self._seed_brands()
        self._seed_users(avg_users_per_account=5)
        self._seed_folders()
        self._seed_templates(avg_templates_per_account=8)
        self._seed_envelopes(total_envelopes=2000)
        self._seed_audit_events()
        
        # Update account statistics
        self._update_account_stats()
        
        result = {
            "accounts": len(self.accounts),
            "users": len(self.users),
            "brands": len(self.brands),
            "folders": len(self.folders),
            "templates": len(self.templates),
            "envelopes": len(self.envelopes),
            "documents": self.db.documents.count_documents({}),
            "recipients": self.db.recipients.count_documents({}),
            "audit_events": self.db.audit_events.count_documents({}),
        }
        
        logger.info(f"Seeding completed: {result}")
        return result
    
    def _clear_all_collections(self):
        """Clear all collections before seeding"""
        from pymongo import MongoClient
        import os
        
        # Get database connection
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        db = client[self.schema.database_name]
        
        for collection_name in self.schema.collections:
            db[collection_name].delete_many({})
    
    def _seed_accounts(self, account_count: int):
        """Seed account documents"""
        logger.info(f"Seeding {account_count} accounts...")
        
        accounts = []
        plan_weights = {
            AccountPlan.PERSONAL: 0.15,
            AccountPlan.STANDARD: 0.35,
            AccountPlan.BUSINESS_PRO: 0.30,
            AccountPlan.ENTERPRISE: 0.15,
            AccountPlan.ADVANCED: 0.05,
        }
        
        for i in range(account_count):
            # Determine account type and plan
            is_business = random.random() > 0.2
            plan = random.choices(
                list(plan_weights.keys()),
                weights=list(plan_weights.values())
            )[0]
            
            # Create account
            account = Account(
                account_id=f"acc_{self.fake.uuid4()}",
                account_name=self.fake.company() if is_business else f"{self.fake.first_name()}'s Account",
                account_external_id=self.fake.uuid4() if random.random() > 0.7 else None,
                created_date=self.fake.date_time_between(start_date="-3y", end_date="-1d"),
                status=random.choices(
                    ["active", "suspended", "closed"],
                    weights=[0.9, 0.07, 0.03]
                )[0],
                admin_email=self.fake.company_email() if is_business else self.fake.email(),
                admin_name=self.fake.name(),
                company_name=self.fake.company() if is_business else None,
                company_size=random.choice(self.company_sizes) if is_business else None,
                industry=random.choice(self.industries) if is_business else None,
                phone=self.fake.phone_number() if random.random() > 0.3 else None,
                address={
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state_abbr(),
                    "zip": self.fake.zipcode(),
                    "country": "US"
                } if random.random() > 0.4 else None,
                user_count=random.randint(1, 50) if plan in [AccountPlan.ENTERPRISE, AccountPlan.ADVANCED] else random.randint(1, 10),
                api_access_enabled=plan != AccountPlan.PERSONAL,
                connect_enabled=plan in [AccountPlan.ENTERPRISE, AccountPlan.ADVANCED],
                billing_info=self._create_billing_info(plan),
                settings=self._create_account_settings(plan),
            )
            
            accounts.append(account)
        
        # Insert accounts
        if accounts:
            self.db.accounts.insert_many(
                [acc.model_dump(by_alias=True) for acc in accounts]
            )
            self.accounts = accounts
    
    def _create_billing_info(self, plan: AccountPlan) -> BillingInfo:
        """Create billing information for an account"""
        envelope_allowances = {
            AccountPlan.PERSONAL: 5,
            AccountPlan.STANDARD: 100,
            AccountPlan.BUSINESS_PRO: 500,
            AccountPlan.ENTERPRISE: 2000,
            AccountPlan.ADVANCED: 10000,
        }
        
        period_start = self.fake.date_time_between(start_date="-30d", end_date="now")
        period_end = period_start + timedelta(days=30)
        allowance = envelope_allowances[plan]
        
        return BillingInfo(
            plan_id=plan,
            billing_period_start=period_start,
            billing_period_end=period_end,
            envelope_allowance=allowance,
            envelopes_used=random.randint(0, int(allowance * 0.8)),
            additional_seats=random.randint(0, 10) if plan != AccountPlan.PERSONAL else 0,
            payment_method=random.choice(["credit_card", "invoice", "ach"]) if plan != AccountPlan.PERSONAL else None,
            next_billing_date=period_end,
            amount_due=0.0 if random.random() > 0.1 else random.uniform(100, 5000),
        )
    
    def _create_account_settings(self, plan: AccountPlan) -> AccountSettings:
        """Create account settings based on plan"""
        advanced_features = plan in [AccountPlan.ENTERPRISE, AccountPlan.ADVANCED]
        
        return AccountSettings(
            enable_sequential_signing=True,
            enable_recipient_authentication=True,
            enable_advanced_recipient_routing=advanced_features,
            enable_conditional_fields=advanced_features,
            enable_payment_processing=plan != AccountPlan.PERSONAL,
            envelope_expiration_days=random.choice([7, 14, 30, 60, 90]),
            reminder_frequency_days=random.choice([1, 2, 3, 5, 7]),
            max_reminders=random.choice([2, 3, 5, 10]),
            session_timeout_minutes=random.choice([15, 20, 30, 60]),
            require_21_cfr_part_11=random.random() > 0.9,  # Rare, for regulated industries
            enable_power_forms=advanced_features,
            enable_sms_delivery=plan != AccountPlan.PERSONAL,
        )
    
    def _seed_brands(self):
        """Seed brand documents"""
        logger.info("Seeding brands...")
        
        brands = []
        brand_themes = [
            {
                "name": "Corporate Blue",
                "primary": "#003d79",
                "secondary": "#0070c0",
                "button": "#0070c0",
            },
            {
                "name": "Modern Green",
                "primary": "#2e7d32",
                "secondary": "#4caf50",
                "button": "#4caf50",
            },
            {
                "name": "Professional Gray",
                "primary": "#424242",
                "secondary": "#757575",
                "button": "#616161",
            },
            {
                "name": "Vibrant Orange",
                "primary": "#e65100",
                "secondary": "#ff6f00",
                "button": "#ff6f00",
            },
        ]
        
        # Create brands for enterprise accounts
        for account in self.accounts:
            if account.billing_info.plan_id in [AccountPlan.ENTERPRISE, AccountPlan.ADVANCED]:
                # Default brand
                theme = random.choice(brand_themes)
                brand = Brand(
                    brand_id=f"brand_{self.fake.uuid4()}",
                    account_id=account.id,
                    brand_name=f"{account.account_name} Brand",
                    is_default=True,
                    primary_color=theme["primary"],
                    secondary_color=theme["secondary"],
                    button_color=theme["button"],
                    button_text_color="#ffffff",
                    text_color="#000000",
                    email_footer_text=f"© {datetime.now().year} {account.company_name or account.account_name}. All rights reserved.",
                    created_date=account.created_date,
                    created_by=PyObjectId(),
                    last_modified_date=self.fake.date_time_between(
                        start_date=account.created_date,
                        end_date="now"
                    ),
                )
                brands.append(brand)
                account.brand_ids.append(brand.id)
                
                # Additional brands for some accounts
                if random.random() > 0.7:
                    for i in range(random.randint(1, 3)):
                        theme = random.choice(brand_themes)
                        dept_brand = Brand(
                            brand_id=f"brand_{self.fake.uuid4()}",
                            account_id=account.id,
                            brand_name=f"{random.choice(['Sales', 'HR', 'Legal', 'Finance'])} Brand",
                            is_default=False,
                            primary_color=theme["primary"],
                            secondary_color=theme["secondary"],
                            button_color=theme["button"],
                            button_text_color="#ffffff",
                            text_color="#000000",
                            created_date=self.fake.date_time_between(
                                start_date=account.created_date,
                                end_date="now"
                            ),
                            created_by=PyObjectId(),
                            last_modified_date=self.fake.date_time_between(
                                start_date=account.created_date,
                                end_date="now"
                            ),
                        )
                        brands.append(dept_brand)
                        account.brand_ids.append(dept_brand.id)
        
        # Insert brands and update accounts
        if brands:
            self.db.brands.insert_many(
                [brand.model_dump(by_alias=True) for brand in brands]
            )
            self.brands = brands
            
            # Update accounts with brand IDs
            for account in self.accounts:
                if account.brand_ids:
                    self.db.accounts.update_one(
                        {"_id": account.id},
                        {"$set": {"brand_ids": account.brand_ids}}
                    )
    
    def _seed_users(self, avg_users_per_account: int):
        """Seed user documents"""
        logger.info("Seeding users...")
        
        users = []
        
        for account in self.accounts:
            # Determine number of users based on account plan
            if account.billing_info.plan_id == AccountPlan.PERSONAL:
                num_users = 1
            else:
                num_users = min(
                    account.user_count,
                    random.randint(1, avg_users_per_account * 2)
                )
            
            # Admin user
            admin_user = User(
                user_id=f"user_{self.fake.uuid4()}",
                account_id=account.id,
                email=account.admin_email,
                user_name=account.admin_email,
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                title=random.choice(["CEO", "President", "VP Operations", "Director", "Manager"]),
                created_date=account.created_date,
                last_login_date=self.fake.date_time_between(start_date="-7d", end_date="now"),
                status="active",
                user_type="admin",
                permissions=UserPermissions(
                    can_send_envelopes=True,
                    can_manage_account=True,
                    can_manage_templates=True,
                    can_view_reports=True,
                    can_manage_users=True,
                    can_use_api=True,
                ),
                login_count=random.randint(10, 1000),
                locale=random.choice(["en_US", "en_GB", "es_ES", "fr_FR", "de_DE"]),
                time_zone=self.fake.timezone(),
            )
            users.append(admin_user)
            
            # Regular users
            for i in range(num_users - 1):
                user_type = random.choices(
                    ["regular", "sender", "viewer"],
                    weights=[0.6, 0.3, 0.1]
                )[0]
                
                user = User(
                    user_id=f"user_{self.fake.uuid4()}",
                    account_id=account.id,
                    email=self.fake.company_email() if account.company_name else self.fake.email(),
                    user_name=self.fake.email(),
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    title=self.fake.job() if random.random() > 0.3 else None,
                    created_date=self.fake.date_time_between(
                        start_date=account.created_date,
                        end_date="now"
                    ),
                    last_login_date=self.fake.date_time_between(start_date="-30d", end_date="now") if random.random() > 0.2 else None,
                    status=random.choices(["active", "inactive"], weights=[0.9, 0.1])[0],
                    user_type=user_type,
                    permissions=self._create_user_permissions(user_type),
                    login_count=random.randint(0, 500),
                    envelopes_sent_count=random.randint(0, 200) if user_type != "viewer" else 0,
                )
                users.append(user)
        
        # Insert users
        if users:
            self.db.users.insert_many(
                [user.model_dump(by_alias=True) for user in users]
            )
            self.users = users
    
    def _create_user_permissions(self, user_type: str) -> UserPermissions:
        """Create user permissions based on user type"""
        if user_type == "admin":
            return UserPermissions(
                can_send_envelopes=True,
                can_manage_account=True,
                can_manage_templates=True,
                can_view_reports=True,
                can_manage_users=True,
                can_use_api=True,
            )
        elif user_type == "sender":
            return UserPermissions(
                can_send_envelopes=True,
                can_manage_account=False,
                can_manage_templates=True,
                can_view_reports=True,
                can_manage_users=False,
                can_use_api=random.random() > 0.5,
            )
        elif user_type == "viewer":
            return UserPermissions(
                can_send_envelopes=False,
                can_manage_account=False,
                can_manage_templates=False,
                can_view_reports=True,
                can_manage_users=False,
                can_use_api=False,
            )
        else:  # regular
            return UserPermissions(
                can_send_envelopes=True,
                can_manage_account=False,
                can_manage_templates=random.random() > 0.5,
                can_view_reports=random.random() > 0.3,
                can_manage_users=False,
                can_use_api=random.random() > 0.7,
            )
    
    def _seed_folders(self):
        """Seed folder documents"""
        logger.info("Seeding folders...")
        
        folders = []
        
        for account in self.accounts:
            # Get account users
            account_users = [u for u in self.users if u.account_id == account.id]
            if not account_users:
                continue
            
            # System folders for each user
            for user in account_users[:5]:  # Limit to first 5 users
                for folder_type in ["sentitems", "draft", "inbox"]:
                    folder = Folder(
                        folder_id=f"folder_{self.fake.uuid4()}",
                        account_id=account.id,
                        name=folder_type.capitalize(),
                        folder_type=folder_type,
                        owner_user_id=user.id,
                        is_shared=False,
                        created_date=user.created_date,
                        last_modified_date=user.created_date,
                    )
                    folders.append(folder)
                
                # Custom folders
                if random.random() > 0.5:
                    for i in range(random.randint(1, 5)):
                        folder_names = [
                            "Contracts", "HR Documents", "Legal", "Sales",
                            "Finance", "Projects", "Archive", "Templates",
                            f"Q{random.randint(1,4)} {random.randint(2020,2024)}"
                        ]
                        folder = Folder(
                            folder_id=f"folder_{self.fake.uuid4()}",
                            account_id=account.id,
                            name=random.choice(folder_names),
                            folder_type="normal",
                            owner_user_id=user.id,
                            is_shared=random.random() > 0.7,
                            shared_with_users=[u.id for u in random.sample(account_users, min(3, len(account_users)))] if random.random() > 0.7 else [],
                            created_date=self.fake.date_time_between(
                                start_date=user.created_date,
                                end_date="now"
                            ),
                            last_modified_date=self.fake.date_time_between(
                                start_date=user.created_date,
                                end_date="now"
                            ),
                        )
                        folders.append(folder)
        
        # Insert folders
        if folders:
            self.db.folders.insert_many(
                [folder.model_dump(by_alias=True) for folder in folders]
            )
            self.folders = folders
    
    def _seed_templates(self, avg_templates_per_account: int):
        """Seed template documents"""
        logger.info("Seeding templates...")
        
        templates = []
        
        for account in self.accounts:
            # Skip personal accounts with low probability
            if account.billing_info.plan_id == AccountPlan.PERSONAL and random.random() > 0.3:
                continue
            
            # Get account users who can create templates
            template_creators = [
                u for u in self.users
                if u.account_id == account.id and u.permissions.can_manage_templates
            ]
            if not template_creators:
                continue
            
            # Determine number of templates
            num_templates = random.randint(1, avg_templates_per_account * 2)
            
            # Get relevant document types for the industry
            industry = account.industry or "Sales"
            doc_types = self.document_types.get(
                industry,
                self.document_types["Sales"]
            )
            
            for i in range(num_templates):
                creator = random.choice(template_creators)
                doc_type = random.choice(doc_types)
                
                # Create template recipients
                recipient_configs = self._create_template_recipients(doc_type)
                
                template = Template(
                    template_id=f"tmpl_{self.fake.uuid4()}",
                    account_id=account.id,
                    name=f"{doc_type} Template",
                    description=f"Standard template for {doc_type.lower()} documents",
                    created_date=self.fake.date_time_between(
                        start_date=creator.created_date,
                        end_date="now"
                    ),
                    created_by=creator.id,
                    last_modified_date=self.fake.date_time_between(
                        start_date=creator.created_date,
                        end_date="now"
                    ),
                    last_used_date=self.fake.date_time_between(start_date="-30d", end_date="now") if random.random() > 0.3 else None,
                    shared=random.random() > 0.7 and account.billing_info.plan_id in [AccountPlan.ENTERPRISE, AccountPlan.ADVANCED],
                    email_subject=f"Please sign: {doc_type}",
                    email_message=f"Please review and sign the attached {doc_type.lower()}. Let me know if you have any questions.",
                    recipients=recipient_configs,
                    document_ids=[f"doc_{self.fake.uuid4()}" for _ in range(random.randint(1, 3))],
                    document_count=random.randint(1, 3),
                    enable_sequential_signing=len(recipient_configs) > 1 and random.random() > 0.3,
                    brand_id=random.choice(account.brand_ids) if account.brand_ids else None,
                    usage_count=random.randint(0, 100),
                    last_30_days_usage=random.randint(0, 20),
                    tags=[industry, doc_type, "template"],
                )
                
                templates.append(template)
        
        # Insert templates
        if templates:
            self.db.templates.insert_many(
                [tmpl.model_dump(by_alias=True) for tmpl in templates]
            )
            self.templates = templates
    
    def _create_template_recipients(self, doc_type: str) -> List[TemplateRecipient]:
        """Create template recipient configurations"""
        recipient_configs = []
        
        # Common patterns based on document type
        if "Agreement" in doc_type or "Contract" in doc_type:
            # Two-party agreement
            recipient_configs = [
                TemplateRecipient(
                    recipient_id=f"role_{self.fake.uuid4()}",
                    recipient_type=RecipientType.SIGNER,
                    role_name="Client",
                    routing_order=1,
                    authentication_methods=[AuthenticationMethod.EMAIL],
                ),
                TemplateRecipient(
                    recipient_id=f"role_{self.fake.uuid4()}",
                    recipient_type=RecipientType.SIGNER,
                    role_name="Company Representative",
                    routing_order=2,
                    authentication_methods=[AuthenticationMethod.EMAIL],
                ),
            ]
        elif "Form" in doc_type or "Application" in doc_type:
            # Single signer with CC
            recipient_configs = [
                TemplateRecipient(
                    recipient_id=f"role_{self.fake.uuid4()}",
                    recipient_type=RecipientType.SIGNER,
                    role_name="Applicant",
                    routing_order=1,
                    authentication_methods=[AuthenticationMethod.EMAIL],
                ),
                TemplateRecipient(
                    recipient_id=f"role_{self.fake.uuid4()}",
                    recipient_type=RecipientType.CARBON_COPY,
                    role_name="Administrator",
                    routing_order=2,
                ),
            ]
        else:
            # Single signer
            recipient_configs = [
                TemplateRecipient(
                    recipient_id=f"role_{self.fake.uuid4()}",
                    recipient_type=RecipientType.SIGNER,
                    role_name="Signer",
                    routing_order=1,
                    authentication_methods=[AuthenticationMethod.EMAIL],
                ),
            ]
        
        # Add authentication for some templates
        if random.random() > 0.7:
            for recipient in recipient_configs:
                if recipient.recipient_type == RecipientType.SIGNER:
                    recipient.authentication_methods.append(
                        random.choice([
                            AuthenticationMethod.ACCESS_CODE,
                            AuthenticationMethod.SMS,
                            AuthenticationMethod.ID_VERIFICATION,
                        ])
                    )
                    if AuthenticationMethod.ACCESS_CODE in recipient.authentication_methods:
                        recipient.access_code = str(random.randint(1000, 9999))
        
        return recipient_configs
    
    def _seed_envelopes(self, total_envelopes: int):
        """Seed envelope documents with complete workflows"""
        logger.info(f"Seeding {total_envelopes} envelopes...")
        
        # Batch processing
        batch_size = 100
        
        for batch_start in range(0, total_envelopes, batch_size):
            batch_end = min(batch_start + batch_size, total_envelopes)
            batch_count = batch_end - batch_start
            
            envelopes = []
            documents = []
            recipients = []
            events = []
            
            for i in range(batch_count):
                # Select random account and sender
                account = random.choice(self.accounts)
                senders = [
                    u for u in self.users
                    if u.account_id == account.id and u.permissions.can_send_envelopes
                ]
                if not senders:
                    continue
                
                sender = random.choice(senders)
                
                # Create envelope
                envelope_data = self._create_envelope(account, sender)
                if not envelope_data:
                    continue
                
                envelope, env_documents, env_recipients, env_events = envelope_data
                
                envelopes.append(envelope)
                documents.extend(env_documents)
                recipients.extend(env_recipients)
                events.extend(env_events)
            
            # Bulk insert
            if envelopes:
                self.db.envelopes.insert_many(
                    [env.model_dump(by_alias=True) for env in envelopes]
                )
                self.envelopes.extend(envelopes)
            
            if documents:
                self.db.documents.insert_many(
                    [doc.model_dump(by_alias=True) for doc in documents]
                )
                self.documents.extend(documents)
            
            if recipients:
                self.db.recipients.insert_many(
                    [rec.model_dump(by_alias=True) for rec in recipients]
                )
                self.recipients.extend(recipients)
            
            if events:
                self.db.audit_events.insert_many(
                    [evt.model_dump(by_alias=True) for evt in events]
                )
            
            logger.info(f"Seeded batch {batch_start}-{batch_end} ({len(envelopes)} envelopes)")
    
    def _create_envelope(
        self,
        account: Account,
        sender: User
    ) -> Optional[Tuple[Envelope, List[Document], List[Recipient], List[AuditEvent]]]:
        """Create a complete envelope with documents, recipients, and events"""
        
        # Envelope timing
        created_date = self.fake.date_time_between(start_date="-90d", end_date="now")
        
        # Determine envelope status and progression
        status_weights = {
            EnvelopeStatus.COMPLETED: 0.6,
            EnvelopeStatus.SENT: 0.15,
            EnvelopeStatus.DELIVERED: 0.1,
            EnvelopeStatus.SIGNED: 0.05,
            EnvelopeStatus.CREATED: 0.05,
            EnvelopeStatus.DECLINED: 0.03,
            EnvelopeStatus.VOIDED: 0.02,
        }
        status = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values())
        )[0]
        
        # Select template or create from scratch
        use_template = random.random() > 0.3
        template = None
        if use_template:
            account_templates = [t for t in self.templates if t.account_id == account.id]
            if account_templates:
                template = random.choice(account_templates)
        
        # Create envelope
        envelope = Envelope(
            envelope_id=f"env_{self.fake.uuid4()}",
            account_id=account.id,
            status=status,
            created_date=created_date,
            email_subject=template.email_subject if template else f"Please sign: {random.choice(['Contract', 'Agreement', 'Form', 'Document'])}",
            email_message=template.email_message if template else "Please review and sign the attached document.",
            sender_user_id=sender.id,
            sender_name=f"{sender.first_name} {sender.last_name}",
            sender_email=sender.email,
            template_id=template.id if template else None,
            notification=EnvelopeNotification(
                use_account_defaults=random.random() > 0.2,
                reminder_enabled=True,
                reminder_delay_days=random.choice([1, 2, 3]),
                reminder_frequency_days=random.choice([2, 3, 5]),
                expiration_enabled=True,
                expiration_days=random.choice([7, 14, 30, 60]),
            ),
            brand_id=random.choice(account.brand_ids) if account.brand_ids else None,
            enable_sequential_signing=random.random() > 0.3,
            transaction_id=self.fake.uuid4() if random.random() > 0.5 else None,
        )
        
        # Create documents
        num_documents = template.document_count if template else random.randint(1, 3)
        documents = []
        for i in range(num_documents):
            doc = self._create_document(envelope, i + 1)
            documents.append(doc)
            envelope.document_ids.append(doc.document_id)
        envelope.document_count = len(documents)
        
        # Create recipients
        if template:
            recipients_data = self._create_recipients_from_template(envelope, template)
        else:
            recipients_data = self._create_recipients(envelope)
        
        recipients = recipients_data
        envelope.recipient_count = len(recipients)
        envelope.signers_count = len([r for r in recipients if r.recipient_type == RecipientType.SIGNER])
        
        # Create workflow events based on status
        events = self._create_envelope_events(envelope, recipients, created_date)
        
        # Update envelope dates based on events
        self._update_envelope_dates(envelope, events)
        
        # Update recipient statuses based on envelope status
        self._update_recipient_statuses(envelope, recipients)
        
        # Calculate completion metrics
        if envelope.status == EnvelopeStatus.COMPLETED and envelope.completed_date and envelope.sent_date:
            envelope.days_to_complete = (envelope.completed_date - envelope.sent_date).days
        
        # Check expiration
        if envelope.status in [EnvelopeStatus.SENT, EnvelopeStatus.DELIVERED] and envelope.sent_date:
            days_since_sent = (datetime.now() - envelope.sent_date).days
            if days_since_sent > envelope.notification.expiration_days:
                envelope.is_expired = True
        
        # Add custom fields
        if random.random() > 0.7:
            envelope.custom_fields = [
                EnvelopeCustomField(
                    field_id=f"field_{self.fake.uuid4()}",
                    name=random.choice(["Department", "Project", "Cost Center", "Reference"]),
                    value=random.choice(["Sales", "HR", "Legal", "Finance", "Project-123", "CC-456"]),
                    required=random.random() > 0.5,
                )
                for _ in range(random.randint(1, 3))
            ]
        
        return envelope, documents, recipients, events
    
    def _create_document(self, envelope: Envelope, order: int) -> Document:
        """Create a document with tabs"""
        doc_names = [
            "Service Agreement", "Purchase Order", "NDA",
            "Contract", "Terms and Conditions", "Invoice",
            "Application Form", "Consent Form", "Disclosure"
        ]
        
        doc = Document(
            document_id=f"doc_{self.fake.uuid4()}",
            envelope_id=envelope.id,
            name=random.choice(doc_names),
            file_extension="pdf",
            document_order=order,
            content_type="application/pdf",
            content_bytes=random.randint(50000, 500000),  # 50KB - 500KB
            content_location=f"s3://docusign-docs/{envelope.envelope_id}/{self.fake.uuid4()}.pdf",
            page_count=random.randint(1, 10),
            created_date=envelope.created_date,
        )
        
        # Add tabs based on layout
        layout = random.choice(list(self.tab_layouts.values()))
        for tab_config in layout:
            tab = DocumentTab(
                tab_id=f"tab_{self.fake.uuid4()}",
                tab_type=tab_config["type"],
                tab_label=tab_config.get("label", tab_config["type"].value),
                page_number=tab_config["page"] if tab_config["page"] > 0 else doc.page_count,
                x_position=tab_config["x"],
                y_position=tab_config["y"],
                width=tab_config.get("width", 100),
                height=tab_config.get("height", 20),
                is_required=True,
            )
            
            # Add validation for certain tab types
            if tab.tab_type == TabType.EMAIL:
                tab.validation_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                tab.validation_message = "Please enter a valid email address"
            elif tab.tab_type == TabType.NUMBER:
                tab.validation_pattern = r"^\d+$"
                tab.validation_message = "Please enter numbers only"
            
            doc.tabs.append(tab)
        
        return doc
    
    def _create_recipients(self, envelope: Envelope) -> List[Recipient]:
        """Create recipients for an envelope"""
        recipients = []
        
        # Number of signers
        num_signers = random.choices([1, 2, 3, 4], weights=[0.4, 0.4, 0.15, 0.05])[0]
        
        # Create signers
        for i in range(num_signers):
            recipient = Recipient(
                recipient_id=f"rec_{self.fake.uuid4()}",
                envelope_id=envelope.id,
                email=self.fake.email(),
                name=self.fake.name(),
                recipient_type=RecipientType.SIGNER,
                routing_order=i + 1,
                status=RecipientStatus.CREATED,
                authentication_methods=[AuthenticationMethod.EMAIL],
            )
            
            # Add additional authentication
            if random.random() > 0.8:
                auth_method = random.choice([
                    AuthenticationMethod.ACCESS_CODE,
                    AuthenticationMethod.SMS,
                    AuthenticationMethod.ID_VERIFICATION,
                ])
                recipient.authentication_methods.append(auth_method)
                
                if auth_method == AuthenticationMethod.ACCESS_CODE:
                    recipient.access_code = str(random.randint(1000, 9999))
                elif auth_method == AuthenticationMethod.SMS:
                    recipient.phone_number = self.fake.phone_number()
            
            recipients.append(recipient)
        
        # Add CC recipients
        if random.random() > 0.5:
            for i in range(random.randint(1, 2)):
                cc_recipient = Recipient(
                    recipient_id=f"rec_{self.fake.uuid4()}",
                    envelope_id=envelope.id,
                    email=self.fake.email(),
                    name=self.fake.name(),
                    recipient_type=RecipientType.CARBON_COPY,
                    routing_order=num_signers + i + 1,
                    status=RecipientStatus.CREATED,
                    authentication_methods=[AuthenticationMethod.EMAIL],
                )
                recipients.append(cc_recipient)
        
        return recipients
    
    def _create_recipients_from_template(
        self,
        envelope: Envelope,
        template: Template
    ) -> List[Recipient]:
        """Create recipients based on template roles"""
        recipients = []
        
        for template_recipient in template.recipients:
            recipient = Recipient(
                recipient_id=f"rec_{self.fake.uuid4()}",
                envelope_id=envelope.id,
                email=self.fake.email(),
                name=self.fake.name(),
                recipient_type=template_recipient.recipient_type,
                routing_order=template_recipient.routing_order,
                status=RecipientStatus.CREATED,
                authentication_methods=template_recipient.authentication_methods.copy(),
                access_code=template_recipient.access_code,
            )
            
            if AuthenticationMethod.SMS in recipient.authentication_methods:
                recipient.phone_number = self.fake.phone_number()
            
            recipients.append(recipient)
        
        return recipients
    
    def _create_envelope_events(
        self,
        envelope: Envelope,
        recipients: List[Recipient],
        start_date: datetime
    ) -> List[AuditEvent]:
        """Create audit events for envelope workflow"""
        events = []
        current_time = start_date
        
        # Envelope created event
        events.append(AuditEvent(
            event_id=f"evt_{self.fake.uuid4()}",
            envelope_id=envelope.id,
            event_type=EventType.ENVELOPE_CREATED,
            timestamp=current_time,
            user_id=envelope.sender_user_id,
            email=envelope.sender_email,
            name=envelope.sender_name,
            details={"action": "created", "status": "created"},
        ))
        
        # Progress through statuses based on final status
        if envelope.status != EnvelopeStatus.CREATED:
            # Envelope sent
            current_time += timedelta(minutes=random.randint(1, 60))
            events.append(AuditEvent(
                event_id=f"evt_{self.fake.uuid4()}",
                envelope_id=envelope.id,
                event_type=EventType.ENVELOPE_SENT,
                timestamp=current_time,
                user_id=envelope.sender_user_id,
                email=envelope.sender_email,
                name=envelope.sender_name,
                details={"action": "sent", "recipient_count": len(recipients)},
            ))
            
            # Process recipients in routing order
            sorted_recipients = sorted(recipients, key=lambda r: r.routing_order)
            
            for recipient in sorted_recipients:
                if envelope.status in [EnvelopeStatus.DECLINED, EnvelopeStatus.VOIDED]:
                    break
                
                # Recipient events based on envelope progression
                if envelope.status in [EnvelopeStatus.DELIVERED, EnvelopeStatus.SIGNED, EnvelopeStatus.COMPLETED]:
                    # Delivered
                    current_time += timedelta(minutes=random.randint(5, 120))
                    events.append(AuditEvent(
                        event_id=f"evt_{self.fake.uuid4()}",
                        envelope_id=envelope.id,
                        event_type=EventType.RECIPIENT_DELIVERED,
                        timestamp=current_time,
                        recipient_id=recipient.recipient_id,
                        email=recipient.email,
                        name=recipient.name,
                        details={"routing_order": recipient.routing_order},
                    ))
                    recipient.delivered_date = current_time
                    
                    if envelope.status in [EnvelopeStatus.SIGNED, EnvelopeStatus.COMPLETED]:
                        # Viewed
                        current_time += timedelta(minutes=random.randint(10, 240))
                        events.append(AuditEvent(
                            event_id=f"evt_{self.fake.uuid4()}",
                            envelope_id=envelope.id,
                            event_type=EventType.RECIPIENT_VIEWED,
                            timestamp=current_time,
                            recipient_id=recipient.recipient_id,
                            email=recipient.email,
                            name=recipient.name,
                            ip_address=self.fake.ipv4(),
                            user_agent=self.fake.user_agent(),
                            details={"pages_viewed": random.randint(1, 10)},
                        ))
                        
                        # Only signers sign
                        if recipient.recipient_type == RecipientType.SIGNER:
                            # Authentication
                            if len(recipient.authentication_methods) > 1:
                                current_time += timedelta(minutes=random.randint(1, 5))
                                events.append(AuditEvent(
                                    event_id=f"evt_{self.fake.uuid4()}",
                                    envelope_id=envelope.id,
                                    event_type=EventType.AUTHENTICATION_PASSED,
                                    timestamp=current_time,
                                    recipient_id=recipient.recipient_id,
                                    email=recipient.email,
                                    name=recipient.name,
                                    authentication_method=recipient.authentication_methods[1],
                                    details={"method": recipient.authentication_methods[1].value},
                                ))
                            
                            # Signed
                            current_time += timedelta(minutes=random.randint(5, 30))
                            events.append(AuditEvent(
                                event_id=f"evt_{self.fake.uuid4()}",
                                envelope_id=envelope.id,
                                event_type=EventType.RECIPIENT_SIGNED,
                                timestamp=current_time,
                                recipient_id=recipient.recipient_id,
                                email=recipient.email,
                                name=recipient.name,
                                ip_address=self.fake.ipv4(),
                                geo_location={
                                    "city": self.fake.city(),
                                    "state": self.fake.state_abbr(),
                                    "country": "US",
                                },
                                details={"signature_type": "electronic"},
                            ))
                            recipient.signed_date = current_time
            
            # Final envelope status events
            if envelope.status == EnvelopeStatus.COMPLETED:
                current_time += timedelta(minutes=random.randint(1, 10))
                events.append(AuditEvent(
                    event_id=f"evt_{self.fake.uuid4()}",
                    envelope_id=envelope.id,
                    event_type=EventType.ENVELOPE_COMPLETED,
                    timestamp=current_time,
                    details={"completion_time_minutes": int((current_time - start_date).total_seconds() / 60)},
                ))
            elif envelope.status == EnvelopeStatus.DECLINED:
                decline_recipient = random.choice([r for r in recipients if r.recipient_type == RecipientType.SIGNER])
                current_time += timedelta(minutes=random.randint(60, 1440))
                events.append(AuditEvent(
                    event_id=f"evt_{self.fake.uuid4()}",
                    envelope_id=envelope.id,
                    event_type=EventType.ENVELOPE_DECLINED,
                    timestamp=current_time,
                    recipient_id=decline_recipient.recipient_id,
                    email=decline_recipient.email,
                    name=decline_recipient.name,
                    details={"reason": random.choice(["Terms not acceptable", "Incorrect information", "Changed mind"])},
                ))
            elif envelope.status == EnvelopeStatus.VOIDED:
                current_time += timedelta(minutes=random.randint(60, 2880))
                events.append(AuditEvent(
                    event_id=f"evt_{self.fake.uuid4()}",
                    envelope_id=envelope.id,
                    event_type=EventType.ENVELOPE_VOIDED,
                    timestamp=current_time,
                    user_id=envelope.sender_user_id,
                    email=envelope.sender_email,
                    name=envelope.sender_name,
                    details={"reason": random.choice(["Cancelled by sender", "Document error", "Wrong recipient"])},
                ))
        
        return events
    
    def _update_envelope_dates(self, envelope: Envelope, events: List[AuditEvent]):
        """Update envelope dates based on events"""
        for event in events:
            if event.event_type == EventType.ENVELOPE_SENT:
                envelope.sent_date = event.timestamp
            # Note: Envelope delivered is handled at recipient level
            elif event.event_type == EventType.ENVELOPE_COMPLETED:
                envelope.completed_date = event.timestamp
            elif event.event_type == EventType.ENVELOPE_DECLINED:
                envelope.declined_date = event.timestamp
            elif event.event_type == EventType.ENVELOPE_VOIDED:
                envelope.voided_date = event.timestamp
                envelope.voided_reason = event.details.get("reason")
    
    def _update_recipient_statuses(self, envelope: Envelope, recipients: List[Recipient]):
        """Update recipient statuses based on envelope status"""
        for recipient in recipients:
            if envelope.status == EnvelopeStatus.CREATED:
                recipient.status = RecipientStatus.CREATED
            elif envelope.status == EnvelopeStatus.SENT:
                recipient.status = RecipientStatus.SENT
                recipient.sent_date = envelope.sent_date
            elif envelope.status == EnvelopeStatus.DELIVERED:
                recipient.status = RecipientStatus.DELIVERED
                recipient.sent_date = envelope.sent_date
                if not recipient.delivered_date:
                    recipient.delivered_date = envelope.sent_date + timedelta(minutes=random.randint(5, 60))
            elif envelope.status in [EnvelopeStatus.SIGNED, EnvelopeStatus.COMPLETED]:
                recipient.status = RecipientStatus.COMPLETED
                recipient.sent_date = envelope.sent_date
                if not recipient.delivered_date:
                    recipient.delivered_date = envelope.sent_date + timedelta(minutes=random.randint(5, 60))
                if recipient.recipient_type == RecipientType.SIGNER and not recipient.signed_date:
                    recipient.signed_date = recipient.delivered_date + timedelta(minutes=random.randint(10, 120))
                recipient.completed_date = recipient.signed_date or recipient.delivered_date
            elif envelope.status == EnvelopeStatus.DECLINED:
                # Some recipients might have signed before decline
                if random.random() > 0.5 and recipient.recipient_type == RecipientType.SIGNER:
                    recipient.status = RecipientStatus.DECLINED
                    recipient.declined_date = envelope.declined_date
                    recipient.declined_reason = "Envelope declined"
            elif envelope.status == EnvelopeStatus.VOIDED:
                recipient.status = RecipientStatus.DECLINED
                recipient.declined_reason = "Envelope voided"
        
        # Update completed signers count
        envelope.completed_signers = len([
            r for r in recipients
            if r.recipient_type == RecipientType.SIGNER and r.status == RecipientStatus.COMPLETED
        ])
    
    def _seed_audit_events(self):
        """Additional audit events are created with envelopes"""
        logger.info("Audit events created with envelopes")
    
    def _update_account_stats(self):
        """Update account statistics based on seeded data"""
        logger.info("Updating account statistics...")
        
        for account in self.accounts:
            # Count envelopes
            total_sent = self.db.envelopes.count_documents({
                "account_id": account.id,
                "status": {"$ne": EnvelopeStatus.CREATED.value}
            })
            
            total_completed = self.db.envelopes.count_documents({
                "account_id": account.id,
                "status": EnvelopeStatus.COMPLETED.value
            })
            
            # Get last activity
            last_envelope = self.db.envelopes.find_one(
                {"account_id": account.id},
                sort=[("created_date", -1)]
            )
            
            # Update account
            update_data = {
                "total_envelopes_sent": total_sent,
                "total_envelopes_completed": total_completed,
            }
            
            if last_envelope:
                update_data["last_activity_date"] = last_envelope["created_date"]
            
            self.db.accounts.update_one(
                {"_id": account.id},
                {"$set": update_data}
            )
        
        # Update user stats
        for user in self.users:
            if user.permissions.can_send_envelopes:
                sent_count = self.db.envelopes.count_documents({
                    "sender_user_id": user.id
                })
                
                last_sent = self.db.envelopes.find_one(
                    {"sender_user_id": user.id},
                    sort=[("created_date", -1)]
                )
                
                update_data = {"envelopes_sent_count": sent_count}
                if last_sent:
                    update_data["last_sent_date"] = last_sent["created_date"]
                
                self.db.users.update_one(
                    {"_id": user.id},
                    {"$set": update_data}
                )
        
        # Update template usage
        for template in self.templates:
            usage_count = self.db.envelopes.count_documents({
                "template_id": template.id
            })
            
            last_30_days = self.db.envelopes.count_documents({
                "template_id": template.id,
                "created_date": {"$gte": datetime.now() - timedelta(days=30)}
            })
            
            self.db.templates.update_one(
                {"_id": template.id},
                {"$set": {
                    "usage_count": usage_count,
                    "last_30_days_usage": last_30_days
                }}
            )