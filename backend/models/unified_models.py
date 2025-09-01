#!/usr/bin/env python3
"""
Unified data models for the 4-Plex Investment Platform
Combines foreclosure discovery and valuation analysis models
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

# Enums for standardized values
class PropertySource(str, Enum):
    FORECLOSURE_DISCOVERY = "foreclosure_discovery"
    MANUAL_ENTRY = "manual_entry"
    API_IMPORT = "api_import"
    AGENT_DISCOVERY = "agent_discovery"

class PropertyType(str, Enum):
    FOURPLEX = "4plex"
    MULTIFAMILY = "multifamily"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    OTHER = "other"

class ForeclosureStatus(str, Enum):
    PRE_FORECLOSURE = "pre_foreclosure"
    AUCTION = "auction"
    REO = "reo"
    TAX_SALE = "tax_sale"
    SHERIFF_SALE = "sheriff_sale"
    NONE = "none"

class DiscoveryStatus(str, Enum):
    DISCOVERED = "discovered"
    VALIDATED = "validated"
    ENRICHED = "enriched"
    ANALYZED = "analyzed"
    ARCHIVED = "archived"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Pydantic models for API serialization
class BasePropertyModel(BaseModel):
    """Base model with common fields"""
    
    model_config = {"from_attributes": True, "use_enum_values": True}

class UnifiedProperty(BasePropertyModel):
    """Unified property model combining discovery and valuation data"""
    
    # Core identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: PropertySource
    external_id: Optional[str] = None
    
    # Basic information
    name: Optional[str] = None
    address: str
    city: str
    county: str
    state: str = Field(default="GA")
    zip_code: str
    parcel_number: Optional[str] = None
    
    # Property characteristics
    property_type: PropertyType = PropertyType.FOURPLEX
    units: int = Field(default=4, ge=1, le=50)
    bedrooms: Optional[int] = Field(default=None, ge=0)
    bathrooms: Optional[float] = Field(default=None, ge=0)
    square_footage: Optional[int] = Field(default=None, ge=0)
    lot_size: Optional[float] = Field(default=None, ge=0)
    year_built: Optional[int] = Field(default=None, ge=1800, le=2030)
    
    # Financial data
    asking_price: Optional[float] = Field(default=None, ge=0)
    assessed_value: Optional[float] = Field(default=None, ge=0)
    market_value: Optional[float] = Field(default=None, ge=0)
    amount_owed: Optional[float] = Field(default=None, ge=0)
    
    # Foreclosure information
    foreclosure_status: Optional[ForeclosureStatus] = None
    foreclosure_stage: Optional[str] = None
    sale_date: Optional[date] = None
    redemption_period: Optional[str] = None
    court_case_number: Optional[str] = None
    
    # Code violations
    has_code_violations: bool = Field(default=False)
    violation_count: int = Field(default=0, ge=0)
    violation_types: List[str] = Field(default_factory=list)
    violation_details: Optional[Dict[str, Any]] = None
    
    # Investment analysis
    cap_rate: Optional[float] = Field(default=None, ge=0, le=50)
    noi: Optional[float] = Field(default=None)
    gross_income: Optional[float] = Field(default=None, ge=0)
    operating_expenses: Optional[float] = Field(default=None, ge=0)
    cash_flow: Optional[float] = Field(default=None)
    investment_score: Optional[int] = Field(default=None, ge=0, le=100)
    viability_score: Optional[float] = Field(default=None, ge=0, le=100)
    risk_level: Optional[RiskLevel] = None
    
    # Processing status
    discovery_status: DiscoveryStatus = DiscoveryStatus.DISCOVERED
    valuation_status: Optional[AnalysisStatus] = None
    
    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional data storage
    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    analysis_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        if v and len(v) not in [5, 9, 10]:  # 5 digits, 9 digits, or 5+4 format
            raise ValueError('Invalid ZIP code format')
        return v
    
    @validator('county')
    def validate_county(cls, v):
        valid_counties = ["Fulton", "DeKalb", "Clayton", "Cobb", "Atlanta"]
        if v not in valid_counties:
            raise ValueError(f'County must be one of: {", ".join(valid_counties)}')
        return v

class DiscoveryJob(BasePropertyModel):
    """Model for discovery job tracking"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    counties: List[str]
    filters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "started"
    agent_count: int = 0
    properties_found: int = 0
    properties_processed: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

