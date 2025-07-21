"""Database schema for NeoLend Bank - Digital Lending Platform"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field, EmailStr, validator
from enum import Enum
from decimal import Decimal

# Import base types from mimoid package
from mimoid import (
    IndexDirection,
    IndexDefinition,
    BaseCollectionSchema,
    BaseMongoDbSchema,
    PyObjectId,
    BaseMongoDbDocumentSchema,
)


# Enums for constrained fields
class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class LoanStatus(str, Enum):
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    DEFAULTED = "defaulted"
    CHARGED_OFF = "charged_off"
    IN_COLLECTIONS = "in_collections"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    MOBILE_MONEY = "mobile_money"
    CASH_AGENT = "cash_agent"
    DEBIT_CARD = "debit_card"


class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DataSourceType(str, Enum):
    DIRECT_INPUT = "direct_input"
    SOCIAL_MEDIA = "social_media"
    DEVICE_DATA = "device_data"
    BEHAVIORAL = "behavioral"
    EXTERNAL_API = "external_api"
    THIRD_PARTY = "third_party"


# Document schemas
class Customer(BaseMongoDbDocumentSchema):
    # Core identity
    phone_number: str = Field(
        ..., description="Primary phone number (unique identifier)"
    )
    email: Optional[EmailStr] = Field(None, description="Email address if available")
    national_id: Optional[str] = Field(
        None, description="National ID or similar identifier"
    )

    # Personal information
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: Optional[datetime] = Field(None)
    gender: Optional[str] = Field(None, max_length=20)

    # Address information
    address: Dict[str, Any] = Field(default={}, description="Address details")
    location_data: Dict[str, Any] = Field(
        default={}, description="GPS and location history"
    )

    # Financial profile
    monthly_income: Optional[float] = Field(None, ge=0)
    employment_status: Optional[str] = Field(None, max_length=50)
    employer_name: Optional[str] = Field(None, max_length=200)
    bank_account_verified: bool = Field(default=False)

    # Alternative data - flexible schema for various data sources
    social_media_data: Dict[str, Any] = Field(
        default={}, description="Social media profile analysis"
    )
    behavioral_data: Dict[str, Any] = Field(
        default={}, description="App usage and behavior patterns"
    )
    device_data: Dict[str, Any] = Field(
        default={}, description="Device fingerprinting data"
    )
    network_data: Dict[str, Any] = Field(
        default={}, description="Social network and connections"
    )

    # Computed scores and metrics
    current_credit_score: Optional[float] = Field(None, ge=0, le=1000)
    risk_level: Optional[RiskLevel] = Field(None)
    fraud_score: Optional[float] = Field(None, ge=0, le=100)

    # Customer lifecycle
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = Field(None)
    kyc_completed: bool = Field(default=False)
    kyc_completion_date: Optional[datetime] = Field(None)

    # Consent and privacy
    data_consent: Dict[str, bool] = Field(
        default={}, description="Consent for different data types"
    )
    marketing_consent: bool = Field(default=False)

    # Summary metrics (computed)
    total_loans: int = Field(default=0, ge=0)
    total_loan_amount: float = Field(default=0.0, ge=0)
    repayment_rate: Optional[float] = Field(None, ge=0, le=1)
    days_since_last_loan: Optional[int] = Field(None, ge=0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    data_sources: List[DataSourceType] = Field(
        default=[], description="Sources of customer data"
    )


class LoanApplication(BaseMongoDbDocumentSchema):
    customer_id: PyObjectId = Field(..., description="Reference to customer")

    # Application details
    requested_amount: float = Field(
        ..., ge=50, le=1500, description="Requested loan amount"
    )
    loan_purpose: str = Field(..., max_length=200, description="Purpose of the loan")
    requested_term_days: int = Field(
        ..., ge=7, le=365, description="Requested loan term in days"
    )

    # Application data (flexible schema)
    application_data: Dict[str, Any] = Field(
        ..., description="Complete application form data"
    )
    supporting_documents: List[Dict[str, Any]] = Field(
        default=[], description="Document uploads and metadata"
    )

    # Alternative data collected at application time
    device_fingerprint: Dict[str, Any] = Field(
        default={}, description="Device information during application"
    )
    session_data: Dict[str, Any] = Field(
        default={}, description="User session behavior data"
    )
    geolocation: Dict[str, Any] = Field(
        default={}, description="Location data during application"
    )

    # Processing information
    status: ApplicationStatus = Field(default=ApplicationStatus.SUBMITTED)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(None)
    decision_date: Optional[datetime] = Field(None)

    # Credit scoring results
    credit_score: Optional[float] = Field(None, description="AI-generated credit score")
    risk_assessment: Dict[str, Any] = Field(
        default={}, description="Detailed risk analysis"
    )
    decision_factors: List[Dict[str, Any]] = Field(
        default=[], description="Factors that influenced decision"
    )
    model_version: Optional[str] = Field(None, description="Credit model version used")

    # Decision outcome
    approved_amount: Optional[float] = Field(None, ge=0)
    approved_term_days: Optional[int] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    rejection_reason: Optional[str] = Field(None, max_length=500)

    # Metadata
    processed_by: Optional[str] = Field(
        None, description="System or user that processed application"
    )
    notes: Optional[str] = Field(None, max_length=1000)


class Loan(BaseMongoDbDocumentSchema):
    customer_id: PyObjectId = Field(..., description="Reference to customer")
    application_id: PyObjectId = Field(
        ..., description="Reference to original application"
    )

    # Loan terms
    principal_amount: float = Field(..., ge=0, description="Original loan amount")
    interest_rate: float = Field(
        ..., ge=0, le=100, description="Annual interest rate percentage"
    )
    term_days: int = Field(..., ge=1, description="Loan term in days")

    # Calculated amounts
    total_amount: float = Field(..., ge=0, description="Principal + interest")
    daily_interest: float = Field(..., ge=0, description="Daily interest amount")

    # Payment schedule
    due_date: datetime = Field(..., description="Final due date")
    payment_schedule: List[Dict[str, Any]] = Field(
        default=[], description="Planned payment schedule"
    )

    # Current status
    status: LoanStatus = Field(default=LoanStatus.ACTIVE)
    disbursed_at: Optional[datetime] = Field(None)
    disbursed_amount: Optional[float] = Field(None, ge=0)
    disbursement_method: Optional[PaymentMethod] = Field(None)

    # Payment tracking
    total_paid: float = Field(default=0.0, ge=0)
    principal_paid: float = Field(default=0.0, ge=0)
    interest_paid: float = Field(default=0.0, ge=0)
    fees_paid: float = Field(default=0.0, ge=0)
    outstanding_balance: float = Field(..., ge=0)

    # Performance metrics
    days_past_due: int = Field(default=0, ge=0)
    payment_count: int = Field(default=0, ge=0)
    missed_payments: int = Field(default=0, ge=0)
    last_payment_date: Optional[datetime] = Field(None)

    # Risk and collections
    current_risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    in_collections: bool = Field(default=False)
    collections_start_date: Optional[datetime] = Field(None)

    # Closure information
    closed_at: Optional[datetime] = Field(None)
    closure_reason: Optional[str] = Field(None, max_length=200)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Payment(BaseMongoDbDocumentSchema):
    loan_id: PyObjectId = Field(..., description="Reference to loan")
    customer_id: PyObjectId = Field(..., description="Reference to customer")

    # Payment details
    amount: float = Field(..., ge=0, description="Payment amount")
    payment_method: PaymentMethod = Field(...)
    payment_reference: Optional[str] = Field(
        None, description="External payment reference"
    )

    # Payment breakdown
    principal_portion: float = Field(default=0.0, ge=0)
    interest_portion: float = Field(default=0.0, ge=0)
    fees_portion: float = Field(default=0.0, ge=0)

    # Status and timing
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    scheduled_date: Optional[datetime] = Field(None)
    processed_date: Optional[datetime] = Field(None)
    value_date: Optional[datetime] = Field(None)

    # Payment processing
    payment_processor: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(
        None, description="Payment processor transaction ID"
    )
    failure_reason: Optional[str] = Field(None, max_length=500)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(
        None, description="User or system that created payment"
    )
    notes: Optional[str] = Field(None, max_length=500)


class CreditScore(BaseMongoDbDocumentSchema):
    customer_id: PyObjectId = Field(..., description="Reference to customer")

    # Score details
    score: float = Field(..., ge=0, le=1000, description="Credit score value")
    confidence_level: float = Field(
        ..., ge=0, le=1, description="Model confidence in score"
    )
    risk_level: RiskLevel = Field(...)

    # Model information
    model_version: str = Field(..., description="Version of the credit model used")
    model_features: Dict[str, Any] = Field(
        ..., description="Features and weights used in scoring"
    )

    # Input data summary
    data_completeness: float = Field(
        ..., ge=0, le=1, description="Percentage of expected data available"
    )
    data_sources_used: List[DataSourceType] = Field(
        ..., description="Data sources included in scoring"
    )
    alternative_data_weight: float = Field(
        default=0.0, ge=0, le=1, description="Weight of alternative vs traditional data"
    )

    # Risk factors
    top_risk_factors: List[str] = Field(
        default=[], description="Primary risk factors identified"
    )
    protective_factors: List[str] = Field(
        default=[], description="Factors that reduce risk"
    )

    # Scoring context
    trigger_event: str = Field(..., description="What triggered this scoring event")
    application_id: Optional[PyObjectId] = Field(
        None, description="Associated loan application if applicable"
    )

    # Validity and expiration
    valid_until: datetime = Field(..., description="When this score expires")
    is_current: bool = Field(
        default=True, description="Is this the current active score"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[int] = Field(
        None, description="Time taken to generate score"
    )


class CollectionCase(BaseMongoDbDocumentSchema):
    loan_id: PyObjectId = Field(..., description="Reference to loan")
    customer_id: PyObjectId = Field(..., description="Reference to customer")

    # Case details
    case_number: str = Field(..., description="Unique collection case identifier")
    opened_date: datetime = Field(default_factory=datetime.utcnow)
    case_status: str = Field(default="open", max_length=50)

    # Debt information
    original_debt: float = Field(..., ge=0)
    current_debt: float = Field(..., ge=0)
    fees_added: float = Field(default=0.0, ge=0)

    # Collection activities
    contact_attempts: List[Dict[str, Any]] = Field(
        default=[], description="Record of contact attempts"
    )
    payments_received: List[Dict[str, Any]] = Field(
        default=[], description="Payments during collection"
    )
    collection_strategy: str = Field(..., max_length=100)

    # Assignment
    assigned_agent: Optional[str] = Field(None, description="Collection agent assigned")
    assigned_date: Optional[datetime] = Field(None)

    # Resolution
    resolution_date: Optional[datetime] = Field(None)
    resolution_type: Optional[str] = Field(None, max_length=100)
    recovery_amount: Optional[float] = Field(None, ge=0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    notes: List[Dict[str, Any]] = Field(
        default=[], description="Collection notes and activities"
    )


class ComplianceRecord(BaseMongoDbDocumentSchema):
    # Record identification
    record_type: str = Field(
        ..., max_length=100, description="Type of compliance record"
    )
    reference_id: PyObjectId = Field(
        ..., description="Reference to related document (loan, customer, etc.)"
    )
    reference_type: str = Field(
        ..., max_length=50, description="Type of referenced document"
    )

    # Compliance data
    regulation_name: str = Field(..., max_length=200)
    compliance_data: Dict[str, Any] = Field(
        ..., description="Regulatory compliance information"
    )

    # Reporting
    reporting_period: str = Field(
        ..., description="Period this record covers (YYYY-MM)"
    )
    report_generated: bool = Field(default=False)
    report_submitted: bool = Field(default=False)
    submission_date: Optional[datetime] = Field(None)

    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="System or user that created record")
    data_hash: Optional[str] = Field(
        None, description="Hash for data integrity verification"
    )


# Collection schema definitions
class CustomerCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Customer.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="phone_unique",
            keys={"phone_number": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="email_index", keys={"email": IndexDirection.ASCENDING}, sparse=True
        ),
        IndexDefinition(
            name="national_id_index",
            keys={"national_id": IndexDirection.ASCENDING},
            sparse=True,
        ),
        IndexDefinition(
            name="risk_score_index",
            keys={
                "risk_level": IndexDirection.ASCENDING,
                "current_credit_score": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="activity_index",
            keys={"last_activity": IndexDirection.DESCENDING},
            sparse=True,
        ),
        IndexDefinition(
            name="name_text_search",
            keys={"first_name": IndexDirection.TEXT, "last_name": IndexDirection.TEXT},
        ),
    ]
    description: str = "Customer profiles with traditional and alternative credit data"


class LoanApplicationCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = LoanApplication.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="customer_applications",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "submitted_at": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="status_date_index",
            keys={
                "status": IndexDirection.ASCENDING,
                "submitted_at": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="decision_date_index",
            keys={"decision_date": IndexDirection.DESCENDING},
            sparse=True,
        ),
        IndexDefinition(
            name="amount_score_index",
            keys={
                "requested_amount": IndexDirection.DESCENDING,
                "credit_score": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Loan applications with credit scoring data"


class LoanCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Loan.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="customer_loans",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="status_due_date",
            keys={
                "status": IndexDirection.ASCENDING,
                "due_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="overdue_loans",
            keys={
                "days_past_due": IndexDirection.DESCENDING,
                "outstanding_balance": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="application_reference",
            keys={"application_id": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="collections_index",
            keys={
                "in_collections": IndexDirection.ASCENDING,
                "collections_start_date": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Active and historical loan records"


class PaymentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Payment.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="loan_payments",
            keys={
                "loan_id": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="customer_payments",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "processed_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="status_date_index",
            keys={
                "status": IndexDirection.ASCENDING,
                "scheduled_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="payment_method_index",
            keys={"payment_method": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="transaction_reference",
            keys={"transaction_id": IndexDirection.ASCENDING},
            sparse=True,
        ),
    ]
    description: str = "Payment transactions and history"


class CreditScoreCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = CreditScore.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="customer_scores",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="current_scores",
            keys={
                "is_current": IndexDirection.ASCENDING,
                "customer_id": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="score_range_index",
            keys={
                "score": IndexDirection.DESCENDING,
                "confidence_level": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="model_version_index", keys={"model_version": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="expiration_index", keys={"valid_until": IndexDirection.ASCENDING}
        ),
    ]
    description: str = "AI-generated credit scores and risk assessments"


class CollectionCaseCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = CollectionCase.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="case_number_unique",
            keys={"case_number": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="loan_collections", keys={"loan_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="customer_collections",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "opened_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="status_agent_index",
            keys={
                "case_status": IndexDirection.ASCENDING,
                "assigned_agent": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="debt_amount_index", keys={"current_debt": IndexDirection.DESCENDING}
        ),
    ]
    description: str = "Collection cases for overdue loans"


class ComplianceRecordCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = ComplianceRecord.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="record_type_period",
            keys={
                "record_type": IndexDirection.ASCENDING,
                "reporting_period": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="reference_index",
            keys={
                "reference_type": IndexDirection.ASCENDING,
                "reference_id": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="reporting_status",
            keys={
                "report_submitted": IndexDirection.ASCENDING,
                "reporting_period": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="regulation_index", keys={"regulation_name": IndexDirection.ASCENDING}
        ),
    ]
    description: str = "Regulatory compliance and audit records"


# Complete database schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "customers": CustomerCollectionSchema(),
        "loan_applications": LoanApplicationCollectionSchema(),
        "loans": LoanCollectionSchema(),
        "payments": PaymentCollectionSchema(),
        "credit_scores": CreditScoreCollectionSchema(),
        "collection_cases": CollectionCaseCollectionSchema(),
        "compliance_records": ComplianceRecordCollectionSchema(),
    }
    database_name: str = "neolend_bank"
    description: str = (
        "Digital lending platform with AI-powered alternative credit scoring"
    )


# Export the database schema
database_schema = MongoDbDataSchema()
