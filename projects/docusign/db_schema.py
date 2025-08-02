"""
DocuSign MongoDB Schema Definitions

This module defines the MongoDB collections and document schemas for modeling
DocuSign's electronic signature platform, including accounts, envelopes,
documents, recipients, templates, and audit trails.
"""

from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum

from mimoid import (
    BaseMongoDbSchema,
    BaseCollectionSchema,
    BaseMongoDbDocumentSchema,
    IndexDefinition,
    IndexDirection,
    PyObjectId,
    DatabaseSeeder,
)


class EnvelopeStatus(str, Enum):
    """Envelope lifecycle status values"""
    CREATED = "created"
    SENT = "sent"
    DELIVERED = "delivered"
    SIGNED = "signed"
    COMPLETED = "completed"
    DECLINED = "declined"
    VOIDED = "voided"


class RecipientType(str, Enum):
    """Types of envelope recipients"""
    SIGNER = "signer"
    CARBON_COPY = "carbon_copy"
    CERTIFIED_DELIVERY = "certified_delivery"
    IN_PERSON_SIGNER = "in_person_signer"
    EDITOR = "editor"
    AGENT = "agent"
    INTERMEDIARY = "intermediary"
    WITNESS = "witness"
    NOTARY = "notary"


class RecipientStatus(str, Enum):
    """Recipient interaction status"""
    CREATED = "created"
    SENT = "sent"
    DELIVERED = "delivered"
    SIGNED = "signed"
    COMPLETED = "completed"
    DECLINED = "declined"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTO_RESPONDED = "auto_responded"


class TabType(str, Enum):
    """Types of form fields/tabs in documents"""
    SIGN_HERE = "sign_here"
    INITIAL_HERE = "initial_here"
    FULL_NAME = "full_name"
    DATE_SIGNED = "date_signed"
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO_GROUP = "radio_group"
    DROPDOWN = "dropdown"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    COMPANY = "company"
    TITLE = "title"
    NOTE = "note"
    APPROVE = "approve"
    DECLINE = "decline"


class AuthenticationMethod(str, Enum):
    """Recipient authentication methods"""
    EMAIL = "email"
    ACCESS_CODE = "access_code"
    SMS = "sms"
    PHONE = "phone"
    KNOWLEDGE_BASED = "knowledge_based"
    ID_VERIFICATION = "id_verification"
    SIGNATURE_PROVIDER = "signature_provider"


class AccountPlan(str, Enum):
    """DocuSign account plan types"""
    PERSONAL = "personal"
    STANDARD = "standard"
    BUSINESS_PRO = "business_pro"
    ENTERPRISE = "enterprise"
    ADVANCED = "advanced"


class EventType(str, Enum):
    """Audit event types"""
    ENVELOPE_CREATED = "envelope_created"
    ENVELOPE_SENT = "envelope_sent"
    ENVELOPE_VIEWED = "envelope_viewed"
    ENVELOPE_SIGNED = "envelope_signed"
    ENVELOPE_COMPLETED = "envelope_completed"
    ENVELOPE_DECLINED = "envelope_declined"
    ENVELOPE_VOIDED = "envelope_voided"
    RECIPIENT_SENT = "recipient_sent"
    RECIPIENT_DELIVERED = "recipient_delivered"
    RECIPIENT_VIEWED = "recipient_viewed"
    RECIPIENT_SIGNED = "recipient_signed"
    RECIPIENT_COMPLETED = "recipient_completed"
    RECIPIENT_DECLINED = "recipient_declined"
    AUTHENTICATION_PASSED = "authentication_passed"
    AUTHENTICATION_FAILED = "authentication_failed"


# Account Schema
class AccountSettings(BaseMongoDbDocumentSchema):
    """Account configuration settings"""
    enable_sequential_signing: bool = True
    enable_recipient_authentication: bool = True
    enable_advanced_recipient_routing: bool = False
    enable_conditional_fields: bool = False
    enable_payment_processing: bool = False
    envelope_expiration_days: int = 30
    reminder_frequency_days: int = 3
    max_reminders: int = 3
    session_timeout_minutes: int = 20
    require_21_cfr_part_11: bool = False
    enable_power_forms: bool = False
    enable_sms_delivery: bool = True
    custom_settings: Dict[str, Any] = {}


