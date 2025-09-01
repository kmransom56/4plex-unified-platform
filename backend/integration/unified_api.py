#!/usr/bin/env python3
"""
Unified API layer for the 4-Plex Investment Platform
Orchestrates communication between discovery and valuation engines
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import httpx
import json

from models.unified_models import (
    UnifiedProperty, DiscoveryJob, AnalysisJob, InvestmentScore,
    PropertyAlert, SystemMetrics, DiscoveryStatus, AnalysisStatus
)

logger = logging.getLogger(__name__)

class UnifiedAPI:
    """
    Unified API that orchestrates between discovery and valuation systems
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Service endpoints (will be configurable)
        self.discovery_endpoint = "http://localhost:11050"
        self.valuation_endpoint = "http://localhost:11060"
        
        # HTTP clients for external services
        self.discovery_client = httpx.AsyncClient(base_url=self.discovery_endpoint)
        self.valuation_client = httpx.AsyncClient(base_url=self.valuation_endpoint)
        
        # Internal state
        self.active_jobs = {}
        self.metrics_cache = {}
        self.last_health_check = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.discovery_client.aclose()
        await self.valuation_client.aclose()

    # Health Check Methods
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for all components"""
        try:
            # Check discovery engine
            discovery_health = await self._check_discovery_health()
            
            # Check valuation engine  
            valuation_health = await self._check_valuation_health()
            
            # Check database
            db_health = await self._check_database_health()
            
            # Overall status
            overall_healthy = all([
                discovery_health.get("healthy", False),
                valuation_health.get("healthy", False),
                db_health.get("healthy", False)
            ])
            
            health_status = {
                "overall": overall_healthy,
                "discovery_engine": discovery_health,
                "valuation_engine": valuation_health,
                "database": db_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.last_health_check = health_status
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "overall": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_discovery_health(self) -> Dict[str, Any]:
        """Check discovery engine health"""
        try:
            response = await self.discovery_client.get("/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "healthy": True,
                    "status": data.get("status", "unknown"),
                    "agents_active": data.get("agents_active", 0),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {"healthy": False, "status_code": response.status_code}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _check_valuation_health(self) -> Dict[str, Any]:
        """Check valuation engine health"""
        try:
            response = await self.valuation_client.get("/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "healthy": True,
                    "status": data.get("status", "unknown"),
                    "jobs_in_queue": data.get("jobs_in_queue", 0),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {"healthy": False, "status_code": response.status_code}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Test database connection
            async with self.db_manager.get_session() as session:
                result = await session.execute("SELECT 1")
                result.fetchone()
                
            return {
                "healthy": True,
                "status": "connected",
                "response_time": 0.1  # Quick connection test
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def get_discovery_health(self) -> Dict[str, Any]:
        """Get discovery engine health"""
        return await self._check_discovery_health()

    async def get_valuation_health(self) -> Dict[str, Any]:
        """Get valuation engine health"""  
        return await self._check_valuation_health()

    # Discovery Engine Integration
    async def start_discovery(self, counties: List[str], filters: Dict[str, Any]) -> DiscoveryJob:
        """Start property discovery across specified counties"""
        try:
            # Create discovery job record
            job = DiscoveryJob(
                counties=counties,
                filters=filters,
                status="starting"
            )
            
            # Store job in database
            async with self.db_manager.get_session() as session:
                await self.db_manager.create_discovery_job(session, job)
            
            # Start discovery agents via external API
            discovery_payload = {
                "counties": counties,
                "filters": filters,
                "job_id": job.id
            }
            
            response = await self.discovery_client.post(
                "/api/discovery/start",
                json=discovery_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                job.status = "started"
                job.agent_count = response.json().get("agent_count", 0)
                
                # Update job status
                async with self.db_manager.get_session() as session:
                    await self.db_manager.update_discovery_job(session, job)
                
                self.active_jobs[job.id] = job
                logger.info(f"Discovery job {job.id} started for counties: {counties}")
                return job
            else:
                job.status = "failed"
                job.error_message = f"Failed to start discovery: {response.status_code}"
                raise Exception(job.error_message)
                
        except Exception as e:
            logger.error(f"Failed to start discovery: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            async with self.db_manager.get_session() as session:
                await self.db_manager.update_discovery_job(session, job)
            raise

    async def get_discovery_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of discovery job"""
        try:
            # Get from cache first
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
            else:
                # Fetch from database
                async with self.db_manager.get_session() as session:
                    job = await self.db_manager.get_discovery_job(session, job_id)
                    if not job:
                        raise ValueError(f"Discovery job {job_id} not found")
            
            # Get real-time status from discovery engine
            response = await self.discovery_client.get(f"/api/discovery/status/{job_id}")
            
            if response.status_code == 200:
                discovery_status = response.json()
                
                # Update job with latest status
                job.status = discovery_status.get("status", job.status)
                job.properties_found = discovery_status.get("properties_found", job.properties_found)
                job.properties_processed = discovery_status.get("properties_processed", job.properties_processed)
                
                if job.status == "completed":
                    job.completed_at = datetime.utcnow()
                
                # Update in database
                async with self.db_manager.get_session() as session:
                    await self.db_manager.update_discovery_job(session, job)
                
                return {
                    "job_id": job.id,
                    "status": job.status,
                    "counties": job.counties,
                    "properties_found": job.properties_found,
                    "properties_processed": job.properties_processed,
                    "agent_count": job.agent_count,
                    "started_at": job.started_at.isoformat(),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "progress_details": discovery_status.get("progress_details", {})
                }
            else:
                raise Exception(f"Failed to get discovery status: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get discovery status for job {job_id}: {str(e)}")
            raise

    async def get_discovery_results(self, job_id: str) -> Dict[str, Any]:
        """Get results from completed discovery job"""
        try:
            # Verify job is completed
            async with self.db_manager.get_session() as session:
                job = await self.db_manager.get_discovery_job(session, job_id)
                if not job:
                    raise ValueError(f"Discovery job {job_id} not found")
                
                if job.status != "completed":
                    raise ValueError(f"Discovery job {job_id} is not completed (status: {job.status})")
            
            # Get results from discovery engine
            response = await self.discovery_client.get(f"/api/discovery/results/{job_id}")
            
            if response.status_code == 200:
                results = response.json()
                
                # Process and store discovered properties
                properties = results.get("properties", [])
                processed_properties = []
                
                for prop_data in properties:
                    # Convert to unified property model
                    unified_prop = await self._convert_discovery_to_unified(prop_data)
                    
                    # Store in database
                    async with self.db_manager.get_session() as session:
                        await self.db_manager.create_or_update_property(session, unified_prop)
                    
                    processed_properties.append(unified_prop.dict())
                
                # Update job with results
                job.results = {
                    "total_properties": len(properties),
                    "processed_properties": len(processed_properties),
                    "summary": results.get("summary", {})
                }
                
                async with self.db_manager.get_session() as session:
                    await self.db_manager.update_discovery_job(session, job)
                
                return {
                    "job_id": job_id,
                    "properties": processed_properties,
                    "total_count": len(processed_properties),
                    "summary": job.results.get("summary", {}),
                    "completed_at": job.completed_at.isoformat()
                }
                
            else:
                raise Exception(f"Failed to get discovery results: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get discovery results for job {job_id}: {str(e)}")
            raise

    async def _convert_discovery_to_unified(self, discovery_data: Dict[str, Any]) -> UnifiedProperty:
        """Convert discovery system data to unified property model"""
        
        return UnifiedProperty(
            source="foreclosure_discovery",
            external_id=discovery_data.get("id"),
            address=discovery_data.get("address", ""),
            city=discovery_data.get("city", ""),
            county=discovery_data.get("county", ""),
            state=discovery_data.get("state", "GA"),
            zip_code=discovery_data.get("zip_code", ""),
            parcel_number=discovery_data.get("parcel_number"),
            
            # Property details
            property_type=discovery_data.get("property_type", "4plex"),
            units=discovery_data.get("units", 4),
            
            # Financial information
            assessed_value=discovery_data.get("assessed_value"),
            amount_owed=discovery_data.get("amount_owed"),
            
            # Foreclosure information
            foreclosure_status=discovery_data.get("foreclosure_status"),
            foreclosure_stage=discovery_data.get("foreclosure_stage"),
            sale_date=discovery_data.get("sale_date"),
            court_case_number=discovery_data.get("court_case_number"),
            
            # Code violations
            has_code_violations=discovery_data.get("has_code_violations", False),
            violation_count=discovery_data.get("violation_count", 0),
            violation_types=discovery_data.get("violation_types", []),
            
            # Status
            discovery_status=DiscoveryStatus.DISCOVERED,
            discovered_at=datetime.utcnow(),
            
            # Raw data for reference
            raw_data=discovery_data
        )

    # Valuation Engine Integration
    async def start_property_analysis(self, property_id: str, options: Dict[str, Any]) -> AnalysisJob:
        """Start comprehensive property analysis"""
        try:
            # Verify property exists
            async with self.db_manager.get_session() as session:
                property_obj = await self.db_manager.get_property(session, property_id)
                if not property_obj:
                    raise ValueError(f"Property {property_id} not found")
            
            # Create analysis job
            job = AnalysisJob(
                property_id=property_id,
                priority=options.get("priority", "normal"),
                status=AnalysisStatus.QUEUED,
                options=options
            )
            
            # Store job in database
            async with self.db_manager.get_session() as session:
                await self.db_manager.create_analysis_job(session, job)
            
            # Submit to valuation engine
            analysis_payload = {
                "property_data": property_obj.dict(),
                "job_id": job.id,
                "options": options
            }
            
            response = await self.valuation_client.post(
                "/api/analyze",
                json=analysis_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                job.status = AnalysisStatus.PROCESSING
                job.started_at = datetime.utcnow()
                
                async with self.db_manager.get_session() as session:
                    await self.db_manager.update_analysis_job(session, job)
                
                logger.info(f"Analysis job {job.id} started for property {property_id}")
                return job
            else:
                job.status = AnalysisStatus.FAILED
                job.error_message = f"Failed to start analysis: {response.status_code}"
                raise Exception(job.error_message)
                
        except Exception as e:
            logger.error(f"Failed to start property analysis: {str(e)}")
            job.status = AnalysisStatus.FAILED
            job.error_message = str(e)
            async with self.db_manager.get_session() as session:
                await self.db_manager.update_analysis_job(session, job)
            raise

    async def get_analysis_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of analysis job"""
        try:
            # Get job from database
            async with self.db_manager.get_session() as session:
                job = await self.db_manager.get_analysis_job(session, job_id)
                if not job:
                    raise ValueError(f"Analysis job {job_id} not found")
            
            # Get real-time status from valuation engine
            response = await self.valuation_client.get(f"/api/status/{job_id}")
            
            if response.status_code == 200:
                valuation_status = response.json()
                
                # Update job with latest status
                job.status = valuation_status.get("status", job.status)
                job.progress = valuation_status.get("progress", job.progress)
                job.current_stage = valuation_status.get("current_stage", job.current_stage)
                
                if job.status == AnalysisStatus.COMPLETED:
                    job.completed_at = datetime.utcnow()
                
                # Update in database
                async with self.db_manager.get_session() as session:
                    await self.db_manager.update_analysis_job(session, job)
                
                return {
                    "job_id": job.id,
                    "property_id": job.property_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "current_stage": job.current_stage,
                    "priority": job.priority.value,
                    "queued_at": job.queued_at.isoformat(),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "estimated_completion": valuation_status.get("estimated_completion")
                }
            else:
                raise Exception(f"Failed to get analysis status: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get analysis status for job {job_id}: {str(e)}")
            raise

    async def get_analysis_results(self, job_id: str) -> Dict[str, Any]:
        """Get results from completed analysis"""
        try:
            # Verify job is completed
            async with self.db_manager.get_session() as session:
                job = await self.db_manager.get_analysis_job(session, job_id)
                if not job:
                    raise ValueError(f"Analysis job {job_id} not found")
                
                if job.status != AnalysisStatus.COMPLETED:
                    raise ValueError(f"Analysis job {job_id} is not completed (status: {job.status})")
            
            # Get results from valuation engine
            response = await self.valuation_client.get(f"/api/results/{job_id}")
            
            if response.status_code == 200:
                results = response.json()
                
                # Update property with analysis results
                async with self.db_manager.get_session() as session:
                    property_obj = await self.db_manager.get_property(session, job.property_id)
                    if property_obj:
                        # Update property with valuation results
                        await self._update_property_with_analysis(property_obj, results)
                        await self.db_manager.update_property(session, property_obj)
                
                # Store results in job
                job.results = results
                async with self.db_manager.get_session() as session:
                    await self.db_manager.update_analysis_job(session, job)
                
                return {
                    "job_id": job_id,
                    "property_id": job.property_id,
                    "analysis_results": results,
                    "completed_at": job.completed_at.isoformat()
                }
                
            else:
                raise Exception(f"Failed to get analysis results: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get analysis results for job {job_id}: {str(e)}")
            raise

    async def _update_property_with_analysis(self, property_obj: UnifiedProperty, results: Dict[str, Any]):
        """Update property object with analysis results"""
        
        # Financial metrics
        if "financial_analysis" in results:
            financial = results["financial_analysis"]
            property_obj.cap_rate = financial.get("cap_rate")
            property_obj.noi = financial.get("noi")
            property_obj.gross_income = financial.get("gross_income")
            property_obj.operating_expenses = financial.get("operating_expenses")
            property_obj.cash_flow = financial.get("cash_flow")
        
        # Investment scoring
        if "investment_score" in results:
            property_obj.investment_score = results["investment_score"]
        
        if "viability_score" in results:
            property_obj.viability_score = results["viability_score"]
        
        if "risk_level" in results:
            property_obj.risk_level = results["risk_level"]
        
        # Market value
        if "market_value" in results:
            property_obj.market_value = results["market_value"]
        
        # Update status and timestamp
        property_obj.valuation_status = AnalysisStatus.COMPLETED
        property_obj.analyzed_at = datetime.utcnow()
        property_obj.analysis_data = results

    # Property Management
    async def get_properties(self, limit: int = 50, offset: int = 0, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get paginated list of properties with filtering"""
        try:
            async with self.db_manager.get_session() as session:
                properties = await self.db_manager.get_properties(session, limit, offset, filters)
                return [prop.dict() for prop in properties]
        except Exception as e:
            logger.error(f"Failed to get properties: {str(e)}")
            raise

    async def get_property_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for specific property"""
        try:
            async with self.db_manager.get_session() as session:
                property_obj = await self.db_manager.get_property(session, property_id)
                return property_obj.dict() if property_obj else None
        except Exception as e:
            logger.error(f"Failed to get property details for {property_id}: {str(e)}")
            raise

    async def get_investment_opportunities(self, limit: int = 25, min_score: int = 70) -> List[Dict[str, Any]]:
        """Get top investment opportunities"""
        try:
            filters = {
                "min_investment_score": min_score,
                "valuation_status": "completed"
            }
            
            async with self.db_manager.get_session() as session:
                opportunities = await self.db_manager.get_properties(
                    session, limit, 0, filters, order_by="investment_score DESC"
                )
                return [opp.dict() for opp in opportunities]
        except Exception as e:
            logger.error(f"Failed to get investment opportunities: {str(e)}")
            raise

    async def get_opportunity_alerts(self) -> List[Dict[str, Any]]:
        """Get high-priority opportunity alerts"""
        try:
            async with self.db_manager.get_session() as session:
                alerts = await self.db_manager.get_active_alerts(session)
                return [alert.dict() for alert in alerts]
        except Exception as e:
            logger.error(f"Failed to get opportunity alerts: {str(e)}")
            raise

    # Analytics and Metrics
    async def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics"""
        try:
            async with self.db_manager.get_session() as session:
                # Get various metrics
                total_properties = await self.db_manager.count_properties(session)
                properties_today = await self.db_manager.count_properties_discovered_today(session)
                analyses_completed = await self.db_manager.count_analyses_completed_today(session)
                high_priority_ops = await self.db_manager.count_high_priority_opportunities(session)
                
                # Get county breakdown
                county_breakdown = await self.db_manager.get_properties_by_county(session)
                
                # Get status breakdown
                status_breakdown = await self.db_manager.get_properties_by_status(session)
                
                return {
                    "summary": {
                        "total_properties": total_properties,
                        "properties_discovered_today": properties_today,
                        "analyses_completed_today": analyses_completed,
                        "high_priority_opportunities": high_priority_ops
                    },
                    "county_breakdown": county_breakdown,
                    "status_breakdown": status_breakdown,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get dashboard analytics: {str(e)}")
            raise

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get platform performance metrics"""
        try:
            # Get health status if not cached
            if not self.last_health_check or (datetime.utcnow() - datetime.fromisoformat(self.last_health_check["timestamp"].replace("Z", "+00:00"))) > timedelta(minutes=5):
                await self.get_health_status()
            
            async with self.db_manager.get_session() as session:
                metrics = await self.db_manager.get_system_metrics(session)
                
            return {
                "health_status": self.last_health_check,
                "performance_metrics": metrics.dict() if metrics else {},
                "active_jobs": len(self.active_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            raise

    async def get_county_analytics(self) -> Dict[str, Any]:
        """Get county-specific analytics"""
        try:
            async with self.db_manager.get_session() as session:
                county_stats = await self.db_manager.get_county_analytics(session)
                
            return {
                "counties": county_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get county analytics: {str(e)}")
            raise

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            # Combine multiple metric sources
            dashboard_analytics = await self.get_dashboard_analytics()
            performance_metrics = await self.get_performance_metrics()
            county_analytics = await self.get_county_analytics()
            
            return {
                "dashboard": dashboard_analytics,
                "performance": performance_metrics,
                "counties": county_analytics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            raise