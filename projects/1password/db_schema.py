"""
1Password Events API MongoDB Schema
Comprehensive database schema for security event monitoring and audit trails
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import Field, field_validator

from mimoid import (
    BaseMongoDbSchema, BaseCollectionSchema, BaseMongoDbDocumentSchema,
    IndexDefinition, IndexDirection, PyObjectId, DatabaseSeeder
)

# Enums and Type Definitions
AuditEventAction = Literal[
    "activate", "update", "delete", "convert", "enblduo", "updatduo", "disblduo",
    "rdmchild", "detchild", "dlgsess", "create", "deolddev", "dealldev", "reauth",
    "begin", "complete", "propose", "updatfw", "join", "leave", "role", "purge",
    "view", "export", "replace", "grant", "revoke", "share", "delshare", "uisas",
    "enblmfa", "updatmfa", "disblmfa", "musercom", "muserdec", "sendpkg", "resendts",
    "prsndall", "trename", "tverify", "trevoke", "ssotknv", "enblsso", "disblsso",
    "chngpsso", "chngasso", "chngdsso", "delgsso", "addgsso", "cancel", "hide",
    "unhide", "upguest", "verify", "reactive", "suspend", "beginr", "provsn",
    "sendts", "unknown", "completr", "cancelr", "trvlaway", "trvlback", "changeks",
    "changemp", "changesk", "changenm", "changela", "tdvcsso", "sdvcsso", "patch",
    "updatea", "vrfydmn", "uvrfydmn", "dvrfydmn"
]

AuditEventObjectType = Literal[
    "account", "user", "device", "group", "gm", "vault", "item", "items",
    "itemhist", "vaultkey", "template", "uva", "gva", "invite", "ec", "miguser",
    "sso", "sub", "card", "pm", "slackapp", "file", "famchild", "sa", "satoken",
    "dlgdsess", "ssotkn", "report"
]

ItemUsageAction = Literal[
    "fill", "select-sso-provider", "enter-item-edit-mode", "export",
    "share", "secure-copy", "reveal", "server-create", "server-update", "server-fetch"
]

SignInAttemptCategory = Literal[
    "success", "credentials_failed", "mfa_failed", "sso_failed",
    "modern_version_failed", "firewall_failed", "firewall_reported_success"
]

SignInAttemptType = Literal[
    "credentials_ok", "mfa_ok", "password_secret_bad", "mfa_missing",
    "totp_disabled", "totp_bad", "totp_timeout", "u2f_disabled", "u2f_bad",
    "u2f_timout", "duo_disabled", "duo_bad", "duo_timeout", "duo_native_bad",
    "service_account_sso_denied", "non_sso_user", "sso_user_mismatch",
    "platform_secret_disabled", "platform_secret_bad", "platform_secret_proxy",
    "code_disabled", "code_bad", "code_timeout", "ip_blocked", "continent_blocked",
    "country_blocked", "anonymous_blocked", "all_blocked", "modern_version_missing",
    "modern_version_old"
]

# Embedded Document Schemas
class LocationSchema(BaseMongoDbDocumentSchema):
    city: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ClientSchema(BaseMongoDbDocumentSchema):
    app_name: Optional[str] = None
    app_version: Optional[str] = None
    ip_address: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    platform_name: Optional[str] = None
    platform_version: Optional[str] = None

class SessionSchema(BaseMongoDbDocumentSchema):
    uuid: str
    device_uuid: str
    ip: Optional[str] = None
    login_time: datetime

class UserRefSchema(BaseMongoDbDocumentSchema):
    uuid: str
    email: Optional[str] = None
    name: Optional[str] = None

class DetailsSchema(BaseMongoDbDocumentSchema):
    value: Optional[str] = None

# Main Document Schemas
class UserSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="1Password user UUID")
    email: str
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None
    role: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class DeviceSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="1Password device UUID")
    user_uuid: str
    name: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    platform: Optional[str] = None
    is_trusted: bool = True
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class VaultSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="1Password vault UUID")
    name: str
    description: Optional[str] = None
    is_shared: bool = False
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    permissions: List[Dict[str, Any]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class ItemSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="1Password item UUID")
    vault_uuid: str
    title: str
    category: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    is_trashed: bool = False
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class AuditEventSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="Event UUID")
    timestamp: datetime
    action: AuditEventAction
    object_type: AuditEventObjectType
    object_uuid: Optional[str] = None
    actor_uuid: str
    aux_id: Optional[int] = None
    aux_info: Optional[str] = None
    aux_uuid: Optional[str] = None
    location: Optional[LocationSchema] = None
    session: Optional[SessionSchema] = None

class ItemUsageSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="Usage event UUID")
    timestamp: datetime
    action: ItemUsageAction
    item_uuid: str
    vault_uuid: str
    user: UserRefSchema
    client: Optional[ClientSchema] = None
    location: Optional[LocationSchema] = None
    used_version: Optional[int] = None

class SignInAttemptSchema(BaseMongoDbDocumentSchema):
    uuid: str = Field(..., description="Sign-in attempt UUID")
    timestamp: datetime
    category: SignInAttemptCategory
    type: SignInAttemptType
    target_user: UserRefSchema
    session_uuid: Optional[str] = None
    client: Optional[ClientSchema] = None
    location: Optional[LocationSchema] = None
    country: Optional[str] = None
    details: Optional[DetailsSchema] = None

# Collection Schemas
class UsersCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = UserSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="email_unique", keys={"email": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="created_at_desc", keys={"created_at": IndexDirection.DESCENDING}),
        IndexDefinition(name="last_seen_desc", keys={"last_seen": IndexDirection.DESCENDING}),
    ]
    description: str = "1Password user accounts and profiles"

class DevicesCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = DeviceSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="user_uuid_idx", keys={"user_uuid": IndexDirection.ASCENDING}),
        IndexDefinition(name="user_last_used_idx", keys={"user_uuid": IndexDirection.ASCENDING, "last_used": IndexDirection.DESCENDING}),
        IndexDefinition(name="registered_at_desc", keys={"registered_at": IndexDirection.DESCENDING}),
    ]
    description: str = "1Password devices and client information"

class VaultsCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = VaultSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="created_by_idx", keys={"created_by": IndexDirection.ASCENDING}),
        IndexDefinition(name="is_shared_idx", keys={"is_shared": IndexDirection.ASCENDING}),
        IndexDefinition(name="created_at_desc", keys={"created_at": IndexDirection.DESCENDING}),
    ]
    description: str = "1Password vaults and access control"

class ItemsCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = ItemSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="vault_uuid_idx", keys={"vault_uuid": IndexDirection.ASCENDING}),
        IndexDefinition(name="vault_updated_idx", keys={"vault_uuid": IndexDirection.ASCENDING, "updated_at": IndexDirection.DESCENDING}),
        IndexDefinition(name="created_by_idx", keys={"created_by": IndexDirection.ASCENDING}),
        IndexDefinition(name="category_idx", keys={"category": IndexDirection.ASCENDING}),
        IndexDefinition(name="is_trashed_idx", keys={"is_trashed": IndexDirection.ASCENDING}),
    ]
    description: str = "1Password vault items and credentials"

class AuditEventsCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = AuditEventSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="timestamp_desc", keys={"timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="actor_timestamp_idx", keys={"actor_uuid": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="action_timestamp_idx", keys={"action": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="object_type_timestamp_idx", keys={"object_type": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="object_uuid_timestamp_idx", keys={"object_uuid": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="location_country_timestamp_idx", keys={"location.country": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
    ]
    description: str = "1Password audit events and action tracking"

class ItemUsagesCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = ItemUsageSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="timestamp_desc", keys={"timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="item_timestamp_idx", keys={"item_uuid": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="vault_timestamp_idx", keys={"vault_uuid": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="user_timestamp_idx", keys={"user.uuid": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="action_timestamp_idx", keys={"action": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
    ]
    description: str = "1Password item usage events and access patterns"

class SignInAttemptsCollection(BaseCollectionSchema):
    json_schema: Dict[str, Any] = SignInAttemptSchema.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(name="uuid_unique", keys={"uuid": IndexDirection.ASCENDING}, unique=True),
        IndexDefinition(name="timestamp_desc", keys={"timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="target_user_timestamp_idx", keys={"target_user.uuid": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="category_timestamp_idx", keys={"category": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="type_timestamp_idx", keys={"type": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="location_country_timestamp_idx", keys={"location.country": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
        IndexDefinition(name="client_ip_timestamp_idx", keys={"client.ip_address": IndexDirection.ASCENDING, "timestamp": IndexDirection.DESCENDING}),
    ]
    description: str = "1Password sign-in attempts and authentication events"

# Main Database Schema
class OnePasswordEventsDatabase(BaseMongoDbSchema):
    database_name: str = "onepassword_events"
    collections: Dict[str, BaseCollectionSchema] = {
        "users": UsersCollection(),
        "devices": DevicesCollection(),
        "vaults": VaultsCollection(),
        "items": ItemsCollection(),
        "audit_events": AuditEventsCollection(),
        "item_usages": ItemUsagesCollection(),
        "sign_in_attempts": SignInAttemptsCollection(),
    }
    description: str = "1Password Events API database for security monitoring and audit trails"

# Export the database schema
database_schema = OnePasswordEventsDatabase()