class BillingInfo(BaseMongoDbDocumentSchema):
    """Account billing information"""
    plan_id: AccountPlan
    billing_period_start: datetime
    billing_period_end: datetime
    envelope_allowance: int
    envelopes_used: int
    additional_seats: int = 0
    payment_method: Optional[str] = None
    next_billing_date: datetime
    amount_due: float = 0.0


class Account(BaseMongoDbDocumentSchema):
    """MongoDB document schema for accounts"""
    account_id: str
    account_name: str
    account_external_id: Optional[str] = None
    created_date: datetime
    status: Literal["active", "suspended", "closed"] = "active"
    billing_info: BillingInfo
    settings: AccountSettings
    
    # Contact information
    admin_email: str
    admin_name: str
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    
    # Features and limits
    user_count: int = 1
    api_access_enabled: bool = True
    connect_enabled: bool = False
    brand_ids: List[PyObjectId] = []
    
    # Usage metrics
    total_envelopes_sent: int = 0
    total_envelopes_completed: int = 0
    last_activity_date: Optional[datetime] = None
    
    # Custom fields for integration
    metadata: Dict[str, Any] = {}


# User Schema
class UserPermissions(BaseMongoDbDocumentSchema):
    """User permission settings"""
    can_send_envelopes: bool = True
    can_manage_account: bool = False
    can_manage_templates: bool = True
    can_view_reports: bool = True
    can_manage_users: bool = False
    can_use_api: bool = False
    template_ids: List[PyObjectId] = []  # Specific templates user can access


class User(BaseMongoDbDocumentSchema):
    """MongoDB document schema for users"""
    user_id: str
    account_id: PyObjectId
    email: str
    user_name: str
    first_name: str
    last_name: str
    title: Optional[str] = None
    created_date: datetime
    last_login_date: Optional[datetime] = None
    status: Literal["active", "inactive", "closed"] = "active"
    user_type: Literal["regular", "admin", "sender", "viewer"] = "regular"
    
    permissions: UserPermissions
    
    # Authentication
    login_count: int = 0
    failed_login_attempts: int = 0
    password_last_changed: Optional[datetime] = None
    
    # Preferences
    locale: str = "en_US"
    time_zone: str = "America/Los_Angeles"
    date_format: str = "MM/dd/yyyy"
    signature_id: Optional[str] = None
    initials_id: Optional[str] = None
    
    # Usage stats
    envelopes_sent_count: int = 0
    last_sent_date: Optional[datetime] = None
    
    # Integration data
    external_user_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


# Template Schema
class TemplateRecipient(BaseMongoDbDocumentSchema):
    """Template recipient definition"""
    recipient_id: str
    recipient_type: RecipientType
    role_name: str
    routing_order: int
    
    # Default values
    default_name: Optional[str] = None
    default_email: Optional[str] = None
    
    # Requirements
    is_required: bool = True
    can_edit_name: bool = True
    can_edit_email: bool = True
    
    # Authentication
    authentication_methods: List[AuthenticationMethod] = []
    access_code: Optional[str] = None
    
    # Tab assignments
    tab_ids: List[str] = []


class Template(BaseMongoDbDocumentSchema):
    """MongoDB document schema for templates"""
    template_id: str
    account_id: PyObjectId
    name: str
    description: Optional[str] = None
    created_date: datetime
    created_by: PyObjectId  # User ID
    last_modified_date: datetime
    last_used_date: Optional[datetime] = None
    
    # Sharing
    shared: bool = False
    shared_with_accounts: List[PyObjectId] = []
    folder_id: Optional[str] = None
    
    # Template content
    email_subject: str
    email_message: Optional[str] = None
    
    # Recipients
    recipients: List[TemplateRecipient] = []
    
    # Documents (simplified - actual content stored separately)
    document_ids: List[str] = []
    document_count: int = 0
    
    # Settings
    enable_sequential_signing: bool = True
    enable_wet_sign: bool = False
    brand_id: Optional[PyObjectId] = None
    
    # Usage tracking
    usage_count: int = 0
    last_30_days_usage: int = 0
    
    # Metadata
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}


# Document Schema
class DocumentTab(BaseMongoDbDocumentSchema):
    """Form field/tab on a document"""
    tab_id: str
    tab_type: TabType
    tab_label: str
    
    # Position
    page_number: int
    x_position: float
    y_position: float
    width: Optional[float] = None
    height: Optional[float] = None
    
    # Assignment
    recipient_id: Optional[str] = None
    
    # Properties
    is_required: bool = True
    is_locked: bool = False
    
    # Values
    default_value: Optional[str] = None
    value: Optional[str] = None
    
    # Validation
    validation_pattern: Optional[str] = None
    validation_message: Optional[str] = None
    max_length: Optional[int] = None
    
    # Tab-specific properties
    options: Optional[List[str]] = None  # For dropdowns/radio
    group_name: Optional[str] = None  # For radio groups
    formula: Optional[str] = None  # For calculated fields


