"""Database schema for MetaSteel Industries - Global Product Quality System"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field
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
class FacilityType(str, Enum):
    INTEGRATED_MILL = "integrated_mill"
    MINI_MILL = "mini_mill"
    FINISHING_PLANT = "finishing_plant"
    RESEARCH_CENTER = "research_center"


class ProductionLineStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"
    STARTUP = "startup"


class ProductType(str, Enum):
    HOT_ROLLED_COIL = "hot_rolled_coil"
    COLD_ROLLED_COIL = "cold_rolled_coil"
    GALVANIZED_STEEL = "galvanized_steel"
    STEEL_PLATE = "steel_plate"
    STEEL_PIPE = "steel_pipe"
    WIRE_ROD = "wire_rod"
    REBAR = "rebar"
    STRUCTURAL_STEEL = "structural_steel"


class QualityGrade(str, Enum):
    PRIME = "prime"
    COMMERCIAL = "commercial"
    SECONDARY = "secondary"
    SCRAP = "scrap"


class DefectSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"


class DefectType(str, Enum):
    SURFACE_DEFECT = "surface_defect"
    DIMENSIONAL_DEFECT = "dimensional_defect"
    CHEMICAL_DEFECT = "chemical_defect"
    MECHANICAL_DEFECT = "mechanical_defect"
    COATING_DEFECT = "coating_defect"


class CheckpointType(str, Enum):
    CHEMICAL_ANALYSIS = "chemical_analysis"
    DIMENSIONAL_CHECK = "dimensional_check"
    SURFACE_INSPECTION = "surface_inspection"
    MECHANICAL_TEST = "mechanical_test"
    TEMPERATURE_MEASUREMENT = "temperature_measurement"
    WEIGHT_CHECK = "weight_check"


class TestMethod(str, Enum):
    TENSILE_TEST = "tensile_test"
    HARDNESS_TEST = "hardness_test"
    IMPACT_TEST = "impact_test"
    BEND_TEST = "bend_test"
    ULTRASONIC_TEST = "ultrasonic_test"
    MAGNETIC_PARTICLE = "magnetic_particle"
    X_RAY_INSPECTION = "x_ray_inspection"


# Document schemas
class Facility(BaseMongoDbDocumentSchema):
    # Basic facility information
    facility_name: str = Field(..., max_length=200)
    facility_code: str = Field(
        ..., max_length=20, description="Unique facility identifier"
    )
    facility_type: FacilityType = Field(...)

    # Location information
    country: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    address: Dict[str, str] = Field(default={})
    coordinates: Dict[str, float] = Field(
        default={}, description="Latitude and longitude"
    )

    # Operational details
    annual_capacity_tons: int = Field(
        ..., ge=0, description="Annual production capacity"
    )
    operational_since: datetime = Field(...)

    # Quality certifications
    iso_certifications: List[str] = Field(
        default=[], description="ISO certifications held"
    )
    quality_standards: List[str] = Field(
        default=[], description="Quality standards compliance"
    )

    # Contact and management
    plant_manager: Optional[str] = Field(None, max_length=100)
    quality_manager: Optional[str] = Field(None, max_length=100)
    contact_info: Dict[str, str] = Field(default={})

    # Status
    is_active: bool = Field(default=True)
    last_audit_date: Optional[datetime] = Field(None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class ProductionLine(BaseMongoDbDocumentSchema):
    facility_id: PyObjectId = Field(..., description="Reference to facility")

    # Line identification
    line_name: str = Field(..., max_length=100)
    line_code: str = Field(..., max_length=20)
    line_number: int = Field(..., ge=1)

    # Production capabilities
    product_types: List[ProductType] = Field(
        ..., description="Types of products this line can produce"
    )
    max_width_mm: int = Field(..., ge=0, description="Maximum product width")
    max_thickness_mm: float = Field(..., ge=0, description="Maximum product thickness")
    production_speed_mpm: float = Field(
        ..., ge=0, description="Production speed in meters per minute"
    )
    annual_capacity_tons: int = Field(..., ge=0)

    # Equipment configuration
    equipment_list: List[Dict[str, Any]] = Field(
        default=[], description="List of equipment and sensors"
    )
    checkpoint_locations: List[Dict[str, Any]] = Field(
        default=[], description="Quality checkpoint positions"
    )

    # Current status
    status: ProductionLineStatus = Field(default=ProductionLineStatus.OPERATIONAL)
    current_product: Optional[str] = Field(
        None, description="Currently producing product"
    )
    current_speed_mpm: Optional[float] = Field(None, ge=0)
    current_temperature_c: Optional[float] = Field(None)

    # Performance metrics
    efficiency_percent: float = Field(default=85.0, ge=0, le=100)
    quality_score: float = Field(default=95.0, ge=0, le=100)
    downtime_hours_monthly: float = Field(default=24.0, ge=0)

    # Maintenance
    last_maintenance_date: Optional[datetime] = Field(None)
    next_maintenance_date: Optional[datetime] = Field(None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class Product(BaseMongoDbDocumentSchema):
    # Product identification
    product_code: str = Field(
        ..., max_length=50, description="Unique product identifier"
    )
    product_name: str = Field(..., max_length=200)
    product_type: ProductType = Field(...)
    grade: str = Field(..., max_length=50, description="Steel grade designation")

    # Physical specifications
    nominal_thickness_mm: Optional[float] = Field(None, ge=0)
    nominal_width_mm: Optional[int] = Field(None, ge=0)
    nominal_length_mm: Optional[int] = Field(None, ge=0)
    nominal_weight_kg: Optional[float] = Field(None, ge=0)

    # Chemical composition (typical steel elements)
    chemical_composition: Dict[str, float] = Field(
        default={}, description="Element percentages"
    )

    # Mechanical properties
    yield_strength_mpa: Optional[float] = Field(None, ge=0)
    tensile_strength_mpa: Optional[float] = Field(None, ge=0)
    elongation_percent: Optional[float] = Field(None, ge=0, le=100)
    hardness_hv: Optional[float] = Field(None, ge=0)

    # Quality specifications
    surface_quality: str = Field(..., max_length=50)
    tolerance_class: str = Field(..., max_length=20)

    # Applications and standards
    application_areas: List[str] = Field(default=[], description="Typical use cases")
    applicable_standards: List[str] = Field(
        default=[], description="Industry standards compliance"
    )

    # Customer and market info
    target_markets: List[str] = Field(
        default=[], description="Geographic or industry markets"
    )
    customer_specifications: Dict[str, Any] = Field(
        default={}, description="Customer-specific requirements"
    )

    # Status
    is_active: bool = Field(default=True)
    development_stage: str = Field(default="production", max_length=50)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class ProductionBatch(BaseMongoDbDocumentSchema):
    facility_id: PyObjectId = Field(..., description="Reference to facility")
    production_line_id: PyObjectId = Field(
        ..., description="Reference to production line"
    )
    product_id: PyObjectId = Field(..., description="Reference to product")

    # Batch identification
    batch_number: str = Field(..., max_length=50, description="Unique batch identifier")
    lot_number: str = Field(..., max_length=50)

    # Production details
    production_start: datetime = Field(...)
    production_end: Optional[datetime] = Field(None)
    planned_quantity_tons: float = Field(..., ge=0)
    actual_quantity_tons: Optional[float] = Field(None, ge=0)

    # Material traceability
    raw_material_batches: List[Dict[str, Any]] = Field(
        default=[], description="Raw material batch references"
    )
    heat_number: Optional[str] = Field(
        None, description="Steel heat number for traceability"
    )

    # Process parameters
    process_parameters: Dict[str, float] = Field(
        default={}, description="Key process settings"
    )
    average_temperature_c: Optional[float] = Field(None)
    rolling_speed_mpm: Optional[float] = Field(None, ge=0)

    # Quality summary
    quality_grade: QualityGrade = Field(default=QualityGrade.PRIME)
    overall_quality_score: Optional[float] = Field(None, ge=0, le=100)
    defect_count: int = Field(default=0, ge=0)
    checkpoint_count: int = Field(default=0, ge=0)

    # Customer and shipping
    customer_order_id: Optional[str] = Field(None, max_length=50)
    shipping_destination: Optional[str] = Field(None, max_length=200)

    # Status
    batch_status: str = Field(default="in_production", max_length=50)
    is_shipped: bool = Field(default=False)
    shipped_date: Optional[datetime] = Field(None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class QualityCheckpoint(BaseMongoDbDocumentSchema):
    facility_id: PyObjectId = Field(..., description="Reference to facility")
    production_line_id: PyObjectId = Field(
        ..., description="Reference to production line"
    )
    batch_id: PyObjectId = Field(..., description="Reference to production batch")

    # Checkpoint identification
    checkpoint_id: str = Field(
        ..., max_length=50, description="Unique checkpoint identifier"
    )
    checkpoint_type: CheckpointType = Field(...)
    location_km: float = Field(
        ..., ge=0, description="Position along production line in km"
    )

    # Measurement data
    measurement_timestamp: datetime = Field(default_factory=datetime.utcnow)
    sensor_readings: Dict[str, float] = Field(
        ..., description="Raw sensor measurements"
    )

    # Physical measurements
    thickness_mm: Optional[float] = Field(None, ge=0)
    width_mm: Optional[float] = Field(None, ge=0)
    temperature_c: Optional[float] = Field(None)
    weight_kg: Optional[float] = Field(None, ge=0)

    # Chemical composition (if applicable)
    chemical_analysis: Dict[str, float] = Field(
        default={}, description="Element concentrations"
    )

    # Mechanical properties (if tested)
    yield_strength_mpa: Optional[float] = Field(None, ge=0)
    tensile_strength_mpa: Optional[float] = Field(None, ge=0)
    hardness_hv: Optional[float] = Field(None, ge=0)
    elongation_percent: Optional[float] = Field(None, ge=0, le=100)

    # Quality assessment
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    pass_fail_status: str = Field(default="pass", max_length=20)
    deviation_from_spec: Dict[str, float] = Field(
        default={}, description="Deviations from specifications"
    )

    # Equipment and operator info
    equipment_id: Optional[str] = Field(None, max_length=50)
    operator_id: Optional[str] = Field(None, max_length=50)

    # Data quality
    confidence_level: float = Field(
        default=95.0, ge=0, le=100, description="Measurement confidence"
    )
    calibration_date: Optional[datetime] = Field(
        None, description="Last equipment calibration"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Defect(BaseMongoDbDocumentSchema):
    facility_id: PyObjectId = Field(..., description="Reference to facility")
    production_line_id: PyObjectId = Field(
        ..., description="Reference to production line"
    )
    batch_id: PyObjectId = Field(..., description="Reference to production batch")
    checkpoint_id: Optional[PyObjectId] = Field(
        None, description="Reference to quality checkpoint"
    )

    # Defect identification
    defect_id: str = Field(..., max_length=50, description="Unique defect identifier")
    defect_type: DefectType = Field(...)
    defect_subtype: str = Field(
        ..., max_length=100, description="Specific defect classification"
    )

    # Location and timing
    detection_timestamp: datetime = Field(default_factory=datetime.utcnow)
    location_km: float = Field(
        ..., ge=0, description="Position where defect was detected"
    )
    location_width_mm: Optional[float] = Field(None, description="Cross-width position")

    # Defect characteristics
    severity: DefectSeverity = Field(...)
    size_length_mm: Optional[float] = Field(None, ge=0)
    size_width_mm: Optional[float] = Field(None, ge=0)
    depth_mm: Optional[float] = Field(None, ge=0)

    # Detection method
    detection_method: str = Field(
        ..., max_length=50, description="How defect was detected"
    )
    automated_detection: bool = Field(default=True)
    ai_confidence: Optional[float] = Field(
        None, ge=0, le=100, description="AI detection confidence"
    )

    # Image and analysis data
    image_path: Optional[str] = Field(None, description="Path to defect image")
    image_analysis: Dict[str, Any] = Field(
        default={}, description="AI image analysis results"
    )

    # Root cause analysis
    probable_cause: Optional[str] = Field(None, max_length=500)
    process_correlation: Dict[str, Any] = Field(
        default={}, description="Process parameters at time of defect"
    )

    # Impact assessment
    affected_area_m2: Optional[float] = Field(None, ge=0)
    quality_impact_score: float = Field(..., ge=0, le=100)
    economic_impact_usd: Optional[float] = Field(None, ge=0)

    # Resolution
    corrective_action: Optional[str] = Field(None, max_length=1000)
    resolution_timestamp: Optional[datetime] = Field(None)
    resolved_by: Optional[str] = Field(None, max_length=100)

    # Quality decision
    material_disposition: str = Field(
        default="accept", max_length=50, description="Accept, rework, or scrap"
    )
    customer_notification_required: bool = Field(default=False)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class TestResult(BaseMongoDbDocumentSchema):
    facility_id: PyObjectId = Field(..., description="Reference to facility")
    batch_id: PyObjectId = Field(..., description="Reference to production batch")
    product_id: PyObjectId = Field(..., description="Reference to product")

    # Test identification
    test_id: str = Field(..., max_length=50, description="Unique test identifier")
    test_method: TestMethod = Field(...)
    test_standard: str = Field(..., max_length=50, description="Testing standard used")

    # Test execution
    test_date: datetime = Field(default_factory=datetime.utcnow)
    laboratory: str = Field(..., max_length=100, description="Testing laboratory")
    technician: str = Field(..., max_length=100)

    # Sample information
    sample_location: str = Field(
        ..., max_length=200, description="Where sample was taken"
    )
    sample_preparation: str = Field(
        ..., max_length=500, description="Sample preparation method"
    )

    # Test conditions
    test_temperature_c: Optional[float] = Field(None)
    test_environment: Dict[str, Any] = Field(
        default={}, description="Environmental conditions"
    )

    # Results
    test_results: Dict[str, float] = Field(..., description="Measured values")
    specification_limits: Dict[str, Dict[str, float]] = Field(
        default={}, description="Min/max acceptable values"
    )
    pass_fail_status: str = Field(..., max_length=20)

    # Statistical analysis
    measurement_uncertainty: Dict[str, float] = Field(
        default={}, description="Measurement uncertainties"
    )
    confidence_interval: Dict[str, List[float]] = Field(
        default={}, description="Confidence intervals"
    )

    # Compliance
    compliant_standards: List[str] = Field(
        default=[], description="Standards this result meets"
    )
    deviations: List[Dict[str, Any]] = Field(
        default=[], description="Any deviations from specifications"
    )

    # Certificate information
    certificate_number: Optional[str] = Field(None, max_length=50)
    certificate_issued: bool = Field(default=False)
    certificate_valid_until: Optional[datetime] = Field(None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


class CustomerSpecification(BaseMongoDbDocumentSchema):
    # Customer information
    customer_name: str = Field(..., max_length=200)
    customer_code: str = Field(..., max_length=50)

    # Product requirements
    product_family: str = Field(..., max_length=100)
    applicable_products: List[PyObjectId] = Field(
        ..., description="References to products"
    )

    # Specification details
    specification_name: str = Field(..., max_length=200)
    specification_version: str = Field(..., max_length=20)
    effective_date: datetime = Field(...)
    expiry_date: Optional[datetime] = Field(None)

    # Quality requirements
    chemical_requirements: Dict[str, Dict[str, float]] = Field(
        default={}, description="Element min/max requirements"
    )
    mechanical_requirements: Dict[str, Dict[str, float]] = Field(
        default={}, description="Strength/hardness requirements"
    )
    dimensional_tolerances: Dict[str, Dict[str, float]] = Field(
        default={}, description="Size tolerances"
    )
    surface_requirements: Dict[str, str] = Field(
        default={}, description="Surface quality specs"
    )

    # Testing requirements
    required_tests: List[TestMethod] = Field(
        default=[], description="Mandatory test methods"
    )
    sampling_plan: Dict[str, Any] = Field(
        default={}, description="Sampling requirements"
    )

    # Acceptance criteria
    acceptance_criteria: Dict[str, Any] = Field(..., description="Pass/fail criteria")
    quality_level: str = Field(
        ..., max_length=50, description="Quality level requirement"
    )

    # Documentation requirements
    certificate_required: bool = Field(default=True)
    test_report_required: bool = Field(default=True)
    traceability_required: bool = Field(default=True)

    # Status
    is_active: bool = Field(default=True)
    approval_status: str = Field(default="approved", max_length=50)
    approved_by: Optional[str] = Field(None, max_length=100)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)


# Collection schema definitions
class FacilityCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Facility.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="facility_code_unique",
            keys={"facility_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="location_index",
            keys={
                "country": IndexDirection.ASCENDING,
                "city": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="type_capacity_index",
            keys={
                "facility_type": IndexDirection.ASCENDING,
                "annual_capacity_tons": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="active_facilities", keys={"is_active": IndexDirection.ASCENDING}
        ),
    ]
    description: str = "Global steel production facilities"


class ProductionLineCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = ProductionLine.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="facility_lines",
            keys={
                "facility_id": IndexDirection.ASCENDING,
                "line_number": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="line_code_unique",
            keys={"line_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="status_performance",
            keys={
                "status": IndexDirection.ASCENDING,
                "efficiency_percent": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="product_capability", keys={"product_types": IndexDirection.ASCENDING}
        ),
        IndexDefinition(
            name="maintenance_schedule",
            keys={"next_maintenance_date": IndexDirection.ASCENDING},
            sparse=True,
        ),
    ]
    description: str = "Production line configurations and status"


class ProductCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Product.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="product_code_unique",
            keys={"product_code": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="product_type_grade",
            keys={
                "product_type": IndexDirection.ASCENDING,
                "grade": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="specifications_index",
            keys={
                "yield_strength_mpa": IndexDirection.DESCENDING,
                "tensile_strength_mpa": IndexDirection.DESCENDING,
            },
            sparse=True,
        ),
        IndexDefinition(
            name="active_products", keys={"is_active": IndexDirection.ASCENDING}
        ),
    ]
    description: str = "Steel product catalog and specifications"


class ProductionBatchCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = ProductionBatch.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="batch_number_unique",
            keys={"batch_number": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="facility_production_time",
            keys={
                "facility_id": IndexDirection.ASCENDING,
                "production_start": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="product_batches",
            keys={
                "product_id": IndexDirection.ASCENDING,
                "production_start": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="quality_tracking",
            keys={
                "quality_grade": IndexDirection.ASCENDING,
                "overall_quality_score": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="customer_orders",
            keys={"customer_order_id": IndexDirection.ASCENDING},
            sparse=True,
        ),
    ]
    description: str = "Production batch tracking and traceability"


class QualityCheckpointCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = QualityCheckpoint.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="batch_checkpoint_time",
            keys={
                "batch_id": IndexDirection.ASCENDING,
                "measurement_timestamp": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="facility_line_time",
            keys={
                "facility_id": IndexDirection.ASCENDING,
                "production_line_id": IndexDirection.ASCENDING,
                "measurement_timestamp": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="checkpoint_type_location",
            keys={
                "checkpoint_type": IndexDirection.ASCENDING,
                "location_km": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="quality_performance",
            keys={
                "quality_score": IndexDirection.DESCENDING,
                "pass_fail_status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="time_series_index",
            keys={"measurement_timestamp": IndexDirection.DESCENDING},
        ),
    ]
    description: str = "Quality measurement checkpoints (time-series data)"


class DefectCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = Defect.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="defect_id_unique",
            keys={"defect_id": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="batch_defects",
            keys={
                "batch_id": IndexDirection.ASCENDING,
                "detection_timestamp": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="facility_defect_tracking",
            keys={
                "facility_id": IndexDirection.ASCENDING,
                "defect_type": IndexDirection.ASCENDING,
                "severity": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="defect_analysis",
            keys={
                "defect_type": IndexDirection.ASCENDING,
                "detection_timestamp": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="resolution_tracking",
            keys={
                "material_disposition": IndexDirection.ASCENDING,
                "resolution_timestamp": IndexDirection.DESCENDING,
            },
        ),
    ]
    description: str = "Quality defects and corrective actions"


class TestResultCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = TestResult.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="test_id_unique",
            keys={"test_id": IndexDirection.ASCENDING},
            unique=True,
        ),
        IndexDefinition(
            name="batch_test_results",
            keys={
                "batch_id": IndexDirection.ASCENDING,
                "test_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="test_method_results",
            keys={
                "test_method": IndexDirection.ASCENDING,
                "pass_fail_status": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="certificate_tracking",
            keys={
                "certificate_number": IndexDirection.ASCENDING,
                "certificate_issued": IndexDirection.ASCENDING,
            },
            sparse=True,
        ),
    ]
    description: str = "Laboratory test results and certifications"


class CustomerSpecificationCollectionSchema(BaseCollectionSchema):
    json_schema: Dict[str, Any] = CustomerSpecification.model_json_schema()
    indexes: List[IndexDefinition] = [
        IndexDefinition(
            name="customer_specs",
            keys={
                "customer_code": IndexDirection.ASCENDING,
                "product_family": IndexDirection.ASCENDING,
            },
        ),
        IndexDefinition(
            name="specification_version",
            keys={
                "specification_name": IndexDirection.ASCENDING,
                "specification_version": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="active_specifications",
            keys={
                "is_active": IndexDirection.ASCENDING,
                "effective_date": IndexDirection.DESCENDING,
            },
        ),
        IndexDefinition(
            name="product_applicability",
            keys={"applicable_products": IndexDirection.ASCENDING},
        ),
    ]
    description: str = "Customer quality specifications and requirements"


# Complete database schema
class MongoDbDataSchema(BaseMongoDbSchema):
    collections: Dict[str, BaseCollectionSchema] = {
        "facilities": FacilityCollectionSchema(),
        "production_lines": ProductionLineCollectionSchema(),
        "products": ProductCollectionSchema(),
        "production_batches": ProductionBatchCollectionSchema(),
        "quality_checkpoints": QualityCheckpointCollectionSchema(),
        "defects": DefectCollectionSchema(),
        "test_results": TestResultCollectionSchema(),
        "customer_specifications": CustomerSpecificationCollectionSchema(),
    }
    database_name: str = "metasteel_gpqs"
    description: str = "Global Product Quality System for steel manufacturing with centralized quality control"


# Export the database schema
database_schema = MongoDbDataSchema()
