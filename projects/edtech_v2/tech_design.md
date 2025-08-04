# Brazilian EdTech Platform - Technical Design Document

## Database Name: `brazilian_edtech`

## 1. Identify Application Workload

### 1.1 Data Requirements

Based on the Cogna Educação platform requirements, the application needs to manage:

- **Student and Applicant Data**: 2.4 million students, 57,000 applicants per semester
- **Document Management**: 22 documents per applicant, verification status, archival requirements
- **Funding/Scholarship Programs**: FIES and Prouni integration, approval workflows
- **Authentication and Authorization**: Self-service portal access, staff permissions
- **Protocol Tracking**: Unique identifiers for application tracking
- **Reporting and Analytics**: Performance metrics, funding statistics, audit trails
- **Educational Content**: Course information, institution data
- **Communication History**: Applicant interactions, notifications

### 1.2 Workload Table

| Action | Query Type | Information | Frequency | Priority |
|--------|------------|-------------|-----------|----------|
| Submit funding application | Write | applicant_id, personal_info, program_type, documents[], protocol_number, submission_timestamp | 57,000 per semester (peak: 1,000/hour) | High |
| Upload supporting document | Write | applicant_id, document_type, file_metadata, upload_timestamp | 1,254,000 per semester (22 docs × 57k applicants) | High |
| Check application status | Read | protocol_number, status, stage, last_updated | 500,000 per semester | High |
| Authenticate user | Read | email/cpf, password_hash, role, permissions | 100,000 per day during peak | High |
| Review/verify document | Write | document_id, reviewer_id, verification_status, comments | 1,254,000 per semester | High |
| Approve/reject application | Write | application_id, decision, approver_id, reason, timestamp | 57,000 per semester | High |
| Generate application report | Read | date_range, institution, program_type, aggregated stats | 500 per day | Medium |
| Archive old documents | Write | document_ids[], archive_date, storage_location | 10,000 per month | Low |
| Search student by CPF/name | Read | cpf, name, enrollment_status, courses | 50,000 per day | Medium |
| Track protocol progress | Read | protocol_number, stage_history[], current_stage | 200,000 per semester | High |
| Send notification | Write | recipient_id, message_type, content, channel, timestamp | 100,000 per semester | Medium |
| Update student profile | Write | student_id, profile_data, last_modified | 10,000 per day | Medium |
| View institution metrics | Read | institution_id, enrolled_count, application_stats | 1,000 per day | Low |
| Audit trail query | Read | entity_id, action_type, user_id, timestamp_range | 5,000 per day | Medium |

## 2. Map Schema Relationships

### 2.1 Identified Related Data

The platform manages several interconnected entities:

1. **Applicants/Students** ← → **Applications** (one-to-many)
2. **Applications** ← → **Documents** (one-to-many)
3. **Applications** ← → **Funding Programs** (many-to-one)
4. **Applications** ← → **Protocols** (one-to-one)
5. **Students** ← → **Institutions** (many-to-many)
6. **Documents** ← → **Reviewers/Staff** (many-to-many)
7. **Applications** ← → **Approval Workflows** (one-to-many)
8. **Users** ← → **Authentication Sessions** (one-to-many)
9. **All Entities** ← → **Audit Logs** (one-to-many)

### 2.2 Schema Relationship Map

```
┌─────────────────┐
│     Users       │
│ (Authentication)│
└────────┬────────┘
         │ 1:N
         ↓
┌─────────────────┐     1:N      ┌─────────────────┐
│   Applicants/   │─────────────→│  Applications   │
│    Students     │              │                 │
└─────────────────┘              └────────┬────────┘
         │                                │
         │ N:M                            │ 1:N
         ↓                                ↓
┌─────────────────┐              ┌─────────────────┐
│  Institutions   │              │   Documents     │
└─────────────────┘              └────────┬────────┘
                                          │
         ┌────────────────────────────────┘
         │ N:M
         ↓
┌─────────────────┐     1:N      ┌─────────────────┐
│  Staff/Reviewers│─────────────→│   Workflows     │
└─────────────────┘              └─────────────────┘
         
┌─────────────────┐              ┌─────────────────┐
│    Protocols    │←────1:1─────→│  Applications   │
└─────────────────┘              └─────────────────┘

┌─────────────────┐              ┌─────────────────┐
│ Funding Programs│←────N:1──────│  Applications   │
└─────────────────┘              └─────────────────┘

┌─────────────────┐
│   Audit Logs    │←────1:N──────All Entities
└─────────────────┘
```