class Document(BaseMongoDbDocumentSchema):
    """MongoDB document schema for documents"""
    document_id: str
    envelope_id: PyObjectId
    name: str
    file_extension: str
    document_order: int
    
    # Content reference
    content_type: str = "application/pdf"
    content_bytes: Optional[int] = None
    content_location: str  # S3 key or file path
    page_count: int = 1
    
    # Document properties
    is_authoritative_copy: bool = False
    include_in_download: bool = True
    signer_must_acknowledge: bool = False
    
    # Form fields
    tabs: List[DocumentTab] = []
    
    # Status
    created_date: datetime
    signed_date: Optional[datetime] = None
    
    # Metadata
    custom_fields: Dict[str, Any] = {}


# Recipient Schema
class Recipient(BaseMongoDbDocumentSchema):
    """MongoDB document schema for recipients"""
    recipient_id: str
    envelope_id: PyObjectId
    
    # Identity
    email: str
    name: str
    recipient_type: RecipientType
    
    # Routing
    routing_order: int
    status: RecipientStatus = RecipientStatus.CREATED
    
    # External references
    client_user_id: Optional[str] = None  # For embedded signing
    user_id: Optional[PyObjectId] = None  # Link to system user
    
    # Authentication
    authentication_methods: List[AuthenticationMethod] = []
    access_code: Optional[str] = None
    phone_number: Optional[str] = None
    id_check_configuration: Optional[Dict[str, Any]] = None
    
    # Delivery
    email_notification: bool = True
    sms_notification: bool = False
    embedded_recipient_start_url: Optional[str] = None
    
    # Timing
    sent_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    signed_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None
    declined_reason: Optional[str] = None
    
    # Tab data
    assigned_tabs: List[str] = []  # Tab IDs
    completed_tabs: List[str] = []
    
    # Delegation
    can_sign_offline: bool = False
    agent_can_edit_email: bool = False
    agent_can_edit_name: bool = False
    
    # Tracking
    ip_address: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    geo_location: Optional[Dict[str, float]] = None
    
    # Custom fields
    custom_fields: Dict[str, Any] = {}


# Envelope Schema
class EnvelopeNotification(BaseMongoDbDocumentSchema):
    """Envelope notification settings"""
    use_account_defaults: bool = True
    reminder_enabled: bool = True
    reminder_delay_days: int = 3
    reminder_frequency_days: int = 3
    expiration_enabled: bool = True
    expiration_days: int = 30
    expiration_warning_days: int = 7


class EnvelopeCustomField(BaseMongoDbDocumentSchema):
    """Envelope custom field"""
    field_id: str
    name: str
    value: str
    required: bool = False
    show_to_recipients: bool = False


class Envelope(BaseMongoDbDocumentSchema):
    """MongoDB document schema for envelopes"""
    envelope_id: str
    account_id: PyObjectId
    
    # Status and lifecycle
    status: EnvelopeStatus = EnvelopeStatus.CREATED
    created_date: datetime
    sent_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None
    voided_date: Optional[datetime] = None
    voided_reason: Optional[str] = None
    
    # Email content
    email_subject: str
    email_message: Optional[str] = None
    
    # Sender info
    sender_user_id: PyObjectId
    sender_name: str
    sender_email: str
    
    # Template reference
    template_id: Optional[PyObjectId] = None
    template_roles: Optional[List[Dict[str, str]]] = None
    
    # Documents
    document_ids: List[str] = []
    document_count: int = 0
    
    # Recipients summary (denormalized for performance)
    recipient_count: int = 0
    signers_count: int = 0
    completed_signers: int = 0
    current_routing_order: int = 1
    
    # Settings
    enable_sequential_signing: bool = True
    enable_wet_sign: bool = False
    allow_markup: bool = True
    allow_comments: bool = True
    allow_view_history: bool = True
    
    # Notification settings
    notification: EnvelopeNotification
    
    # Branding
    brand_id: Optional[PyObjectId] = None
    
    # Security
    message_lock: bool = False
    recipients_lock: bool = False
    use_disclosure: bool = True
    
    # Signing location
    signing_location: Literal["online", "offline", "both"] = "online"
    
    # Custom fields and metadata
    custom_fields: List[EnvelopeCustomField] = []
    envelope_metadata: Dict[str, Any] = {}
    
    # Integration tracking
    transaction_id: Optional[str] = None
    external_envelope_id: Optional[str] = None
    
    # Computed fields
    days_to_complete: Optional[int] = None
    is_expired: bool = False