class AnalysisJob(BasePropertyModel):
    """Model for property analysis job tracking"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_id: str
    priority: Priority = Priority.NORMAL
    status: AnalysisStatus = AnalysisStatus.PENDING
    options: Dict[str, Any] = Field(default_factory=dict)
    
    # Progress tracking
    progress: float = Field(default=0.0, ge=0, le=100)
    current_stage: Optional[str] = None
    
    # Timing
    queued_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class InvestmentScore(BasePropertyModel):
    """Detailed investment scoring breakdown"""
    
    property_id: str
    total_score: int = Field(ge=0, le=100)
    
    # Score components
    discovery_score: float = Field(default=0, ge=0, le=40)
    valuation_score: float = Field(default=0, ge=0, le=60)
    risk_adjustment: float = Field(default=0, ge=-20, le=0)
    
    # Detailed metrics
    discovery_metrics: Dict[str, float] = Field(default_factory=dict)
    valuation_metrics: Dict[str, float] = Field(default_factory=dict)
    risk_factors: Dict[str, float] = Field(default_factory=dict)
    
    # Confidence and recommendations
    confidence_level: float = Field(default=0, ge=0, le=100)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    calculation_version: str = Field(default="1.0")

class PropertyAlert(BasePropertyModel):
    """Model for high-priority property alerts"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_id: str
    alert_type: str
    priority: Priority
    title: str
    message: str
    
    # Alert criteria
    trigger_score: Optional[int] = None
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    is_active: bool = Field(default=True)
    acknowledged: bool = Field(default=False)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class SystemMetrics(BasePropertyModel):
    """Model for system performance metrics"""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Discovery metrics
    total_properties: int = 0
    properties_discovered_today: int = 0
    properties_in_queue: int = 0
    active_agents: int = 0
    
    # Analysis metrics
    analyses_completed_today: int = 0
    analyses_in_progress: int = 0
    analyses_failed_today: int = 0
    average_analysis_time: float = 0
    
    # Investment metrics
    high_priority_opportunities: int = 0
    medium_priority_opportunities: int = 0
    total_investment_value: float = 0
    average_investment_score: float = 0
    
    # System health
    discovery_engine_health: bool = True
    valuation_engine_health: bool = True
    database_health: bool = True
    api_response_time: float = 0

# SQLAlchemy models for database persistence
class UnifiedPropertyDB(Base):
    """Database model for unified properties"""
    
    __tablename__ = "unified_properties"
    
    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    external_id = Column(String)
    
    # Basic information
    name = Column(String)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    county = Column(String, nullable=False)
    state = Column(String, default="GA")
    zip_code = Column(String)
    parcel_number = Column(String)
    
    # Property characteristics
    property_type = Column(String, default="4plex")
    units = Column(Integer, default=4)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_footage = Column(Integer)
    lot_size = Column(Float)
    year_built = Column(Integer)
    
    # Financial data
    asking_price = Column(Float)
    assessed_value = Column(Float)
    market_value = Column(Float)
    amount_owed = Column(Float)
    
    # Foreclosure information
    foreclosure_status = Column(String)
    foreclosure_stage = Column(String)
    sale_date = Column(DateTime)
    redemption_period = Column(String)
    court_case_number = Column(String)
    
    # Code violations
    has_code_violations = Column(Boolean, default=False)
    violation_count = Column(Integer, default=0)
    violation_types = Column(JSON)
    violation_details = Column(JSON)
    
    # Investment analysis
    cap_rate = Column(Float)
    noi = Column(Float)
    gross_income = Column(Float)
    operating_expenses = Column(Float)
    cash_flow = Column(Float)
    investment_score = Column(Integer)
    viability_score = Column(Float)
    risk_level = Column(String)
    
    # Processing status
    discovery_status = Column(String, default="discovered")
    valuation_status = Column(String)
    
    # Metadata
    discovered_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data storage
    raw_data = Column(JSON)
    analysis_data = Column(JSON)

class DiscoveryJobDB(Base):
    """Database model for discovery jobs"""
    
    __tablename__ = "discovery_jobs"
    
    id = Column(String, primary_key=True)
    counties = Column(JSON, nullable=False)
    filters = Column(JSON)
    status = Column(String, default="started")
    agent_count = Column(Integer, default=0)
    properties_found = Column(Integer, default=0)
    properties_processed = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    results = Column(JSON)

class AnalysisJobDB(Base):
    """Database model for analysis jobs"""
    
    __tablename__ = "analysis_jobs"
    
    id = Column(String, primary_key=True)
    property_id = Column(String, nullable=False)
    priority = Column(String, default="normal")
    status = Column(String, default="pending")
    options = Column(JSON)
    progress = Column(Float, default=0)
    current_stage = Column(String)
    queued_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    results = Column(JSON)
    error_message = Column(Text)

# Utility functions for model conversions
def property_db_to_pydantic(db_property: UnifiedPropertyDB) -> UnifiedProperty:
    """Convert database model to Pydantic model"""
    return UnifiedProperty.from_orm(db_property)

def property_pydantic_to_db(pydantic_property: UnifiedProperty) -> UnifiedPropertyDB:
    """Convert Pydantic model to database model"""
    return UnifiedPropertyDB(**pydantic_property.dict(exclude_unset=True))

# Export all models
__all__ = [
    "PropertySource", "PropertyType", "ForeclosureStatus", "DiscoveryStatus",
    "AnalysisStatus", "RiskLevel", "Priority", "UnifiedProperty", "DiscoveryJob",
    "AnalysisJob", "InvestmentScore", "PropertyAlert", "SystemMetrics",
    "UnifiedPropertyDB", "DiscoveryJobDB", "AnalysisJobDB",
    "property_db_to_pydantic", "property_pydantic_to_db"
]