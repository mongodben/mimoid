"""Database schema for DataTech Platform - MarTech Customer Data Platform"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, EmailStr, validator
from enum import Enum

# Import base types from mimiod package
from mimiod import (
    IndexDirection,
    IndexDefinition,
    BaseCollectionSchema,
    BaseMongoDbSchema,
    PyObjectId,
    BaseMongoDbDocumentSchema,
)


# Enums for constrained fields
class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    PURCHASE = "purchase"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    FORM_SUBMIT = "form_submit"
    CAMPAIGN_CLICK = "campaign_click"
    SOCIAL_SHARE = "social_share"
    LOGIN = "login"
    REGISTRATION = "registration"


class CampaignType(str, Enum):
    EMAIL = "email"
    SOCIAL = "social"
    DISPLAY = "display"
    SEARCH = "search"
    PUSH = "push"
    SMS = "sms"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class DataSourceType(str, Enum):
    WEB = "web"
    MOBILE_APP = "mobile_app"
    EMAIL = "email"
    SOCIAL = "social"
    CRM = "crm"
    THIRD_PARTY = "third_party"


# Document schemas
class Customer(BaseMongoDbDocumentSchema):
    # Core identity fields
    email: Optional[EmailStr] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Primary phone number")
    external_id: Optional[str] = Field(None, description="External system customer ID")

    # Profile information
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=150)

    # Demographics
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, max_length=20)
    location: Optional[Dict[str, Any]] = Field(
        default={}, description="Address and location data"
    )

    # Custom fields - flexible schema
    custom_fields: Dict[str, Any] = Field(
        default={}, description="Dynamic custom attributes"
    )
    tags: List[str] = Field(
        default=[], max_items=50, description="Customer tags for segmentation"
    )

    # Computed values
    lifetime_value: float = Field(
        default=0.0, description="Calculated customer lifetime value"
    )
    engagement_score: float = Field(
        default=0.0, ge=0, le=100, description="Engagement score 0-100"
    )
    last_activity_date: Optional[datetime] = Field(
        None, description="Most recent customer activity"
    )

    # Preferences and consent
    preferences: Dict[str, Any] = Field(
        default={}, description="Communication and product preferences"
    )
    consent: Dict[str, bool] = Field(
        default={}, description="Privacy and marketing consent flags"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    data_sources: List[str] = Field(
        default=[], description="Sources that contributed data"
    )


class Event(BaseMongoDbDocumentSchema):
    customer_id: PyObjectId = Field(..., description="Reference to customer")

    # Event details
    event_type: EventType = Field(..., description="Type of event")
    event_name: str = Field(..., max_length=100, description="Specific event name")

    # Event data - flexible schema for different event types
    properties: Dict[str, Any] = Field(
        default={}, description="Event-specific properties"
    )

    # Context
    session_id: Optional[str] = Field(None, description="User session identifier")
    campaign_id: Optional[PyObjectId] = Field(None, description="Associated campaign")

    # Technical details
    user_agent: Optional[str] = Field(None, description="Browser/app user agent")
    ip_address: Optional[str] = Field(None, description="IP address")
    device_type: Optional[str] = Field(
        None, description="Device type (mobile, desktop, tablet)"
    )

    # Location and source
    page_url: Optional[str] = Field(None, description="URL where event occurred")
    referrer: Optional[str] = Field(None, description="Referrer URL")
    source: DataSourceType = Field(..., description="Data source")

    # Timestamp
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When event occurred"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(BaseMongoDbDocumentSchema):
    # Basic campaign info
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    campaign_type: CampaignType = Field(...)
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)

    # Campaign content and configuration
    content: Dict[str, Any] = Field(
        default={}, description="Campaign content and settings"
    )
    targeting: Dict[str, Any] = Field(default={}, description="Targeting criteria")

    # Schedule
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)

    # Performance metrics
    metrics: Dict[str, float] = Field(
        default={}, description="Campaign performance metrics"
    )

    # Metadata
    created_by: Optional[str] = Field(None, description="User who created campaign")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Segment(BaseMongoDbDocumentSchema):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=500)

    # Segment definition
    criteria: Dict[str, Any] = Field(..., description="Segment criteria and filters")
    customer_count: int = Field(
        default=0, ge=0, description="Number of customers in segment"
    )

    # Performance tracking
    last_calculated: Optional[datetime] = Field(
        None, description="When segment was last calculated"
    )
    is_dynamic: bool = Field(default=True, description="Whether segment auto-updates")

    # Metadata
    created_by: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class SocialMember(BaseMongoDbDocumentSchema):
    customer_id: PyObjectId = Field(..., description="Reference to customer")

    # Social platform details
    platform: str = Field(..., max_length=50, description="Social platform name")
    platform_user_id: str = Field(..., description="User ID on the social platform")
    username: Optional[str] = Field(None, description="Username/handle")

    # Profile data
    profile_data: Dict[str, Any] = Field(
        default={}, description="Platform-specific profile data"
    )
    follower_count: Optional[int] = Field(None, ge=0)
    following_count: Optional[int] = Field(None, ge=0)

    # Activity metrics
    engagement_metrics: Dict[str, float] = Field(
        default={}, description="Platform engagement metrics"
    )
    last_activity: Optional[datetime] = Field(None)

    # Metadata
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class DataSource(BaseMongoDbDocumentSchema):
    name: str = Field(..., min_length=1, max_length=100)
    source_type: DataSourceType = Field(...)
    description: Optional[str] = Field(None, max_length=500)

    # Configuration
    connection_config: Dict[str, Any] = Field(
        default={}, description="Connection configuration"
    )
    data_mapping: Dict[str, str] = Field(
        default={}, description="Field mapping configuration"
    )

    # Status and monitoring
    is_active: bool = Field(default=True)
    last_sync: Optional[datetime] = Field(None)
    sync_status: Optional[str] = Field(None)
    error_count: int = Field(default=0, ge=0)

    # Quality metrics
    data_quality_score: float = Field(default=0.0, ge=0, le=100)
    record_count: int = Field(default=0, ge=0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


# Collection schema definitions
class CustomerCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Customer.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="email_unique",
            keys={"email": IndexDirection.ASCENDING},
            unique=True,
            sparse=True,
        ),
        IndexDefinition(
            name="phone_index", keys={"phone": IndexDirection.ASCENDING}, sparse=True
        ),
        IndexDefinition(
            name="external_id_index",
            keys={"external_id": IndexDirection.ASCENDING},
            sparse=True,
        ),
        IndexDefinition(name="tags_index", keys={"tags": IndexDirection.ASCENDING}),
        IndexDefinition(
            name="name_text_search",
            keys={
                "first_name": IndexDirection.TEXT,
                "last_name": IndexDirection.TEXT,
                "company": IndexDirection.TEXT,
            },
        ),
        IndexDefinition(
            name="activity_score_index",
            keys={
                "last_activity_date": IndexDirection.DESCENDING,
                "engagement_score": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Customer profiles with flexible custom fields"


class EventCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Event.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="customer_timestamp_index",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "timestamp": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="event_type_timestamp_index",
            keys={
                "event_type": IndexDirection.ASCENDING,
                "timestamp": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="campaign_events_index",
            keys={
                "campaign_id": IndexDirection.ASCENDING,
                "timestamp": IndexDirection.DESCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="session_events_index",
            keys={"session_id": IndexDirection.ASCENDING},
            sparse=True,
        ),
    ]
    description: str = "Customer event tracking and behavior data"


class CampaignCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Campaign.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="name_index", keys={"name": IndexDirection.ASCENDING}),
        IndexDefinition(
            name="type_status_index",
            keys={
                "campaign_type": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="date_range_index",
            keys={
                "start_date": IndexDirection.ASCENDING,
                "end_date": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
    ]
    description: str = "Marketing campaigns and automation"


class SegmentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Segment.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="name_unique", keys={"name": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="dynamic_segments_index", keys={"is_dynamic": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="last_calculated_index",
            keys={"last_calculated": IndexDirection.DESCENDING},
            sparse=True,
        ),
    ]
    description: str = "Customer segments for targeting"


class SocialMemberCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = SocialMember.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="customer_platform_index",
            keys={
                "customer_id": IndexDirection.ASCENDING,
                "platform": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="platform_user_unique",
            keys={
                "platform": IndexDirection.ASCENDING,
                "platform_user_id": IndexDirection.ASCENDING,
            },
            unique=True,
        ),
        IndexDefinition(
            name="active_members_index",
            keys={
                "is_active": IndexDirection.ASCENDING,
                "last_activity": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Social platform member profiles"


class DataSourceCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = DataSource.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="name_unique", keys={"name": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="type_active_index",
            keys={
                "source_type": IndexDirection.ASCENDING,
                "is_active": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="sync_status_index", keys={"last_sync": IndexDirection.DESCENDING}
        ),
    ]
    description: str = "Data source connections and monitoring"


# Complete database schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "customers": CustomerCollectionSchema(),
        "events": EventCollectionSchema(),
        "campaigns": CampaignCollectionSchema(),
        "segments": SegmentCollectionSchema(),
        "social_members": SocialMemberCollectionSchema(),
        "data_sources": DataSourceCollectionSchema(),
    }
    database_name: str = "datatech_platform"
    description: str = (
        "MarTech Customer Data Platform with flexible schema and multi-channel support"
    )


# Export the database schema
database_schema = MongoDbDataSchema()