# Audit Event Schema
class AuditEvent(BaseMongoDbDocumentSchema):
    """MongoDB document schema for audit events"""
    event_id: str
    envelope_id: PyObjectId
    event_type: EventType
    timestamp: datetime
    
    # Actor information
    user_id: Optional[PyObjectId] = None
    recipient_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    
    # Event details
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    geo_location: Optional[Dict[str, Any]] = None
    
    # Event-specific data
    details: Dict[str, Any] = {}
    
    # Security info
    security_level: Literal["low", "medium", "high"] = "medium"
    authentication_method: Optional[AuthenticationMethod] = None
    
    # Platform info
    client_type: Optional[str] = None  # web, mobile, api
    client_version: Optional[str] = None


# Brand Schema
class Brand(BaseMongoDbDocumentSchema):
    """MongoDB document schema for brands"""
    brand_id: str
    account_id: PyObjectId
    brand_name: str
    is_default: bool = False
    
    # Logo
    logo_url: Optional[str] = None
    logo_type: Optional[str] = None
    
    # Colors
    primary_color: str = "#003d79"
    secondary_color: str = "#0070c0"
    text_color: str = "#000000"
    button_color: str = "#0070c0"
    button_text_color: str = "#ffffff"
    
    # Email branding
    email_header_logo: Optional[str] = None
    email_footer_text: Optional[str] = None
    
    # Signing page branding
    signing_page_logo: Optional[str] = None
    signing_page_header_text: Optional[str] = None
    
    # Created/modified tracking
    created_date: datetime
    created_by: PyObjectId
    last_modified_date: datetime
    
    # Usage
    envelope_count: int = 0


# Folder Schema
class Folder(BaseMongoDbDocumentSchema):
    """MongoDB document schema for folders"""
    folder_id: str
    account_id: PyObjectId
    name: str
    parent_folder_id: Optional[str] = None
    
    # Type
    folder_type: Literal["normal", "recyclebin", "sentitems", "draft", "inbox"] = "normal"
    
    # Ownership
    owner_user_id: PyObjectId
    
    # Sharing
    is_shared: bool = False
    shared_with_users: List[PyObjectId] = []
    
    # Counts
    envelope_count: int = 0
    folder_count: int = 0
    
    # Dates
    created_date: datetime
    last_modified_date: datetime


