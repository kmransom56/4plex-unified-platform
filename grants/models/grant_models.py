"""
Grant opportunity data models for 4-Plex Unified Platform
Extends the unified property models with grant-specific functionality
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

# Use the same base as unified models for consistency
Base = declarative_base()

# Grant-specific enums
class GrantType(str, Enum):
    REHABILITATION = "rehabilitation"
    ENERGY_EFFICIENCY = "energy_efficiency"
    SOLAR_INSTALLATION = "solar_installation"
    WEATHERIZATION = "weatherization"
    AFFORDABLE_HOUSING = "affordable_housing"
    COMMUNITY_DEVELOPMENT = "community_development"
    HISTORIC_PRESERVATION = "historic_preservation"
    ACCESSIBILITY = "accessibility"
    ENVIRONMENTAL = "environmental"
    GENERAL_RENOVATION = "general_renovation"

class FundingSource(str, Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    MUNICIPAL = "municipal"
    UTILITY = "utility"
    NONPROFIT = "nonprofit"
    FOUNDATION = "foundation"
    PRIVATE = "private"

class GrantStatus(str, Enum):
    DISCOVERED = "discovered"
    RESEARCHED = "researched"
    ELIGIBLE = "eligible"
    APPLIED = "applied"
    APPROVED = "approved"
    FUNDED = "funded"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ApplicationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class PropertyEligibility(str, Enum):
    SINGLE_FAMILY = "single_family"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    FOURPLEX = "4plex"
    MULTIFAMILY = "multifamily"
    MIXED_USE = "mixed_use"
    COMMERCIAL = "commercial"
    ALL_RESIDENTIAL = "all_residential"

# Pydantic models
class BaseGrantModel(BaseModel):
    """Base model for grant-related objects"""
    
    model_config = {"from_attributes": True, "use_enum_values": True}

class GrantOpportunity(BaseGrantModel):
    """Grant opportunity model aligned with property locations and types"""
    
    # Core identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None
    
    # Grant basic information
    program_name: str
    agency_name: str
    description: str
    grant_type: GrantType
    funding_source: FundingSource
    
    # Geographic eligibility
    eligible_counties: List[str] = Field(default_factory=list)
    eligible_municipalities: List[str] = Field(default_factory=list)
    statewide_eligible: bool = Field(default=False)
    nationwide_eligible: bool = Field(default=False)
    
    # Property eligibility
    property_types_eligible: List[PropertyEligibility] = Field(default_factory=list)
    min_units: Optional[int] = Field(default=None, ge=1)
    max_units: Optional[int] = Field(default=None, ge=1)
    owner_occupied_required: Optional[bool] = None
    income_limits: Optional[Dict[str, float]] = None
    
    # Funding details
    min_funding_amount: Optional[float] = Field(default=None, ge=0)
    max_funding_amount: Optional[float] = Field(default=None, ge=0)
    total_program_funding: Optional[float] = Field(default=None, ge=0)
    funding_percentage: Optional[float] = Field(default=None, ge=0, le=100)  # % of project cost covered
    match_required: Optional[float] = Field(default=None, ge=0, le=100)  # % match required
    
    # Timing and deadlines
    application_deadline: Optional[date] = None
    funding_period_start: Optional[date] = None
    funding_period_end: Optional[date] = None
    is_ongoing: bool = Field(default=False)
    is_rolling_deadline: bool = Field(default=False)
    
    # Application requirements
    application_url: Optional[str] = None
    application_materials: List[str] = Field(default_factory=list)
    eligibility_criteria: List[str] = Field(default_factory=list)
    required_documentation: List[str] = Field(default_factory=list)
    
    # Contact information
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    program_website: Optional[str] = None
    
    # Research metadata
    source_url: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    research_notes: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0, le=100)  # Confidence in data accuracy
    
    # Integration with properties
    applicable_properties: List[str] = Field(default_factory=list)  # Property IDs
    estimated_matches: int = Field(default=0, ge=0)
    
    @validator('eligible_counties')
    def validate_counties(cls, v):
        valid_counties = ["Fulton", "DeKalb", "Clayton", "Cobb", "Atlanta"]
        for county in v:
            if county not in valid_counties:
                raise ValueError(f'County must be one of: {", ".join(valid_counties)}')
        return v
    
    @validator('max_funding_amount')
    def validate_funding_range(cls, v, values):
        if v is not None and 'min_funding_amount' in values and values['min_funding_amount'] is not None:
            if v < values['min_funding_amount']:
                raise ValueError('max_funding_amount must be greater than min_funding_amount')
        return v

class PropertyGrantMatch(BaseGrantModel):
    """Model representing a match between a property and grant opportunity"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_id: str
    grant_id: str
    
    # Match scoring
    eligibility_score: float = Field(ge=0, le=100)  # How well property matches grant eligibility
    funding_potential: float = Field(ge=0)  # Estimated funding amount
    success_probability: float = Field(ge=0, le=100)  # Likelihood of approval
    overall_score: float = Field(ge=0, le=100)  # Combined score
    
    # Match details
    matching_criteria: List[str] = Field(default_factory=list)
    disqualifying_factors: List[str] = Field(default_factory=list)
    required_actions: List[str] = Field(default_factory=list)
    
    # Application tracking
    application_status: ApplicationStatus = ApplicationStatus.NOT_STARTED
    application_date: Optional[date] = None
    expected_decision_date: Optional[date] = None
    
    # Results
    approved_amount: Optional[float] = None
    rejection_reason: Optional[str] = None
    
    # Metadata
    matched_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class GrantApplication(BaseGrantModel):
    """Model for tracking grant applications"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_grant_match_id: str
    application_number: Optional[str] = None
    
    # Application details
    requested_amount: float = Field(ge=0)
    project_description: str
    budget_breakdown: Dict[str, float] = Field(default_factory=dict)
    timeline: Dict[str, str] = Field(default_factory=dict)
    
    # Status tracking
    status: ApplicationStatus = ApplicationStatus.NOT_STARTED
    submitted_date: Optional[date] = None
    review_start_date: Optional[date] = None
    decision_date: Optional[date] = None
    
    # Results
    approved_amount: Optional[float] = None
    conditions: List[str] = Field(default_factory=list)
    rejection_reason: Optional[str] = None
    appeal_deadline: Optional[date] = None
    
    # Documentation
    submitted_documents: List[str] = Field(default_factory=list)
    required_reports: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GrantResearchJob(BaseGrantModel):
    """Model for tracking grant research jobs"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    counties: List[str]
    grant_types: List[GrantType] = Field(default_factory=list)
    property_types: List[PropertyEligibility] = Field(default_factory=list)
    
    # Job status
    status: str = "started"
    urls_to_research: int = 0
    urls_completed: int = 0
    grants_discovered: int = 0
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # minutes
    
    # Results
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Configuration
    research_depth: str = Field(default="standard")  # shallow, standard, deep
    include_expired: bool = Field(default=False)
    min_funding_threshold: Optional[float] = None

