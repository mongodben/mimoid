# Technical Design: 1Password Events API Database

## Input Analysis

The 1Password Events API is a security-focused REST API that provides access to audit events, item usages, and sign-in attempts for 1Password accounts. The API follows OpenAPI 3.0 specification and includes comprehensive event tracking for security monitoring and compliance purposes.

## API Overview

- **Service**: 1Password Events API v1.2.0
- **Purpose**: Security event monitoring and audit trail management
- **Authentication**: JWT-based service account tokens
- **Geographic Regions**: Multiple endpoints (US, CA, EU, Enterprise)

## Core Entity Analysis

### Primary Event Types
1. **Audit Events** (`/api/v1/auditevents`) - Actions performed by team members
2. **Item Usages** (`/api/v1/itemusages`) - Usage of items in shared vaults  
3. **Sign-in Attempts** (`/api/v1/signinattempts`) - Authentication attempts (success/failure)

### Key Data Structures

#### Audit Events
- **Actions**: 70+ predefined actions (activate, update, delete, create, etc.)
- **Object Types**: 28 object types (account, user, device, vault, item, etc.)
- **Actors**: Users performing actions
- **Temporal Data**: RFC3339 timestamps
- **Geolocation**: City, country, region, coordinates
- **Session Context**: Device and session information

#### Item Usages
- **Actions**: 8 usage types (fill, reveal, export, share, etc.)
- **Items**: References to vault items
- **Users**: Who accessed the item
- **Client Info**: App details, OS, platform
- **Versioning**: Item version tracking

#### Sign-in Attempts
- **Categories**: 7 attempt categories (success, various failure types)
- **Types**: 30+ specific failure reasons
- **Geographic Blocking**: Continent/country-based restrictions
- **MFA Details**: Multi-factor authentication results
- **Client Fingerprinting**: Detailed device/browser information

## Database Design Strategy

### Collections Structure

1. **audit_events** - Primary audit trail collection
2. **item_usages** - Item access tracking
3. **sign_in_attempts** - Authentication event log
4. **users** - User directory and profiles
5. **devices** - Device registry and metadata
6. **sessions** - Active session tracking
7. **vaults** - Vault definitions and access control
8. **items** - Vault item catalog
9. **locations** - Geographic data cache

### Relationships

- Users → Multiple devices, sessions, events
- Devices → Sessions, events
- Vaults → Items, access events
- Sessions → Events, sign-in attempts
- Locations → Events, sign-in attempts (cached geo data)

### Indexing Strategy

**Performance Indexes:**
- Time-based queries: `timestamp` descending
- User activity: `user_uuid + timestamp`
- Device tracking: `device_uuid + timestamp`
- Geographic analysis: `location.country + timestamp`

**Security Indexes:**
- Failed login tracking: `category + timestamp` (for sign-in attempts)
- Audit trail: `action + object_type + timestamp`
- Item access: `item_uuid + timestamp`

### Data Patterns

**Time-Series Optimization:**
- Events stored with descending timestamp indexes
- Partition consideration by date ranges
- Bulk insert patterns for high-volume events

**Security-First Design:**
- Immutable event records
- Comprehensive audit trails
- Geographic anomaly detection support
- Failed authentication pattern analysis

**Cursor-Based Pagination:**
- Support for cursor-based pagination as per API design
- Efficient large dataset traversal
- Stateless pagination tokens

## Performance Considerations

- **High Volume**: Design for millions of events per day
- **Real-time Queries**: Sub-second response for recent events
- **Historical Analysis**: Efficient queries across time ranges
- **Geographic Queries**: Optimized location-based filtering
- **Compliance**: Long-term retention with efficient archival

## Security Features

- **Audit Trail Integrity**: Immutable event logging
- **Access Pattern Analysis**: User behavior tracking
- **Anomaly Detection**: Geographic and temporal anomalies
- **Compliance Reporting**: SOX, GDPR, HIPAA audit support
- **Retention Policies**: Configurable data lifecycle management