# Collection Schemas
class AccountCollectionSchema(BaseCollectionSchema):
    """Account collection configuration"""
    json_schema: Dict[str, Any] = Account.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="account_id_unique",
            keys={"account_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="admin_email_index",
            keys={"admin_email": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="status_index",
            keys={"status": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="company_name_index",
            keys={"company_name": IndexDirection.ASCENDING},
            sparse=True
        ),
    ]
    description: str = "DocuSign account information"


class UserCollectionSchema(BaseCollectionSchema):
    """User collection configuration"""
    json_schema: Dict[str, Any] = User.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="user_id_unique",
            keys={"user_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="email_unique",
            keys={"email": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="account_id_index",
            keys={"account_id": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="account_status_index",
            keys={
                "account_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            }
        ),
    ]
    description: str = "User accounts and permissions"


class TemplateCollectionSchema(BaseCollectionSchema):
    """Template collection configuration"""
    json_schema: Dict[str, Any] = Template.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="template_id_unique",
            keys={"template_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="account_id_index",
            keys={"account_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="account_shared_index",
            keys={
                "account_id": IndexDirection.ASCENDING,
                "shared": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="name_text_index",
            keys={"name": "text"},
        ),
        IndexDefinition(
            name="usage_count_index",
            keys={"usage_count": IndexDirection.DESCENDING},
        ),
    ]
    description: str = "Reusable document templates"


class DocumentCollectionSchema(BaseCollectionSchema):
    """Document collection configuration"""
    json_schema: Dict[str, Any] = Document.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="document_id_unique",
            keys={"document_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="envelope_id_index",
            keys={"envelope_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="envelope_order_index",
            keys={
                "envelope_id": IndexDirection.ASCENDING,
                "document_order": IndexDirection.ASCENDING
            }
        ),
    ]
    description: str = "Documents within envelopes"


class RecipientCollectionSchema(BaseCollectionSchema):
    """Recipient collection configuration"""
    json_schema: Dict[str, Any] = Recipient.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="recipient_id_unique",
            keys={"recipient_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="envelope_id_index",
            keys={"envelope_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="email_index",
            keys={"email": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="envelope_routing_index",
            keys={
                "envelope_id": IndexDirection.ASCENDING,
                "routing_order": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="envelope_status_index",
            keys={
                "envelope_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="email_status_date_index",
            keys={
                "email": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
                "sent_date": IndexDirection.DESCENDING
            }
        ),
    ]
    description: str = "Envelope recipients and their status"


class EnvelopeCollectionSchema(BaseCollectionSchema):
    """Envelope collection configuration"""
    json_schema: Dict[str, Any] = Envelope.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="envelope_id_unique",
            keys={"envelope_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="account_id_index",
            keys={"account_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="account_status_date_index",
            keys={
                "account_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
                "sent_date": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="sender_status_index",
            keys={
                "sender_user_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="email_subject_text_index",
            keys={"email_subject": "text"}
        ),
        IndexDefinition(
            name="sent_date_index",
            keys={"sent_date": IndexDirection.DESCENDING},
            sparse=True
        ),
        IndexDefinition(
            name="external_envelope_id_index",
            keys={"external_envelope_id": IndexDirection.ASCENDING},
            sparse=True
        ),
    ]
    description: str = "Envelope containers for documents"


class AuditEventCollectionSchema(BaseCollectionSchema):
    """Audit event collection configuration"""
    json_schema: Dict[str, Any] = AuditEvent.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="event_id_unique",
            keys={"event_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="envelope_timestamp_index",
            keys={
                "envelope_id": IndexDirection.ASCENDING,
                "timestamp": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="event_type_timestamp_index",
            keys={
                "event_type": IndexDirection.ASCENDING,
                "timestamp": IndexDirection.DESCENDING
            }
        ),
        IndexDefinition(
            name="timestamp_index",
            keys={"timestamp": IndexDirection.DESCENDING}
        ),
        IndexDefinition(
            name="user_id_index",
            keys={"user_id": IndexDirection.ASCENDING},
            sparse=True
        ),
    ]
    description: str = "Audit trail of all envelope events"


class BrandCollectionSchema(BaseCollectionSchema):
    """Brand collection configuration"""
    json_schema: Dict[str, Any] = Brand.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="brand_id_unique",
            keys={"brand_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="account_id_index",
            keys={"account_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="account_default_index",
            keys={
                "account_id": IndexDirection.ASCENDING,
                "is_default": IndexDirection.ASCENDING
            }
        ),
    ]
    description: str = "Branding configurations for accounts"


class FolderCollectionSchema(BaseCollectionSchema):
    """Folder collection configuration"""
    json_schema: Dict[str, Any] = Folder.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="folder_id_unique",
            keys={"folder_id": IndexDirection.ASCENDING},
            unique=True
        ),
        IndexDefinition(
            name="account_id_index",
            keys={"account_id": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="owner_type_index",
            keys={
                "owner_user_id": IndexDirection.ASCENDING,
                "folder_type": IndexDirection.ASCENDING
            }
        ),
        IndexDefinition(
            name="parent_folder_index",
            keys={"parent_folder_id": IndexDirection.ASCENDING},
            sparse=True
        ),
    ]
    description: str = "Organizational folders for envelopes"


# Main schema class
class DocuSignMongoDbSchema(BaseMongoDbSchema):
    """Complete MongoDB schema for DocuSign platform"""
    
    collections: Dict[str, BaseCollectionSchema] = {
        "accounts": AccountCollectionSchema(),
        "users": UserCollectionSchema(),
        "templates": TemplateCollectionSchema(),
        "documents": DocumentCollectionSchema(),
        "recipients": RecipientCollectionSchema(),
        "envelopes": EnvelopeCollectionSchema(),
        "audit_events": AuditEventCollectionSchema(),
        "brands": BrandCollectionSchema(),
        "folders": FolderCollectionSchema(),
    }
    
    database_name: str = "docusign"
    description: str = "MongoDB schema for DocuSign electronic signature platform"