# SQLAlchemy models for database persistence
class GrantOpportunityDB(Base):
    """Database model for grant opportunities"""
    
    __tablename__ = "grant_opportunities"
    
    id = Column(String, primary_key=True)
    external_id = Column(String)
    
    # Basic information
    program_name = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)
    description = Column(Text)
    grant_type = Column(String, nullable=False)
    funding_source = Column(String, nullable=False)
    
    # Geographic eligibility
    eligible_counties = Column(JSON)
    eligible_municipalities = Column(JSON)
    statewide_eligible = Column(Boolean, default=False)
    nationwide_eligible = Column(Boolean, default=False)
    
    # Property eligibility
    property_types_eligible = Column(JSON)
    min_units = Column(Integer)
    max_units = Column(Integer)
    owner_occupied_required = Column(Boolean)
    income_limits = Column(JSON)
    
    # Funding details
    min_funding_amount = Column(Float)
    max_funding_amount = Column(Float)
    total_program_funding = Column(Float)
    funding_percentage = Column(Float)
    match_required = Column(Float)
    
    # Timing
    application_deadline = Column(DateTime)
    funding_period_start = Column(DateTime)
    funding_period_end = Column(DateTime)
    is_ongoing = Column(Boolean, default=False)
    is_rolling_deadline = Column(Boolean, default=False)
    
    # Application information
    application_url = Column(String)
    application_materials = Column(JSON)
    eligibility_criteria = Column(JSON)
    required_documentation = Column(JSON)
    
    # Contact information
    contact_name = Column(String)
    contact_phone = Column(String)
    contact_email = Column(String)
    program_website = Column(String)
    
    # Research metadata
    source_url = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    research_notes = Column(Text)
    confidence_score = Column(Float, default=0.0)
    
    # Integration data
    applicable_properties = Column(JSON)
    estimated_matches = Column(Integer, default=0)
    
    # Relationships
    property_matches = relationship("PropertyGrantMatchDB", back_populates="grant")