### 2.3 Embedding vs Reference Decisions

Based on the workload analysis and relationship mapping:

#### Embed:
1. **Application → Basic Applicant Info**: Embed frequently accessed applicant details (name, CPF, contact) to avoid lookups during status checks
2. **Application → Protocol**: Embed protocol information as it's always accessed together
3. **Document → Metadata**: Embed file metadata, verification status, and reviewer comments
4. **User → Permissions**: Embed role and permissions for fast authentication
5. **Application → Stage History**: Embed workflow stages for protocol tracking

#### Reference:
1. **Application → Documents**: Reference due to high volume (22 docs per application) and independent lifecycle
2. **Student → Institution**: Reference as students may attend multiple institutions
3. **Document → Reviewers**: Reference to track multiple reviewers per document
4. **Application → Funding Program**: Reference to centrally manage program rules
5. **All Entities → Audit Logs**: Separate collection for compliance and archival

## 3. Apply Design Patterns

### 3.1 Computed Values Pattern
- **Application Statistics**: Pre-calculate approval rates, average processing time per institution
- **Student Metrics**: Compute total funding received, courses completed, engagement score
- **Document Processing Stats**: Calculate average verification time, rejection reasons

### 3.2 Bucket Pattern for Time-Series Data
- **Audit Logs**: Group by day/hour for efficient querying and archival
- **Application Submissions**: Bucket by semester for seasonal analysis
- **Notification History**: Group by month for retention policies

### 3.3 Polymorphic Pattern
- **Documents Collection**: Handle various document types (ID, income proof, academic records) with flexible schema
- **Workflows Collection**: Support different approval processes for FIES vs Prouni

### 3.4 Subset Pattern
- **Student Profile**: Keep active semester data in main document, archive historical data
- **Application Summary**: Maintain current status in application, detailed history in separate collection

### 3.5 Document Versioning
- **Application Schema**: Version field to handle regulatory changes
- **Document Requirements**: Version tracking for changing program requirements

### 3.6 Archival Pattern
- **Document Archive**: Move documents older than 2 years to MongoDB Atlas Online Archive
- **Completed Applications**: Archive after 5 years for compliance

## 4. Collections Design

### Primary Collections:

1. **users**: Authentication and authorization
2. **students**: Student profiles and enrollment data
3. **applications**: Funding/scholarship applications
4. **documents**: Supporting documents with verification
5. **protocols**: Application tracking system
6. **funding_programs**: FIES, Prouni program definitions
7. **institutions**: Educational institution data
8. **workflows**: Approval workflow definitions and instances
9. **notifications**: Communication history
10. **audit_logs**: Compliance and tracking
11. **application_stats**: Pre-computed analytics
12. **archived_documents**: Historical document storage

### Index Strategy:

1. **High-frequency queries**: Compound indexes on (protocol_number, status), (student_id, semester)
2. **Search operations**: Text indexes on student names, document content
3. **Time-based queries**: Date indexes with TTL for archival
4. **Unique constraints**: On CPF, protocol_number, student email
5. **Geospatial**: Institution locations for regional analysis

### Performance Optimizations:

1. **Sharding Strategy**: Shard on institution_id for horizontal scaling
2. **Read Preference**: Use secondary reads for reporting queries
3. **Write Concerns**: Majority write concern for critical operations
4. **Connection Pooling**: Optimize for 100k+ concurrent connections during peak
5. **Caching Layer**: Redis for session management and frequent lookups