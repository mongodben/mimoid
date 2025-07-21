"""Database schema for Cogna Educação Brazilian EdTech Platform"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, validator
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
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    DOCUMENTATION_REQUESTED = "documentation_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    ENROLLED = "enrolled"


class DocumentType(str, Enum):
    IDENTITY_DOCUMENT = "identity_document"
    PROOF_OF_INCOME = "proof_of_income"
    ACADEMIC_TRANSCRIPT = "academic_transcript"
    BIRTH_CERTIFICATE = "birth_certificate"
    PROOF_OF_RESIDENCE = "proof_of_residence"
    BANK_STATEMENT = "bank_statement"
    TAX_DECLARATION = "tax_declaration"
    EMPLOYMENT_LETTER = "employment_letter"
    MEDICAL_CERTIFICATE = "medical_certificate"
    MILITARY_CERTIFICATE = "military_certificate"
    VOTER_REGISTRATION = "voter_registration"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_RESUBMISSION = "requires_resubmission"


class FundingProgram(str, Enum):
    FIES = "fies"  # Student Financing Fund
    PROUNI = "prouni"  # University for All Program
    INSTITUTIONAL_SCHOLARSHIP = "institutional_scholarship"
    MERIT_SCHOLARSHIP = "merit_scholarship"
    NEED_BASED_AID = "need_based_aid"


class StudentStatus(str, Enum):
    PROSPECTIVE = "prospective"
    APPLICANT = "applicant"
    ENROLLED = "enrolled"
    ACTIVE = "active"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"
    DROPPED_OUT = "dropped_out"
    SUSPENDED = "suspended"


class CourseStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class AssessmentType(str, Enum):
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    PRESENTATION = "presentation"
    PARTICIPATION = "participation"
    FINAL_EXAM = "final_exam"


class GradeStatus(str, Enum):
    PENDING = "pending"
    GRADED = "graded"
    LATE_SUBMISSION = "late_submission"
    NOT_SUBMITTED = "not_submitted"
    EXCUSED = "excused"


class StaffRole(str, Enum):
    PROFESSOR = "professor"
    ADJUNCT_PROFESSOR = "adjunct_professor"
    TEACHING_ASSISTANT = "teaching_assistant"
    ACADEMIC_ADVISOR = "academic_advisor"
    ADMINISTRATOR = "administrator"
    FINANCIAL_AID_OFFICER = "financial_aid_officer"
    ADMISSIONS_OFFICER = "admissions_officer"
    SUPPORT_STAFF = "support_staff"


# Document schemas
class Institution(BaseMongoDbDocumentSchema):
    # Basic institution information
    name: str = Field(..., max_length=200)
    short_name: str = Field(
        ..., max_length=50, description="Acronym or abbreviated name"
    )
    institution_code: str = Field(
        ..., max_length=20, description="Unique institutional identifier"
    )

    # Location and contact
    address: Dict[str, str] = Field(..., description="Complete institutional address")
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=50, description="Brazilian state")
    postal_code: str = Field(
        ..., max_length=10, description="CEP - Brazilian postal code"
    )
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=255)
    website: Optional[str] = Field(None, max_length=500)

    # Educational details
    institution_type: str = Field(
        ..., max_length=50, description="University, college, vocational school"
    )
    accreditation_level: str = Field(
        ..., max_length=50, description="MEC accreditation level"
    )
    founded_year: int = Field(..., ge=1500, le=2030)

    # Operational information
    total_students: int = Field(default=0, ge=0)
    total_faculty: int = Field(default=0, ge=0)
    total_staff: int = Field(default=0, ge=0)
    annual_budget: Optional[float] = Field(
        None, ge=0, description="Annual budget in BRL"
    )

    # Academic offerings
    degree_levels: List[str] = Field(
        default=[], description="Undergraduate, graduate, doctoral, etc."
    )
    academic_areas: List[str] = Field(default=[], description="Fields of study offered")

    # Compliance and certification
    mec_code: str = Field(..., description="Ministry of Education institutional code")
    accreditation_date: Optional[datetime] = Field(None)
    accreditation_expiry: Optional[datetime] = Field(None)
    quality_rating: Optional[str] = Field(
        None, max_length=10, description="MEC quality assessment"
    )

    # Financial aid participation
    participates_fies: bool = Field(default=False)
    participates_prouni: bool = Field(default=False)
    scholarship_programs: List[str] = Field(
        default=[], description="Available scholarship programs"
    )

    # Status and metadata
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Student(BaseMongoDbDocumentSchema):
    # Personal information
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    full_name: str = Field(..., max_length=200, description="Complete legal name")

    # Brazilian identification
    cpf: str = Field(..., max_length=14, description="Brazilian tax ID (CPF)")
    rg: str = Field(..., max_length=20, description="Brazilian identity document")
    birth_date: datetime = Field(...)
    birth_place: str = Field(..., max_length=100, description="City and state of birth")
    nationality: str = Field(default="Brazilian", max_length=50)

    # Contact information
    email: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20, description="Brazilian phone format")
    mobile: Optional[str] = Field(None, max_length=20)

    # Address information
    address: Dict[str, str] = Field(..., description="Complete residential address")
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=50, description="Brazilian state")
    postal_code: str = Field(..., max_length=10, description="CEP")

    # Demographic information
    gender: Optional[str] = Field(None, max_length=20)
    ethnicity: Optional[str] = Field(
        None, max_length=50, description="Self-declared ethnicity"
    )
    marital_status: Optional[str] = Field(None, max_length=20)

    # Emergency contact
    emergency_contact: Dict[str, str] = Field(
        ..., description="Emergency contact information"
    )

    # Educational background
    previous_education: List[Dict[str, Any]] = Field(
        default=[], description="Educational history"
    )
    high_school_completion_year: Optional[int] = Field(None, ge=1980, le=2030)

    # Current status
    student_id: str = Field(..., max_length=50, description="Institutional student ID")
    primary_institution_id: PyObjectId = Field(
        ..., description="Primary enrolled institution"
    )
    status: StudentStatus = Field(default=StudentStatus.PROSPECTIVE)

    # Academic metrics
    current_gpa: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Brazilian grading scale 0-10"
    )
    total_credits: int = Field(default=0, ge=0)
    completed_credits: int = Field(default=0, ge=0)
    enrollment_date: Optional[datetime] = Field(None)
    expected_graduation: Optional[datetime] = Field(None)

    # Financial information
    family_income: Optional[float] = Field(
        None, ge=0, description="Monthly family income in BRL"
    )
    financial_aid_eligible: bool = Field(default=False)
    receives_financial_aid: bool = Field(default=False)

    # Special circumstances
    disabilities: List[str] = Field(
        default=[], description="Accessibility requirements"
    )
    special_needs: List[str] = Field(default=[], description="Additional support needs")

    # System information
    account_created: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None)
    portal_preferences: Dict[str, Any] = Field(
        default={}, description="User interface preferences"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Program(BaseMongoDbDocumentSchema):
    institution_id: PyObjectId = Field(..., description="Offering institution")

    # Program identification
    name: str = Field(..., max_length=200)
    program_code: str = Field(
        ..., max_length=50, description="Institutional program code"
    )
    mec_code: Optional[str] = Field(
        None, max_length=50, description="MEC program registration code"
    )

    # Program details
    degree_level: str = Field(
        ..., max_length=50, description="Undergraduate, graduate, doctoral"
    )
    degree_type: str = Field(
        ..., max_length=100, description="Bachelor, Master, PhD, etc."
    )
    field_of_study: str = Field(..., max_length=100, description="Academic area")
    specialization: Optional[str] = Field(None, max_length=100)

    # Academic structure
    total_credits: int = Field(
        ..., ge=0, description="Total credits required for completion"
    )
    duration_semesters: int = Field(..., ge=1, description="Expected program duration")
    modality: str = Field(..., max_length=50, description="On-site, online, hybrid")

    # Program description
    description: str = Field(
        ..., max_length=2000, description="Program overview and objectives"
    )
    career_outcomes: List[str] = Field(default=[], description="Expected career paths")
    prerequisites: List[str] = Field(default=[], description="Admission requirements")

    # Curriculum structure
    core_courses: List[Dict[str, Any]] = Field(
        default=[], description="Required course list"
    )
    elective_options: List[Dict[str, Any]] = Field(
        default=[], description="Optional courses"
    )
    capstone_requirements: Optional[Dict[str, Any]] = Field(
        None, description="Final project/thesis requirements"
    )

    # Financial information
    tuition_per_semester: float = Field(..., ge=0, description="Tuition cost in BRL")
    additional_fees: Dict[str, float] = Field(
        default={}, description="Additional program fees"
    )
    financial_aid_available: bool = Field(default=True)

    # Accreditation and quality
    accreditation_status: str = Field(..., max_length=50)
    quality_rating: Optional[str] = Field(
        None, max_length=10, description="MEC program evaluation"
    )
    last_evaluation_date: Optional[datetime] = Field(None)

    # Enrollment information
    max_enrollment: int = Field(..., ge=1, description="Maximum students per cohort")
    current_enrollment: int = Field(default=0, ge=0)
    admission_periods: List[Dict[str, Any]] = Field(
        default=[], description="Application deadlines"
    )

    # Program statistics
    completion_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    employment_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    average_starting_salary: Optional[float] = Field(
        None, ge=0, description="Graduate starting salary in BRL"
    )

    # Status
    is_active: bool = Field(default=True)
    start_date: datetime = Field(...)
    end_date: Optional[datetime] = Field(
        None, description="Program discontinuation date"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Application(BaseMongoDbDocumentSchema):
    # Application identification
    application_number: str = Field(
        ..., max_length=50, description="System-generated application ID"
    )
    protocol_number: str = Field(
        ..., max_length=50, description="Government protocol number"
    )

    # Applicant information
    student_id: PyObjectId = Field(..., description="Applying student")
    institution_id: PyObjectId = Field(..., description="Target institution")
    program_id: PyObjectId = Field(..., description="Target program")

    # Funding details
    funding_program: FundingProgram = Field(...)
    requested_amount: float = Field(
        ..., ge=0, description="Requested funding amount in BRL"
    )
    funding_percentage: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percentage of tuition covered"
    )

    # Application timeline
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    deadline_date: datetime = Field(...)
    decision_date: Optional[datetime] = Field(None)
    enrollment_deadline: Optional[datetime] = Field(None)

    # Status tracking
    status: ApplicationStatus = Field(default=ApplicationStatus.DRAFT)
    status_history: List[Dict[str, Any]] = Field(
        default=[], description="Status change log"
    )
    current_stage: str = Field(default="initial_review", max_length=100)

    # Application data
    application_form: Dict[str, Any] = Field(
        ..., description="Complete application form responses"
    )
    personal_statement: Optional[str] = Field(None, max_length=5000)
    academic_goals: Optional[str] = Field(None, max_length=2000)

    # Financial information
    family_income_declared: float = Field(
        ..., ge=0, description="Declared family income in BRL"
    )
    dependents_count: int = Field(default=0, ge=0)
    employment_status: str = Field(..., max_length=50)
    previous_funding: List[Dict[str, Any]] = Field(
        default=[], description="Previous financial aid history"
    )

    # Required documents tracking
    required_documents: List[DocumentType] = Field(
        ..., description="List of required document types"
    )
    submitted_documents: List[PyObjectId] = Field(
        default=[], description="References to submitted documents"
    )
    missing_documents: List[DocumentType] = Field(
        default=[], description="Outstanding required documents"
    )

    # Review process
    assigned_reviewer: Optional[PyObjectId] = Field(
        None, description="Staff member assigned for review"
    )
    review_notes: List[Dict[str, Any]] = Field(
        default=[], description="Internal review comments"
    )
    eligibility_check: Dict[str, Any] = Field(
        default={}, description="Automated eligibility verification"
    )

    # Decision information
    decision: Optional[str] = Field(None, max_length=50)
    decision_reason: Optional[str] = Field(None, max_length=1000)
    approved_amount: Optional[float] = Field(
        None, ge=0, description="Approved funding amount in BRL"
    )
    conditions: List[str] = Field(
        default=[], description="Approval conditions or requirements"
    )

    # Integration with government systems
    fies_protocol: Optional[str] = Field(
        None, max_length=100, description="FIES system protocol"
    )
    prouni_protocol: Optional[str] = Field(
        None, max_length=100, description="Prouni system protocol"
    )
    government_status: Optional[str] = Field(
        None, max_length=50, description="Government system status"
    )

    # Communication log
    notifications_sent: List[Dict[str, Any]] = Field(
        default=[], description="Communication history"
    )
    student_inquiries: List[Dict[str, Any]] = Field(
        default=[], description="Student questions and responses"
    )

    # Quality assurance
    data_verification_status: str = Field(default="pending", max_length=50)
    fraud_check_status: str = Field(default="pending", max_length=50)
    compliance_status: str = Field(default="pending", max_length=50)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Document(BaseMongoDbDocumentSchema):
    application_id: PyObjectId = Field(..., description="Associated application")
    student_id: PyObjectId = Field(..., description="Document owner")

    # Document identification
    document_type: DocumentType = Field(...)
    document_name: str = Field(
        ..., max_length=200, description="Original filename or document title"
    )
    document_description: Optional[str] = Field(None, max_length=500)

    # File information
    file_path: str = Field(..., max_length=1000, description="Storage path or URL")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    file_format: str = Field(..., max_length=20, description="PDF, JPG, PNG, etc.")
    mime_type: str = Field(..., max_length=100)

    # Document metadata
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = Field(
        None, description="Document validity expiration"
    )
    version: int = Field(default=1, ge=1, description="Document version number")

    # Verification status
    status: DocumentStatus = Field(default=DocumentStatus.PENDING)
    verification_date: Optional[datetime] = Field(None)
    verified_by: Optional[PyObjectId] = Field(
        None, description="Staff member who verified"
    )

    # Review information
    review_notes: Optional[str] = Field(
        None, max_length=1000, description="Reviewer comments"
    )
    rejection_reason: Optional[str] = Field(None, max_length=500)
    requires_resubmission: bool = Field(default=False)
    resubmission_instructions: Optional[str] = Field(None, max_length=1000)

    # Document processing
    ocr_extracted_text: Optional[str] = Field(
        None, description="Extracted text from OCR processing"
    )
    extracted_data: Dict[str, Any] = Field(
        default={}, description="Automatically extracted document data"
    )
    validation_results: Dict[str, Any] = Field(
        default={}, description="Automated validation results"
    )

    # Security and compliance
    checksum: str = Field(..., description="File integrity checksum")
    digital_signature: Optional[str] = Field(
        None, description="Digital signature if applicable"
    )
    encryption_status: bool = Field(default=True)
    access_log: List[Dict[str, Any]] = Field(
        default=[], description="Document access history"
    )

    # Archive information
    archived: bool = Field(default=False)
    archive_date: Optional[datetime] = Field(None)
    retention_period: Optional[int] = Field(
        None, description="Retention period in years"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Staff(BaseMongoDbDocumentSchema):
    # Personal information
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    full_name: str = Field(..., max_length=200)

    # Brazilian identification
    cpf: str = Field(..., max_length=14, description="Brazilian tax ID")
    employee_id: str = Field(
        ..., max_length=50, description="Institutional employee ID"
    )

    # Contact information
    email: str = Field(..., max_length=255, description="Institutional email")
    phone: str = Field(..., max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)

    # Employment information
    institution_id: PyObjectId = Field(..., description="Primary institution")
    department: str = Field(..., max_length=100)
    role: StaffRole = Field(...)
    title: str = Field(..., max_length=100, description="Job title")

    # Academic credentials
    education: List[Dict[str, Any]] = Field(
        default=[], description="Educational background"
    )
    certifications: List[Dict[str, Any]] = Field(
        default=[], description="Professional certifications"
    )
    areas_of_expertise: List[str] = Field(
        default=[], description="Subject matter expertise"
    )

    # Employment details
    hire_date: datetime = Field(...)
    employment_type: str = Field(
        ..., max_length=50, description="Full-time, part-time, contract"
    )
    salary_range: Optional[str] = Field(
        None, max_length=50, description="Salary classification"
    )

    # Work assignment
    workload_percentage: int = Field(
        default=100, ge=0, le=100, description="Percentage of full-time equivalent"
    )
    assigned_programs: List[PyObjectId] = Field(
        default=[], description="Programs staff member works with"
    )
    maximum_applications: Optional[int] = Field(
        None, ge=0, description="Max applications for review"
    )

    # Performance metrics
    applications_reviewed: int = Field(default=0, ge=0)
    average_review_time: Optional[float] = Field(
        None, ge=0, description="Average review time in hours"
    )
    quality_score: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Review quality rating"
    )

    # System access
    user_permissions: List[str] = Field(
        default=[], description="System access permissions"
    )
    last_login: Optional[datetime] = Field(None)
    account_status: str = Field(default="active", max_length=20)

    # Communication preferences
    notification_preferences: Dict[str, bool] = Field(
        default={}, description="Email and SMS preferences"
    )
    language_preference: str = Field(default="pt-BR", max_length=10)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Course(BaseMongoDbDocumentSchema):
    institution_id: PyObjectId = Field(..., description="Offering institution")
    program_id: PyObjectId = Field(..., description="Associated program")

    # Course identification
    course_code: str = Field(
        ..., max_length=20, description="Institutional course code"
    )
    name: str = Field(..., max_length=200)
    short_name: Optional[str] = Field(None, max_length=50)

    # Course details
    description: str = Field(..., max_length=2000)
    learning_objectives: List[str] = Field(
        default=[], description="Course learning outcomes"
    )
    prerequisites: List[str] = Field(default=[], description="Required prior courses")

    # Academic information
    credits: int = Field(..., ge=0, description="Credit hours")
    level: str = Field(..., max_length=50, description="Undergraduate, graduate level")
    subject_area: str = Field(..., max_length=100, description="Academic discipline")

    # Course structure
    total_hours: int = Field(..., ge=0, description="Total contact hours")
    lecture_hours: int = Field(default=0, ge=0)
    lab_hours: int = Field(default=0, ge=0)
    seminar_hours: int = Field(default=0, ge=0)

    # Delivery information
    modality: str = Field(..., max_length=50, description="In-person, online, hybrid")
    schedule: Dict[str, Any] = Field(
        default={}, description="Class schedule and timing"
    )
    classroom: Optional[str] = Field(
        None, max_length=100, description="Room assignment"
    )

    # Course content
    syllabus: Optional[str] = Field(
        None, max_length=10000, description="Detailed course syllabus"
    )
    reading_list: List[Dict[str, Any]] = Field(
        default=[], description="Required and recommended readings"
    )
    assessment_methods: List[Dict[str, Any]] = Field(
        default=[], description="Grading criteria and methods"
    )

    # Instructor information
    primary_instructor: PyObjectId = Field(..., description="Lead instructor")
    additional_instructors: List[PyObjectId] = Field(
        default=[], description="Co-instructors and TAs"
    )

    # Enrollment information
    max_enrollment: int = Field(..., ge=1)
    current_enrollment: int = Field(default=0, ge=0)
    waitlist_size: int = Field(default=0, ge=0)

    # Course metrics
    completion_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    average_grade: Optional[float] = Field(None, ge=0.0, le=10.0)
    student_satisfaction: Optional[float] = Field(None, ge=0.0, le=10.0)

    # Status and scheduling
    status: CourseStatus = Field(default=CourseStatus.ACTIVE)
    semester: str = Field(..., max_length=20, description="Academic semester/term")
    academic_year: int = Field(..., ge=2020, le=2030)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Enrollment(BaseMongoDbDocumentSchema):
    student_id: PyObjectId = Field(..., description="Enrolled student")
    course_id: PyObjectId = Field(..., description="Course enrolled in")
    program_id: Optional[PyObjectId] = Field(
        None, description="Associated degree program"
    )

    # Enrollment details
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    semester: str = Field(..., max_length=20)
    academic_year: int = Field(..., ge=2020, le=2030)

    # Status tracking
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ENROLLED)
    status_date: datetime = Field(default_factory=datetime.utcnow)
    withdrawal_date: Optional[datetime] = Field(None)
    completion_date: Optional[datetime] = Field(None)

    # Academic performance
    final_grade: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Final course grade"
    )
    letter_grade: Optional[str] = Field(
        None, max_length=5, description="Letter grade equivalent"
    )
    grade_points: Optional[float] = Field(
        None, ge=0.0, description="Grade points earned"
    )

    # Attendance and participation
    attendance_percentage: Optional[float] = Field(None, ge=0.0, le=1.0)
    participation_score: Optional[float] = Field(None, ge=0.0, le=10.0)

    # Assessment tracking
    midterm_grade: Optional[float] = Field(None, ge=0.0, le=10.0)
    assignments_completed: int = Field(default=0, ge=0)
    total_assignments: int = Field(default=0, ge=0)

    # Special circumstances
    accommodations: List[str] = Field(default=[], description="Academic accommodations")
    notes: Optional[str] = Field(
        None, max_length=1000, description="Special notes or circumstances"
    )

    # Financial information
    tuition_amount: Optional[float] = Field(
        None, ge=0, description="Tuition for this enrollment"
    )
    financial_aid_applied: Optional[float] = Field(
        None, ge=0, description="Financial aid amount"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Assessment(BaseMongoDbDocumentSchema):
    course_id: PyObjectId = Field(..., description="Associated course")
    student_id: PyObjectId = Field(..., description="Student being assessed")
    enrollment_id: PyObjectId = Field(..., description="Associated enrollment record")

    # Assessment details
    assessment_type: AssessmentType = Field(...)
    title: str = Field(..., max_length=200, description="Assignment or exam title")
    description: Optional[str] = Field(None, max_length=1000)

    # Scheduling
    assigned_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(...)
    submission_date: Optional[datetime] = Field(None)
    graded_date: Optional[datetime] = Field(None)

    # Grading information
    points_possible: float = Field(..., ge=0, description="Maximum points available")
    points_earned: Optional[float] = Field(None, ge=0, description="Points awarded")
    percentage_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    letter_grade: Optional[str] = Field(None, max_length=5)

    # Submission details
    submission_format: Optional[str] = Field(
        None, max_length=100, description="File, online, paper, etc."
    )
    submission_files: List[str] = Field(default=[], description="Submitted file paths")
    submission_text: Optional[str] = Field(None, description="Text-based submission")

    # Grading details
    graded_by: Optional[PyObjectId] = Field(None, description="Staff member who graded")
    rubric_scores: Dict[str, float] = Field(
        default={}, description="Detailed rubric scoring"
    )
    feedback: Optional[str] = Field(
        None, max_length=2000, description="Instructor feedback"
    )

    # Status and flags
    status: GradeStatus = Field(default=GradeStatus.PENDING)
    is_late: bool = Field(default=False)
    is_excused: bool = Field(default=False)
    requires_resubmission: bool = Field(default=False)

    # Academic integrity
    plagiarism_check: Optional[Dict[str, Any]] = Field(
        None, description="Plagiarism detection results"
    )
    originality_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Weight and importance
    weight_percentage: float = Field(
        ..., ge=0.0, le=1.0, description="Weight in final grade calculation"
    )
    category: Optional[str] = Field(
        None, max_length=50, description="Homework, exam, project, etc."
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Content(BaseMongoDbDocumentSchema):
    institution_id: PyObjectId = Field(..., description="Content owner institution")
    course_id: Optional[PyObjectId] = Field(
        None, description="Associated course if course-specific"
    )
    program_id: Optional[PyObjectId] = Field(
        None, description="Associated program if program-specific"
    )

    # Content identification
    title: str = Field(..., max_length=200)
    content_type: str = Field(
        ..., max_length=50, description="video, document, presentation, quiz, etc."
    )
    category: str = Field(
        ..., max_length=100, description="lecture, assignment, reading, etc."
    )

    # Content details
    description: Optional[str] = Field(None, max_length=1000)
    learning_objectives: List[str] = Field(
        default=[], description="What students will learn"
    )
    keywords: List[str] = Field(default=[], description="Searchable keywords")

    # File information
    file_path: Optional[str] = Field(
        None, max_length=1000, description="Storage path or URL"
    )
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    file_format: Optional[str] = Field(None, max_length=20)
    duration: Optional[int] = Field(
        None, ge=0, description="Content duration in seconds"
    )

    # Content metadata
    author: PyObjectId = Field(..., description="Content creator")
    contributors: List[PyObjectId] = Field(
        default=[], description="Additional contributors"
    )
    version: str = Field(default="1.0", max_length=20)

    # Educational metadata
    difficulty_level: Optional[str] = Field(
        None, max_length=50, description="Beginner, intermediate, advanced"
    )
    prerequisites: List[str] = Field(default=[], description="Required knowledge")
    estimated_time: Optional[int] = Field(
        None, ge=0, description="Estimated study time in minutes"
    )

    # Access and permissions
    visibility: str = Field(
        default="course",
        max_length=20,
        description="public, institution, course, private",
    )
    access_requirements: List[str] = Field(
        default=[], description="Requirements to access content"
    )

    # Usage metrics
    view_count: int = Field(default=0, ge=0)
    download_count: int = Field(default=0, ge=0)
    average_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    rating_count: int = Field(default=0, ge=0)

    # Content management
    is_published: bool = Field(default=False)
    publish_date: Optional[datetime] = Field(None)
    expiration_date: Optional[datetime] = Field(None)
    last_reviewed: Optional[datetime] = Field(None)

    # Technical metadata
    mime_type: Optional[str] = Field(None, max_length=100)
    encoding: Optional[str] = Field(None, max_length=50)
    resolution: Optional[str] = Field(
        None, max_length=20, description="Video resolution if applicable"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class FinancialAid(BaseMongoDbDocumentSchema):
    student_id: PyObjectId = Field(..., description="Aid recipient")
    application_id: Optional[PyObjectId] = Field(
        None, description="Associated application"
    )
    institution_id: PyObjectId = Field(..., description="Granting institution")

    # Aid identification
    aid_id: str = Field(..., max_length=50, description="Financial aid record ID")
    funding_program: FundingProgram = Field(...)
    aid_type: str = Field(
        ..., max_length=50, description="Grant, loan, scholarship, work-study"
    )

    # Award details
    award_amount: float = Field(..., ge=0, description="Total award amount in BRL")
    disbursed_amount: float = Field(
        default=0.0, ge=0, description="Amount actually disbursed"
    )
    remaining_amount: float = Field(..., ge=0, description="Undisbursed balance")

    # Academic period
    academic_year: int = Field(..., ge=2020, le=2030)
    semester: Optional[str] = Field(None, max_length=20)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)

    # Disbursement schedule
    disbursement_schedule: List[Dict[str, Any]] = Field(
        default=[], description="Payment schedule"
    )
    disbursement_history: List[Dict[str, Any]] = Field(
        default=[], description="Payment history"
    )

    # Eligibility and requirements
    eligibility_criteria: Dict[str, Any] = Field(
        default={}, description="Qualification requirements"
    )
    renewal_requirements: List[str] = Field(
        default=[], description="Requirements to maintain aid"
    )
    gpa_requirement: Optional[float] = Field(None, ge=0.0, le=10.0)
    credit_hour_requirement: Optional[int] = Field(None, ge=0)

    # Status tracking
    status: str = Field(
        ..., max_length=50, description="Active, suspended, completed, cancelled"
    )
    status_reason: Optional[str] = Field(None, max_length=500)
    last_status_change: datetime = Field(default_factory=datetime.utcnow)

    # Government integration
    government_approval_number: Optional[str] = Field(None, max_length=100)
    government_status: Optional[str] = Field(None, max_length=50)
    fies_contract_number: Optional[str] = Field(None, max_length=100)

    # Repayment information (for loans)
    repayment_terms: Optional[Dict[str, Any]] = Field(
        None, description="Loan repayment details"
    )
    grace_period_months: Optional[int] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0.0)

    # Performance tracking
    academic_progress: Dict[str, Any] = Field(
        default={}, description="Student progress monitoring"
    )
    compliance_status: str = Field(default="compliant", max_length=50)
    warning_flags: List[str] = Field(
        default=[], description="Academic or financial warnings"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


# Collection schema definitions
class InstitutionCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Institution.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="institution_code_unique",
            keys={"institution_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="mec_code_unique",
            keys={"mec_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="location_index",
            keys={"state": IndexDirection.ASCENDING, "city": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="active_institutions", keys={"is_active": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="funding_programs",
            keys={
                "participates_fies": IndexDirection.ASCENDING,
                "participates_prouni": IndexDirection.ASCENDING,
            },
        ),
    ]
    description: str = "Educational institutions in the Cogna network"


class StudentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Student.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="cpf_unique", keys={"cpf": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="student_id_unique",
            keys={"student_id": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="email_unique", keys={"email": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="institution_status",
            keys={
                "primary_institution_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="financial_aid_eligible",
            keys={
                "financial_aid_eligible": IndexDirection.ASCENDING,
                "family_income": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="location_index",
            keys={"state": IndexDirection.ASCENDING, "city": IndexDirection.ASCENDING},
        ),
        IndexDefinition(
            name="academic_performance",
            keys={
                "current_gpa": IndexDirection.DESCENDING,
                "completed_credits": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Student profiles and academic records"


class ProgramCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Program.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="program_code_institution",
            keys={
                "institution_id": IndexDirection.ASCENDING,
                "program_code": IndexDirection.ASCENDING,
            },
            unique=True,
        ),
        IndexDefinition(
            name="field_level_index",
            keys={
                "field_of_study": IndexDirection.ASCENDING,
                "degree_level": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="active_programs",
            keys={
                "is_active": IndexDirection.ASCENDING,
                "institution_id": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="tuition_index",
            keys={
                "tuition_per_semester": IndexDirection.ASCENDING,
                "financial_aid_available": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="quality_metrics",
            keys={
                "completion_rate": IndexDirection.DESCENDING,
                "employment_rate": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Academic programs and degrees offered"


class ApplicationCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Application.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="application_number_unique",
            keys={"application_number": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="protocol_number_unique",
            keys={"protocol_number": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="student_applications",
            keys={
                "student_id": IndexDirection.ASCENDING,
                "submission_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="status_processing",
            keys={
                "status": IndexDirection.ASCENDING,
                "submission_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="funding_program_status",
            keys={
                "funding_program": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
                "submission_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="reviewer_assignment",
            keys={
                "assigned_reviewer": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="deadline_tracking",
            keys={
                "deadline_date": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="institution_program",
            keys={
                "institution_id": IndexDirection.ASCENDING,
                "program_id": IndexDirection.ASCENDING,
                "submission_date": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Student funding applications (FIES, Prouni, scholarships)"


class DocumentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Document.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="application_documents",
            keys={
                "application_id": IndexDirection.ASCENDING,
                "document_type": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="student_documents",
            keys={
                "student_id": IndexDirection.ASCENDING,
                "upload_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="verification_queue",
            keys={
                "status": IndexDirection.ASCENDING,
                "upload_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="reviewer_workload",
            keys={
                "verified_by": IndexDirection.ASCENDING,
                "verification_date": IndexDirection.DESCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="document_type_status",
            keys={
                "document_type": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="archive_management",
            keys={
                "archived": IndexDirection.ASCENDING,
                "archive_date": IndexDirection.ASCENDING,
            },
        ),
    ]
    description: str = "Application supporting documents and verification"


class StaffCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Staff.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="employee_id_unique",
            keys={"employee_id": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="cpf_unique", keys={"cpf": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="email_unique", keys={"email": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="institution_role",
            keys={
                "institution_id": IndexDirection.ASCENDING,
                "role": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="department_staff",
            keys={
                "department": IndexDirection.ASCENDING,
                "account_status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="workload_capacity",
            keys={
                "role": IndexDirection.ASCENDING,
                "maximum_applications": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="performance_metrics",
            keys={
                "quality_score": IndexDirection.DESCENDING,
                "average_review_time": IndexDirection.ASCENDING,
            },
        ),
    ]
    description: str = "Faculty and administrative staff"


class CourseCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Course.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="course_code_institution",
            keys={
                "institution_id": IndexDirection.ASCENDING,
                "course_code": IndexDirection.ASCENDING,
            },
            unique=True,
        ),
        IndexDefinition(
            name="program_courses",
            keys={
                "program_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="instructor_courses",
            keys={
                "primary_instructor": IndexDirection.ASCENDING,
                "academic_year": IndexDirection.DESCENDING,
                "semester": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="subject_level",
            keys={
                "subject_area": IndexDirection.ASCENDING,
                "level": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="enrollment_tracking",
            keys={
                "current_enrollment": IndexDirection.DESCENDING,
                "max_enrollment": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="academic_period",
            keys={
                "academic_year": IndexDirection.DESCENDING,
                "semester": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
    ]
    description: str = "Course catalog and offerings"


class EnrollmentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Enrollment.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="student_course_enrollment",
            keys={
                "student_id": IndexDirection.ASCENDING,
                "course_id": IndexDirection.ASCENDING,
                "academic_year": IndexDirection.DESCENDING,
                "semester": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="course_enrollments",
            keys={
                "course_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="student_academic_progress",
            keys={
                "student_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
                "academic_year": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="program_enrollment",
            keys={
                "program_id": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="grade_performance",
            keys={
                "final_grade": IndexDirection.DESCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="completion_tracking",
            keys={
                "completion_date": IndexDirection.DESCENDING,
                "status": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
    ]
    description: str = "Student course enrollments and academic progress"


class AssessmentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Assessment.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="student_assessments",
            keys={
                "student_id": IndexDirection.ASCENDING,
                "course_id": IndexDirection.ASCENDING,
                "due_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="course_assessments",
            keys={
                "course_id": IndexDirection.ASCENDING,
                "assessment_type": IndexDirection.ASCENDING,
                "due_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="grading_queue",
            keys={
                "status": IndexDirection.ASCENDING,
                "submission_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="grader_workload",
            keys={
                "graded_by": IndexDirection.ASCENDING,
                "graded_date": IndexDirection.DESCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="due_date_tracking",
            keys={
                "due_date": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="enrollment_assessments",
            keys={
                "enrollment_id": IndexDirection.ASCENDING,
                "assigned_date": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Student assignments, exams, and grades"


class ContentCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Content.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="course_content",
            keys={
                "course_id": IndexDirection.ASCENDING,
                "category": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="program_content",
            keys={
                "program_id": IndexDirection.ASCENDING,
                "content_type": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="institution_content",
            keys={
                "institution_id": IndexDirection.ASCENDING,
                "visibility": IndexDirection.ASCENDING,
                "is_published": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="author_content",
            keys={
                "author": IndexDirection.ASCENDING,
                "created_at": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="content_search",
            keys={
                "keywords": IndexDirection.ASCENDING,
                "content_type": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="popularity_index",
            keys={
                "view_count": IndexDirection.DESCENDING,
                "average_rating": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Learning content and educational resources"


class FinancialAidCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = FinancialAid.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="aid_id_unique", keys={"aid_id": IndexDirection.ASCENDING}, unique=True
        ),
        IndexDefinition(
            name="student_aid",
            keys={
                "student_id": IndexDirection.ASCENDING,
                "academic_year": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="funding_program_tracking",
            keys={
                "funding_program": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
                "academic_year": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="institution_aid",
            keys={
                "institution_id": IndexDirection.ASCENDING,
                "funding_program": IndexDirection.ASCENDING,
                "status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="disbursement_tracking",
            keys={
                "status": IndexDirection.ASCENDING,
                "start_date": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="application_aid",
            keys={"application_id": IndexDirection.ASCENDING},
            sparse=True,
        ),
    ]
    description: str = "Financial aid awards and disbursements"


# Complete database schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "institutions": InstitutionCollectionSchema(),
        "students": StudentCollectionSchema(),
        "programs": ProgramCollectionSchema(),
        "applications": ApplicationCollectionSchema(),
        "documents": DocumentCollectionSchema(),
        "staff": StaffCollectionSchema(),
        "courses": CourseCollectionSchema(),
        "enrollments": EnrollmentCollectionSchema(),
        "assessments": AssessmentCollectionSchema(),
        "content": ContentCollectionSchema(),
        "financial_aid": FinancialAidCollectionSchema(),
    }
    database_name: str = "cogna_edtech_platform"
    description: str = "Cogna Educação Brazilian EdTech platform with student applications, funding programs, and academic management"


# Export the database schema
database_schema = MongoDbDataSchema()