class PropertyGrantMatchDB(Base):
    """Database model for property-grant matches"""
    
    __tablename__ = "property_grant_matches"
    
    id = Column(String, primary_key=True)
    property_id = Column(String, nullable=False)  # Links to UnifiedPropertyDB
    grant_id = Column(String, ForeignKey('grant_opportunities.id'), nullable=False)
    
    # Scoring
    eligibility_score = Column(Float, nullable=False)
    funding_potential = Column(Float, nullable=False)
    success_probability = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    # Match details
    matching_criteria = Column(JSON)
    disqualifying_factors = Column(JSON)
    required_actions = Column(JSON)
    
    # Application tracking
    application_status = Column(String, default="not_started")
    application_date = Column(DateTime)
    expected_decision_date = Column(DateTime)
    
    # Results
    approved_amount = Column(Float)
    rejection_reason = Column(Text)
    
    # Metadata
    matched_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    grant = relationship("GrantOpportunityDB", back_populates="property_matches")
    applications = relationship("GrantApplicationDB", back_populates="property_match")

class GrantApplicationDB(Base):
    """Database model for grant applications"""
    
    __tablename__ = "grant_applications"
    
    id = Column(String, primary_key=True)
    property_grant_match_id = Column(String, ForeignKey('property_grant_matches.id'), nullable=False)
    application_number = Column(String)
    
    # Application details
    requested_amount = Column(Float, nullable=False)
    project_description = Column(Text, nullable=False)
    budget_breakdown = Column(JSON)
    timeline = Column(JSON)
    
    # Status
    status = Column(String, default="not_started")
    submitted_date = Column(DateTime)
    review_start_date = Column(DateTime)
    decision_date = Column(DateTime)
    
    # Results
    approved_amount = Column(Float)
    conditions = Column(JSON)
    rejection_reason = Column(Text)
    appeal_deadline = Column(DateTime)
    
    # Documentation
    submitted_documents = Column(JSON)
    required_reports = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property_match = relationship("PropertyGrantMatchDB", back_populates="applications")

class GrantResearchJobDB(Base):
    """Database model for research jobs"""
    
    __tablename__ = "grant_research_jobs"
    
    id = Column(String, primary_key=True)
    counties = Column(JSON, nullable=False)
    grant_types = Column(JSON)
    property_types = Column(JSON)
    
    # Status
    status = Column(String, default="started")
    urls_to_research = Column(Integer, default=0)
    urls_completed = Column(Integer, default=0)
    grants_discovered = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    estimated_duration = Column(Integer)
    
    # Results
    results = Column(JSON)
    error_message = Column(Text)
    
    # Configuration
    research_depth = Column(String, default="standard")
    include_expired = Column(Boolean, default=False)
    min_funding_threshold = Column(Float)

# Utility functions
def grant_db_to_pydantic(db_grant: GrantOpportunityDB) -> GrantOpportunity:
    """Convert database model to Pydantic model"""
    return GrantOpportunity.from_orm(db_grant)

def grant_pydantic_to_db(pydantic_grant: GrantOpportunity) -> GrantOpportunityDB:
    """Convert Pydantic model to database model"""
    return GrantOpportunityDB(**pydantic_grant.dict(exclude_unset=True))

# Export all models
__all__ = [
    "GrantType", "FundingSource", "GrantStatus", "ApplicationStatus", "PropertyEligibility",
    "GrantOpportunity", "PropertyGrantMatch", "GrantApplication", "GrantResearchJob",
    "GrantOpportunityDB", "PropertyGrantMatchDB", "GrantApplicationDB", "GrantResearchJobDB",
    "grant_db_to_pydantic", "grant_pydantic_to_db"
]