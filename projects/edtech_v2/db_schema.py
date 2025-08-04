"""
Brazilian EdTech Platform - MongoDB Schema Definition
Database: brazilian_edtech
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal, Type
from enum import Enum
from pydantic import Field, field_validator, ConfigDict
from decimal import Decimal

from mimoid.schema_types import (
    BaseMongoDbSchema, BaseCollectionSchema, BaseMongoDbDocumentSchema,
    IndexDefinition, IndexDirection, PyObjectId
)
from mimoid.seeder_base import DatabaseSeeder


# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    APPLICANT = "applicant"
    STAFF = "staff"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    INSTITUTION_ADMIN = "institution_admin"


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    DOCUMENTS_PENDING = "documents_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ENROLLED = "enrolled"
    CANCELLED = "cancelled"


class DocumentType(str, Enum):
    CPF = "cpf"
    RG = "rg"
    PROOF_OF_INCOME = "proof_of_income"
    PROOF_OF_ADDRESS = "proof_of_address"
    ACADEMIC_TRANSCRIPT = "academic_transcript"
    ENROLLMENT_CERTIFICATE = "enrollment_certificate"
    BANK_STATEMENT = "bank_statement"
    TAX_DECLARATION = "tax_declaration"
    PHOTO = "photo"
    EMPLOYMENT_CERTIFICATE = "employment_certificate"
    OTHER = "other"


class FundingProgramType(str, Enum):
    FIES = "fies"
    PROUNI = "prouni"
    INSTITUTIONAL = "institutional"
    STATE_PROGRAM = "state_program"
    FEDERAL_PROGRAM = "federal_program"


class InstitutionType(str, Enum):
    UNIVERSITY = "university"
    COLLEGE = "college"
    TECHNICAL_SCHOOL = "technical_school"
    DISTANCE_LEARNING = "distance_learning"
    POSTGRADUATE = "postgraduate"


class WorkflowStage(str, Enum):
    APPLICATION_RECEIVED = "application_received"
    DOCUMENT_VERIFICATION = "document_verification"
    ACADEMIC_REVIEW = "academic_review"
    FINANCIAL_REVIEW = "financial_review"
    FINAL_APPROVAL = "final_approval"
    ENROLLMENT = "enrollment"


# User Schema
class UserPermission(BaseMongoDbDocumentSchema):
    resource: str
    actions: List[str]
    institution_id: Optional[PyObjectId] = None


class User(BaseMongoDbDocumentSchema):
    email: str
    cpf: str
    password_hash: str
    full_name: str
    phone: str
    role: UserRole
    permissions: List[UserPermission] = Field(default_factory=list)
    institution_ids: List[PyObjectId] = Field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('cpf')
    def validate_cpf(cls, v):
        # Basic CPF validation (11 digits)
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        return cpf


class UserCollection(BaseCollectionSchema):
    collection_name: str = "users"
    document_schema: Type[BaseMongoDbDocumentSchema] = User
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("email", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("cpf", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("role", IndexDirection.ASCENDING), ("is_active", IndexDirection.ASCENDING)]
        )
    ]


# Student Schema
class StudentAddress(BaseMongoDbDocumentSchema):
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    zip_code: str
    
    @field_validator('zip_code')
    def validate_zip(cls, v):
        # Brazilian ZIP code format
        zip_clean = ''.join(filter(str.isdigit, v))
        if len(zip_clean) != 8:
            raise ValueError('ZIP code must have 8 digits')
        return zip_clean


class StudentEnrollment(BaseMongoDbDocumentSchema):
    institution_id: PyObjectId
    course_name: str
    semester: str
    enrollment_date: datetime
    status: Literal["active", "completed", "dropped", "transferred"]
    completion_date: Optional[datetime] = None


class Student(BaseMongoDbDocumentSchema):
    user_id: PyObjectId
    cpf: str
    full_name: str
    birth_date: datetime
    gender: Literal["M", "F", "Other"]
    address: StudentAddress
    enrollments: List[StudentEnrollment] = Field(default_factory=list)
    total_funding_received: Decimal = Decimal("0.00")
    engagement_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StudentCollection(BaseCollectionSchema):
    collection_name: str = "students"
    document_schema: Type[BaseMongoDbDocumentSchema] = Student
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("cpf", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("user_id", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("full_name", IndexDirection.TEXT)]
        ),
        IndexDefinition(
            keys=[("enrollments.institution_id", IndexDirection.ASCENDING),
                  ("enrollments.status", IndexDirection.ASCENDING)]
        )
    ]


# Application Schema
class ApplicationApplicantInfo(BaseMongoDbDocumentSchema):
    full_name: str
    cpf: str
    email: str
    phone: str
    birth_date: datetime


class ApplicationStageHistory(BaseMongoDbDocumentSchema):
    stage: WorkflowStage
    status: Literal["pending", "completed", "failed"]
    assigned_to: Optional[PyObjectId] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    comments: Optional[str] = None


class Application(BaseMongoDbDocumentSchema):
    applicant_id: PyObjectId
    applicant_info: ApplicationApplicantInfo  # Embedded for performance
    protocol_number: str
    funding_program_id: PyObjectId
    institution_id: PyObjectId
    course_name: str
    semester: str
    requested_amount: Decimal
    approved_amount: Optional[Decimal] = None
    status: ApplicationStatus
    stage_history: List[ApplicationStageHistory] = Field(default_factory=list)
    current_stage: Optional[WorkflowStage] = None
    document_ids: List[PyObjectId] = Field(default_factory=list)
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    decision_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApplicationCollection(BaseCollectionSchema):
    collection_name: str = "applications"
    document_schema: Type[BaseMongoDbDocumentSchema] = Application
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("protocol_number", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("applicant_id", IndexDirection.ASCENDING),
                  ("semester", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("status", IndexDirection.ASCENDING),
                  ("submission_date", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("institution_id", IndexDirection.ASCENDING),
                  ("funding_program_id", IndexDirection.ASCENDING),
                  ("status", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("applicant_info.cpf", IndexDirection.ASCENDING)]
        )
    ]


# Document Schema
class DocumentMetadata(BaseMongoDbDocumentSchema):
    file_name: str
    file_size: int
    mime_type: str
    upload_date: datetime
    storage_path: str
    checksum: str


class DocumentVerification(BaseMongoDbDocumentSchema):
    reviewer_id: PyObjectId
    status: Literal["pending", "approved", "rejected"]
    verified_at: datetime
    comments: Optional[str] = None
    rejection_reason: Optional[str] = None


class Document(BaseMongoDbDocumentSchema):
    application_id: PyObjectId
    applicant_id: PyObjectId
    document_type: DocumentType
    metadata: DocumentMetadata
    verification_history: List[DocumentVerification] = Field(default_factory=list)
    current_status: Literal["pending", "verified", "rejected", "expired"]
    is_archived: bool = False
    archive_date: Optional[datetime] = None
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentCollection(BaseCollectionSchema):
    collection_name: str = "documents"
    document_schema: Type[BaseMongoDbDocumentSchema] = Document
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("application_id", IndexDirection.ASCENDING),
                  ("document_type", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("applicant_id", IndexDirection.ASCENDING),
                  ("created_at", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("current_status", IndexDirection.ASCENDING),
                  ("is_archived", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("archive_date", IndexDirection.ASCENDING)],
            ttl_seconds=31536000  # 1 year TTL for archived documents
        )
    ]


# Protocol Schema
class Protocol(BaseMongoDbDocumentSchema):
    protocol_number: str
    application_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    qr_code: Optional[str] = None
    access_code: Optional[str] = None


class ProtocolCollection(BaseCollectionSchema):
    collection_name: str = "protocols"
    document_schema: Type[BaseMongoDbDocumentSchema] = Protocol
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("protocol_number", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("application_id", IndexDirection.ASCENDING)],
            unique=True
        )
    ]


# Funding Program Schema
class FundingProgramRequirement(BaseMongoDbDocumentSchema):
    name: str
    description: str
    document_types: List[DocumentType]
    is_mandatory: bool = True


class FundingProgramCriteria(BaseMongoDbDocumentSchema):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_income: Optional[Decimal] = None
    min_score: Optional[float] = None
    allowed_courses: List[str] = Field(default_factory=list)
    restricted_states: List[str] = Field(default_factory=list)


class FundingProgram(BaseMongoDbDocumentSchema):
    name: str
    program_type: FundingProgramType
    description: str
    requirements: List[FundingProgramRequirement]
    criteria: FundingProgramCriteria
    max_funding_amount: Decimal
    coverage_percentage: float
    is_active: bool = True
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FundingProgramCollection(BaseCollectionSchema):
    collection_name: str = "funding_programs"
    document_schema: Type[BaseMongoDbDocumentSchema] = FundingProgram
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("program_type", IndexDirection.ASCENDING),
                  ("is_active", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("name", IndexDirection.ASCENDING)],
            unique=True
        )
    ]


# Institution Schema
class InstitutionAddress(BaseMongoDbDocumentSchema):
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    zip_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class InstitutionCourse(BaseMongoDbDocumentSchema):
    name: str
    degree_type: Literal["bachelor", "technologist", "postgraduate", "master", "doctorate"]
    duration_semesters: int
    monthly_fee: Decimal
    is_active: bool = True


class Institution(BaseMongoDbDocumentSchema):
    name: str
    institution_type: InstitutionType
    cnpj: str
    mec_code: str  # Ministry of Education code
    address: InstitutionAddress
    courses: List[InstitutionCourse] = Field(default_factory=list)
    total_students: int = 0
    rating: Optional[float] = None
    accepts_fies: bool = True
    accepts_prouni: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InstitutionCollection(BaseCollectionSchema):
    collection_name: str = "institutions"
    document_schema: Type[BaseMongoDbDocumentSchema] = Institution
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("cnpj", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("mec_code", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("name", IndexDirection.TEXT)]
        ),
        IndexDefinition(
            keys=[("address.state", IndexDirection.ASCENDING),
                  ("address.city", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("address.latitude", IndexDirection.GEO2D),
                  ("address.longitude", IndexDirection.GEO2D)]
        )
    ]


# Workflow Schema
class WorkflowStep(BaseMongoDbDocumentSchema):
    stage: WorkflowStage
    assigned_role: UserRole
    sla_hours: int
    auto_approve: bool = False
    approval_criteria: Dict[str, Any] = Field(default_factory=dict)


class WorkflowInstance(BaseMongoDbDocumentSchema):
    workflow_id: PyObjectId
    application_id: PyObjectId
    current_step: int
    status: Literal["active", "completed", "cancelled"]
    started_at: datetime
    completed_at: Optional[datetime] = None
    step_results: List[Dict[str, Any]] = Field(default_factory=list)


class Workflow(BaseMongoDbDocumentSchema):
    name: str
    funding_program_id: PyObjectId
    steps: List[WorkflowStep]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowCollection(BaseCollectionSchema):
    collection_name: str = "workflows"
    document_schema: Type[BaseMongoDbDocumentSchema] = Workflow
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("funding_program_id", IndexDirection.ASCENDING),
                  ("is_active", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("name", IndexDirection.ASCENDING)],
            unique=True
        )
    ]


# Notification Schema
class Notification(BaseMongoDbDocumentSchema):
    recipient_id: PyObjectId
    recipient_email: str
    notification_type: Literal["email", "sms", "push", "in_app"]
    subject: str
    content: str
    related_entity_type: Literal["application", "document", "workflow"]
    related_entity_id: PyObjectId
    status: Literal["pending", "sent", "delivered", "failed"]
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationCollection(BaseCollectionSchema):
    collection_name: str = "notifications"
    document_schema: Type[BaseMongoDbDocumentSchema] = Notification
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("recipient_id", IndexDirection.ASCENDING),
                  ("created_at", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("status", IndexDirection.ASCENDING),
                  ("notification_type", IndexDirection.ASCENDING)]
        ),
        IndexDefinition(
            keys=[("related_entity_type", IndexDirection.ASCENDING),
                  ("related_entity_id", IndexDirection.ASCENDING)]
        )
    ]


# Audit Log Schema
class AuditLog(BaseMongoDbDocumentSchema):
    user_id: PyObjectId
    action: str
    entity_type: str
    entity_id: PyObjectId
    changes: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class AuditLogCollection(BaseCollectionSchema):
    collection_name: str = "audit_logs"
    document_schema: Type[BaseMongoDbDocumentSchema] = AuditLog
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("entity_type", IndexDirection.ASCENDING),
                  ("entity_id", IndexDirection.ASCENDING),
                  ("timestamp", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("user_id", IndexDirection.ASCENDING),
                  ("timestamp", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("timestamp", IndexDirection.ASCENDING)],
            ttl_seconds=157680000  # 5 years retention
        )
    ]


# Application Statistics Schema
class ApplicationStats(BaseMongoDbDocumentSchema):
    institution_id: PyObjectId
    funding_program_id: PyObjectId
    semester: str
    total_applications: int
    approved_count: int
    rejected_count: int
    pending_count: int
    approval_rate: float
    average_processing_days: float
    total_funding_approved: Decimal
    top_rejection_reasons: List[Dict[str, Any]] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class ApplicationStatsCollection(BaseCollectionSchema):
    collection_name: str = "application_stats"
    document_schema: Type[BaseMongoDbDocumentSchema] = ApplicationStats
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("institution_id", IndexDirection.ASCENDING),
                  ("semester", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("funding_program_id", IndexDirection.ASCENDING),
                  ("semester", IndexDirection.DESCENDING)]
        )
    ]


# Archived Documents Schema
class ArchivedDocument(BaseMongoDbDocumentSchema):
    original_id: PyObjectId
    application_id: PyObjectId
    applicant_id: PyObjectId
    document_type: DocumentType
    metadata: DocumentMetadata
    archive_reason: str
    archived_at: datetime = Field(default_factory=datetime.utcnow)
    retention_until: datetime


class ArchivedDocumentCollection(BaseCollectionSchema):
    collection_name: str = "archived_documents"
    document_schema: Type[BaseMongoDbDocumentSchema] = ArchivedDocument
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            keys=[("original_id", IndexDirection.ASCENDING)],
            unique=True
        ),
        IndexDefinition(
            keys=[("applicant_id", IndexDirection.ASCENDING),
                  ("archived_at", IndexDirection.DESCENDING)]
        ),
        IndexDefinition(
            keys=[("retention_until", IndexDirection.ASCENDING)]
        )
    ]


# Main Schema Definition
class BrazilianEdtechSchema(BaseMongoDbSchema):
    database_name: str = "brazilian_edtech"
    collections: Dict[str, BaseCollectionSchema] = {
        "users": UserCollection(),
        "students": StudentCollection(),
        "applications": ApplicationCollection(),
        "documents": DocumentCollection(),
        "protocols": ProtocolCollection(),
        "funding_programs": FundingProgramCollection(),
        "institutions": InstitutionCollection(),
        "workflows": WorkflowCollection(),
        "notifications": NotificationCollection(),
        "audit_logs": AuditLogCollection(),
        "application_stats": ApplicationStatsCollection(),
        "archived_documents": ArchivedDocumentCollection()
    }