"""
Grant research API endpoints for 4-Plex Unified Platform
Integrates grant discovery and matching with property analysis
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# Import the unified platform dependencies (these will need to be updated)
# from backend.common.database import get_db
# from backend.models.unified_models import UnifiedProperty

# Import grant models
from grants.models.grant_models import (
    GrantOpportunity, PropertyGrantMatch, GrantApplication, GrantResearchJob,
    GrantType, FundingSource, PropertyEligibility, ApplicationStatus,
    GrantOpportunityDB, PropertyGrantMatchDB, GrantApplicationDB, GrantResearchJobDB
)

# Import research utilities
from grants.coding.updated_research_urls import get_county_urls, get_priority_urls, COUNTY_SPECIFIC_URLS

router = APIRouter(prefix="/api/v1/grants", tags=["grants"])

# --- Grant Discovery Endpoints ---

@router.post("/research/start", response_model=Dict[str, Any])
async def start_grant_research(
    background_tasks: BackgroundTasks,
    counties: List[str] = Query(..., description="Target counties for research"),
    grant_types: Optional[List[GrantType]] = Query(None, description="Specific grant types to focus on"),
    property_types: Optional[List[PropertyEligibility]] = Query(None, description="Property types to match"),
    research_depth: str = Query("standard", description="Research depth: shallow, standard, deep"),
    include_expired: bool = Query(False, description="Include expired grants"),
    min_funding_threshold: Optional[float] = Query(None, description="Minimum funding amount")
):
    """
    Start a comprehensive grant research job across specified counties
    
    **Business Value**: Automated discovery of funding opportunities
    **Revenue Impact**: Enables $500-5000 premium per property analysis
    """
    
    # Validate counties
    valid_counties = ["Fulton", "DeKalb", "Clayton", "Cobb", "Atlanta"]
    invalid_counties = [c for c in counties if c not in valid_counties]
    if invalid_counties:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid counties: {invalid_counties}. Valid options: {valid_counties}"
        )
    
    # Create research job
    job = GrantResearchJob(
        counties=counties,
        grant_types=grant_types or [],
        property_types=property_types or [],
        research_depth=research_depth,
        include_expired=include_expired,
        min_funding_threshold=min_funding_threshold,
        urls_to_research=sum(len(get_county_urls(county.lower())) for county in counties)
    )
    
    # Add background task (this would integrate with the AutoGen agents)
    background_tasks.add_task(execute_grant_research, job)
    
    return {
        "job_id": job.id,
        "status": "started",
        "counties": counties,
        "estimated_duration": job.urls_to_research * 2,  # 2 minutes per URL estimate
        "urls_to_research": job.urls_to_research,
        "message": "Grant research job started. Check status endpoint for progress."
    }

@router.get("/research/status/{job_id}", response_model=Dict[str, Any])
async def get_research_status(job_id: str):
    """
    Get the status of a grant research job
    
    **Tracking**: Real-time progress monitoring for client transparency
    """
    
    # This would query the database for the job status
    # For now, return a mock response
    return {
        "job_id": job_id,
        "status": "completed",  # started, in_progress, completed, failed
        "progress": 100.0,
        "urls_completed": 45,
        "urls_total": 45,
        "grants_discovered": 23,
        "estimated_time_remaining": 0,
        "current_activity": "Analysis complete",
        "results_available": True
    }

@router.get("/research/results/{job_id}", response_model=List[GrantOpportunity])
async def get_research_results(job_id: str):
    """
    Get the discovered grant opportunities from a research job
    
    **Output**: Structured grant data for property matching
    """
    
    # This would retrieve the actual results from the database
    # For now, return mock data showing the structure
    mock_grants = [
        GrantOpportunity(
            program_name="Fulton County HOME Program",
            agency_name="Fulton County Community Development",
            description="Provides rehabilitation loans for multifamily properties",
            grant_type=GrantType.REHABILITATION,
            funding_source=FundingSource.COUNTY,
            eligible_counties=["Fulton"],
            property_types_eligible=[PropertyEligibility.FOURPLEX, PropertyEligibility.MULTIFAMILY],
            min_funding_amount=10000.0,
            max_funding_amount=75000.0,
            funding_percentage=80.0,
            match_required=20.0,
            application_deadline=date(2025, 6, 30),
            source_url="https://www.fultoncountyga.gov/services/community-development/home-program",
            confidence_score=85.0,
            contact_email="homeprogram@fultoncountyga.gov",
            eligibility_criteria=[
                "Property must be in Fulton County",
                "Maximum 4 units",
                "Owner occupancy required for first year",
                "Income limits apply"
            ]
        )
    ]
    
    return mock_grants

# --- Property-Grant Matching Endpoints ---

@router.post("/match/property/{property_id}", response_model=List[PropertyGrantMatch])
async def match_grants_to_property(
    property_id: str,
    min_score_threshold: float = Query(60.0, description="Minimum match score (0-100)"),
    max_results: int = Query(10, description="Maximum number of matches to return")
):
    """
    Find grant opportunities that match a specific property
    
    **Core Feature**: AI-powered grant-to-property matching
    **Business Value**: Automatic identification of funding opportunities
    """
    
    # This would:
    # 1. Retrieve the property from UnifiedPropertyDB
    # 2. Query available grants based on property characteristics
    # 3. Calculate matching scores using business logic
    # 4. Return ranked matches
    
    mock_matches = [
        PropertyGrantMatch(
            property_id=property_id,
            grant_id="fulton-home-program-2025",
            eligibility_score=85.0,
            funding_potential=50000.0,
            success_probability=75.0,
            overall_score=80.0,
            matching_criteria=[
                "Property located in Fulton County",
                "4-plex property type eligible",
                "Rehabilitation focus matches grant",
                "Property value within program limits"
            ],
            required_actions=[
                "Verify owner occupancy requirement",
                "Obtain property condition assessment",
                "Complete income documentation",
                "Prepare rehabilitation scope of work"
            ]
        )
    ]
    
    return mock_matches

@router.post("/match/batch", response_model=Dict[str, Any])
async def batch_match_properties(
    background_tasks: BackgroundTasks,
    property_ids: List[str],
    counties: Optional[List[str]] = Query(None, description="Limit to specific counties"),
    grant_types: Optional[List[GrantType]] = Query(None, description="Limit to specific grant types"),
    min_funding: Optional[float] = Query(None, description="Minimum funding amount")
):
    """
    Match multiple properties to grant opportunities in bulk
    
    **Scalability**: Handle portfolio-level grant analysis
    **Revenue Model**: Premium service for property management companies
    """
    
    job_id = f"batch-match-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Add background task for bulk processing
    background_tasks.add_task(execute_batch_matching, property_ids, counties, grant_types, min_funding)
    
    return {
        "job_id": job_id,
        "properties_queued": len(property_ids),
        "estimated_completion": "10-30 minutes",
        "status": "started",
        "message": "Batch matching job started. Use job_id to check progress."
    }

# --- Grant Application Management Endpoints ---

@router.post("/applications/create", response_model=GrantApplication)
async def create_grant_application(
    property_grant_match_id: str,
    requested_amount: float,
    project_description: str,
    budget_breakdown: Dict[str, float],
    timeline: Dict[str, str]
):
    """
    Create a new grant application based on a property-grant match
    
    **Service Extension**: Full application management workflow
    **Revenue Opportunity**: $2,000-5,000 per application service
    """
    
    application = GrantApplication(
        property_grant_match_id=property_grant_match_id,
        requested_amount=requested_amount,
        project_description=project_description,
        budget_breakdown=budget_breakdown,
        timeline=timeline
    )
    
    # This would save to database and return the created application
    return application

@router.get("/applications/{application_id}", response_model=GrantApplication)
async def get_grant_application(application_id: str):
    """Get grant application details"""
    
    # Mock response showing application structure
    return GrantApplication(
        id=application_id,
        property_grant_match_id="match-123",
        requested_amount=45000.0,
        project_description="Complete rehabilitation of 4-plex property including energy efficiency upgrades",
        budget_breakdown={
            "HVAC_System": 15000.0,
            "Insulation": 8000.0,
            "Windows": 12000.0,
            "Solar_Installation": 10000.0
        },
        timeline={
            "Planning": "30 days",
            "Permits": "45 days", 
            "Construction": "120 days",
            "Completion": "180 days total"
        },
        status=ApplicationStatus.IN_PROGRESS
    )

@router.put("/applications/{application_id}/status", response_model=Dict[str, Any])
async def update_application_status(
    application_id: str,
    status: ApplicationStatus,
    notes: Optional[str] = None
):
    """Update grant application status"""
    
    return {
        "application_id": application_id,
        "status": status,
        "updated_at": datetime.utcnow(),
        "notes": notes,
        "message": "Application status updated successfully"
    }

# --- Analytics and Reporting Endpoints ---

@router.get("/analytics/county/{county}", response_model=Dict[str, Any])
async def get_county_grant_analytics(county: str):
    """
    Get grant opportunity analytics for a specific county
    
    **Business Intelligence**: Market analysis for funding opportunities
    **Customer Value**: Data-driven investment decisions
    """
    
    return {
        "county": county,
        "total_grants": 15,
        "total_funding_available": 2500000.0,
        "average_grant_size": 166667.0,
        "grant_types_breakdown": {
            "rehabilitation": 6,
            "energy_efficiency": 4,
            "affordable_housing": 3,
            "weatherization": 2
        },
        "funding_sources": {
            "county": 8,
            "state": 4,
            "federal": 2,
            "utility": 1
        },
        "property_eligibility": {
            "fourplex": 12,
            "multifamily": 10,
            "duplex": 8,
            "triplex": 8
        },
        "upcoming_deadlines": 3,
        "rolling_deadlines": 5
    }

@router.get("/analytics/portfolio", response_model=Dict[str, Any])
async def get_portfolio_grant_potential(property_ids: List[str] = Query(...)):
    """
    Analyze grant potential across a property portfolio
    
    **Premium Feature**: Portfolio-level funding optimization
    **Revenue Justification**: Demonstrates ROI for platform investment
    """
    
    return {
        "properties_analyzed": len(property_ids),
        "total_funding_potential": 850000.0,
        "average_per_property": 85000.0,
        "high_potential_properties": 6,
        "medium_potential_properties": 4,
        "applications_recommended": 8,
        "estimated_success_rate": 22.5,
        "projected_funding": 191250.0,
        "roi_multiplier": 3.2,
        "recommendations": [
            "Prioritize energy efficiency grants in Q2",
            "Bundle applications for similar properties",
            "Focus on Fulton County programs first",
            "Consider owner occupancy requirements"
        ]
    }

# --- Background Task Functions ---

async def execute_grant_research(job: GrantResearchJob):
    """
    Execute the grant research using AutoGen agents
    This would integrate with the research_agents.py system
    """
    
    # This function would:
    # 1. Initialize the AutoGen agent system
    # 2. Configure agents with county-specific URLs
    # 3. Execute the web scraping and analysis
    # 4. Parse and structure the results
    # 5. Save grant opportunities to database
    # 6. Update job status
    
    pass

async def execute_batch_matching(
    property_ids: List[str], 
    counties: Optional[List[str]], 
    grant_types: Optional[List[GrantType]], 
    min_funding: Optional[float]
):
    """
    Execute bulk property-to-grant matching
    """
    
    # This function would:
    # 1. Retrieve all properties from database
    # 2. Query available grants based on filters
    # 3. Calculate matching scores for each property-grant pair
    # 4. Save matches to database
    # 5. Generate summary reports
    
    pass

# Export the router
__all__ = ["router"]