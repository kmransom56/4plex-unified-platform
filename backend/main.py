#!/usr/bin/env python3
"""
4-Plex Unified Investment Platform - Main Application
Combines foreclosure discovery with professional investment analysis
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import os
import sys

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

# Unified imports (will be created)
from integration.unified_api import UnifiedAPI
from integration.workflow_orchestrator import WorkflowOrchestrator
from integration.data_synchronizer import DataSynchronizer
from models.unified_models import (
    UnifiedProperty, 
    DiscoveryStatus, 
    AnalysisStatus,
    InvestmentScore
)
from common.config import get_settings
from common.logging_config import setup_logging
from common.database import get_database_manager

# Configuration
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="4-Plex Unified Investment Platform",
    description="AI-powered property discovery and investment analysis platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
unified_api: Optional[UnifiedAPI] = None
workflow_orchestrator: Optional[WorkflowOrchestrator] = None
data_synchronizer: Optional[DataSynchronizer] = None

# Pydantic models for API endpoints
class DiscoveryStartRequest(BaseModel):
    counties: List[str] = Field(default=["Fulton", "DeKalb", "Clayton", "Cobb", "Atlanta"])
    property_types: List[str] = Field(default=["4plex"])
    max_price: Optional[float] = Field(default=500000)
    min_cap_rate: Optional[float] = Field(default=8.0)

class AnalysisRequest(BaseModel):
    property_id: str
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    include_market_analysis: bool = Field(default=True)
    include_risk_assessment: bool = Field(default=True)

class InvestmentFilter(BaseModel):
    min_score: Optional[int] = Field(default=60, ge=0, le=100)
    max_price: Optional[float] = Field(default=500000)
    counties: Optional[List[str]] = None
    foreclosure_types: Optional[List[str]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the unified platform on startup"""
    global unified_api, workflow_orchestrator, data_synchronizer
    
    logger.info("🚀 Starting 4-Plex Unified Investment Platform...")
    
    try:
        # Initialize database connections
        db_manager = await get_database_manager()
        
        # Initialize core components
        unified_api = UnifiedAPI(db_manager)
        workflow_orchestrator = WorkflowOrchestrator(unified_api)
        data_synchronizer = DataSynchronizer(db_manager)
        
        # Start background services
        asyncio.create_task(workflow_orchestrator.start())
        asyncio.create_task(data_synchronizer.start())
        
        logger.info("✅ Platform initialization completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Platform initialization failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of platform services"""
    logger.info("🛑 Shutting down 4-Plex Unified Platform...")
    
    if workflow_orchestrator:
        await workflow_orchestrator.stop()
    if data_synchronizer:
        await data_synchronizer.stop()
    
    logger.info("✅ Platform shutdown completed")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Comprehensive health check for all platform components"""
    try:
        health_status = await unified_api.get_health_status()
        return JSONResponse(content={
            "status": "healthy" if health_status.get("overall", False) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": health_status,
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/health/discovery")
async def discovery_health():
    """Health check specifically for discovery engine"""
    try:
        status = await unified_api.get_discovery_health()
        return JSONResponse(content=status)
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": str(e)})

@app.get("/health/valuation")
async def valuation_health():
    """Health check specifically for valuation engine"""
    try:
        status = await unified_api.get_valuation_health()
        return JSONResponse(content=status)
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": str(e)})

# Discovery Engine Endpoints
@app.post("/api/discovery/start")
async def start_discovery(
    request: DiscoveryStartRequest,
    background_tasks: BackgroundTasks
):
    """Start property discovery across specified counties"""
    try:
        discovery_job = await unified_api.start_discovery(
            counties=request.counties,
            filters={
                "property_types": request.property_types,
                "max_price": request.max_price,
                "min_cap_rate": request.min_cap_rate
            }
        )
        
        # Queue background processing
        background_tasks.add_task(
            workflow_orchestrator.process_discovery_results,
            discovery_job.id
        )
        
        return JSONResponse(content={
            "job_id": discovery_job.id,
            "status": "started",
            "counties": request.counties,
            "estimated_duration": "30-60 minutes",
            "message": "Discovery agents have been deployed"
        })
        
    except Exception as e:
        logger.error(f"Failed to start discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discovery/status/{job_id}")
async def get_discovery_status(job_id: str):
    """Get status of discovery job"""
    try:
        status = await unified_api.get_discovery_status(job_id)
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")

@app.get("/api/discovery/results/{job_id}")
async def get_discovery_results(job_id: str):
    """Get results from completed discovery job"""
    try:
        results = await unified_api.get_discovery_results(job_id)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Valuation Engine Endpoints
@app.post("/api/valuation/analyze")
async def analyze_property(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start comprehensive property analysis"""
    try:
        analysis_job = await unified_api.start_property_analysis(
            property_id=request.property_id,
            options={
                "priority": request.priority,
                "include_market_analysis": request.include_market_analysis,
                "include_risk_assessment": request.include_risk_assessment
            }
        )
        
        # Queue background processing
        background_tasks.add_task(
            workflow_orchestrator.process_analysis_job,
            analysis_job.id
        )
        
        return JSONResponse(content={
            "job_id": analysis_job.id,
            "property_id": request.property_id,
            "status": "queued",
            "priority": request.priority,
            "estimated_duration": "10-30 minutes"
        })
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/valuation/status/{job_id}")
async def get_analysis_status(job_id: str):
    """Get status of valuation analysis job"""
    try:
        status = await unified_api.get_analysis_status(job_id)
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/valuation/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Get results from completed analysis"""
    try:
        results = await unified_api.get_analysis_results(job_id)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Unified Property Management Endpoints
@app.get("/api/properties")
async def get_properties(
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    county: Optional[str] = Query(default=None),
    min_score: Optional[int] = Query(default=None, ge=0, le=100),
    status: Optional[str] = Query(default=None)
):
    """Get paginated list of properties with filtering"""
    try:
        filters = {}
        if county:
            filters["county"] = county
        if min_score:
            filters["min_investment_score"] = min_score
        if status:
            filters["discovery_status"] = status
            
        properties = await unified_api.get_properties(
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        return JSONResponse(content={
            "properties": properties,
            "total": len(properties),
            "offset": offset,
            "limit": limit
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/{property_id}")
async def get_property_details(property_id: str):
    """Get detailed information for a specific property"""
    try:
        property_details = await unified_api.get_property_details(property_id)
        if not property_details:
            raise HTTPException(status_code=404, detail="Property not found")
        return JSONResponse(content=property_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/properties/{property_id}/analyze")
async def queue_property_analysis(
    property_id: str,
    background_tasks: BackgroundTasks,
    priority: str = "normal"
):
    """Queue a property for analysis"""
    try:
        analysis_request = AnalysisRequest(
            property_id=property_id,
            priority=priority
        )
        
        return await analyze_property(analysis_request, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Investment Opportunities Endpoints
@app.get("/api/opportunities")
async def get_investment_opportunities(
    limit: int = Query(default=25, le=100),
    min_score: int = Query(default=70, ge=0, le=100)
):
    """Get top investment opportunities"""
    try:
        opportunities = await unified_api.get_investment_opportunities(
            limit=limit,
            min_score=min_score
        )
        
        return JSONResponse(content={
            "opportunities": opportunities,
            "total": len(opportunities),
            "criteria": {
                "min_score": min_score,
                "limit": limit
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/alerts")
async def get_opportunity_alerts():
    """Get high-priority opportunity alerts"""
    try:
        alerts = await unified_api.get_opportunity_alerts()
        return JSONResponse(content={"alerts": alerts})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Reporting Endpoints
@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        analytics = await unified_api.get_dashboard_analytics()
        return JSONResponse(content=analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance")
async def get_performance_metrics():
    """Get platform performance metrics"""
    try:
        metrics = await unified_api.get_performance_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/counties")
async def get_county_analytics():
    """Get county-specific analytics"""
    try:
        county_data = await unified_api.get_county_analytics()
        return JSONResponse(content=county_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Management Endpoints
@app.post("/api/system/sync")
async def trigger_data_sync():
    """Trigger manual data synchronization between systems"""
    try:
        sync_job = await data_synchronizer.trigger_full_sync()
        return JSONResponse(content={
            "sync_job_id": sync_job.id,
            "status": "started",
            "message": "Data synchronization initiated"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        metrics = await unified_api.get_system_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve main dashboard HTML"""
    dashboard_html = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if dashboard_html.exists():
        return HTMLResponse(content=dashboard_html.read_text())
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>4-Plex Unified Platform</title></head>
            <body>
                <h1>4-Plex Unified Investment Platform</h1>
                <p>Dashboard is being built...</p>
                <p><a href="/api/docs">View API Documentation</a></p>
            </body>
        </html>
        """)

if __name__ == "__main__":
    logger.info("🏠 Starting 4-Plex Unified Investment Platform...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=11070,
        reload=True,
        log_level="info",
        access_log=True
    )