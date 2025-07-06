from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
import schedule
import threading
import time
from datetime import datetime, timedelta

from .database import get_db, create_tables, Endpoint, SIEMEvent
from .sophos_client import SophosClient

app = FastAPI(title="Sophos Aggregator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client instance
sophos_client = SophosClient()

# Background task scheduler
scheduler_running = False

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and start scheduler on startup."""
    create_tables()
    
    # Auto-start scheduler if enabled via environment variable
    import os
    if os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true":
        global scheduler_running
        if not scheduler_running:
            scheduler_running = True
            schedule_data_fetch()
            
            # Start scheduler in background thread
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Sophos Aggregator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "fetch_endpoints": "/fetch/endpoints",
            "fetch_events": "/fetch/events",
            "get_endpoints": "/data/endpoints",
            "get_events": "/data/events",
            "get_stats": "/data/stats",
            "start_scheduler": "/scheduler/start",
            "stop_scheduler": "/scheduler/stop"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/fetch/endpoints")
async def fetch_endpoints(
    background_tasks: BackgroundTasks,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    """Fetch and store endpoint data from Sophos API."""
    try:
        result = sophos_client.fetch_endpoints(db, page_size)
        return {
            "message": "Endpoint data fetched successfully",
            "result": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fetch/events")
async def fetch_events(
    background_tasks: BackgroundTasks,
    max_events: int = 100000,
    db: Session = Depends(get_db)
):
    """Fetch and store SIEM events from Sophos API."""
    try:
        result = sophos_client.fetch_siem_events(db, max_events)
        return {
            "message": "SIEM events fetched successfully",
            "result": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/data/endpoints")
async def get_endpoints(
    skip: int = 0,
    limit: int = 100,
    online_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get stored endpoint data with pagination."""
    query = db.query(Endpoint)
    
    if online_only:
        query = query.filter(Endpoint.online_status == True)
    
    total = query.count()
    endpoints = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "endpoints": [
            {
                "id": ep.id,
                "endpoint_id": ep.endpoint_id,
                "hostname": ep.hostname,
                "os_name": ep.os_name,
                "endpoint_type": ep.endpoint_type,
                "online_status": ep.online_status,
                "health_status": ep.health_status,
                "group_name": ep.group_name,
                "ip_addresses": ep.ip_addresses,
                "created_at": ep.created_at,
                "updated_at": ep.updated_at
            }
            for ep in endpoints
        ]
    }

@app.get("/data/events")
async def get_events(
    skip: int = 0,
    limit: int = 100,
    severity: str = None,
    event_type: str = None,
    db: Session = Depends(get_db)
):
    """Get stored SIEM events with filtering and pagination."""
    query = db.query(SIEMEvent)
    
    if severity:
        query = query.filter(SIEMEvent.severity == severity)
    if event_type:
        query = query.filter(SIEMEvent.event_type == event_type)
    
    total = query.count()
    events = query.order_by(desc(SIEMEvent.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "events": [
            {
                "id": ev.id,
                "event_id": ev.event_id,
                "endpoint_id": ev.endpoint_id,
                "event_type": ev.event_type,
                "severity": ev.severity,
                "source": ev.source,
                "name": ev.name,
                "location": ev.location,
                "group": ev.group,
                "created_at": ev.created_at,
                "when": ev.when,
                "fetched_at": ev.fetched_at
            }
            for ev in events
        ]
    }

@app.get("/data/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get aggregated statistics."""
    # Endpoint stats
    total_endpoints = db.query(Endpoint).count()
    online_endpoints = db.query(Endpoint).filter(Endpoint.online_status == True).count()
    
    # Event stats
    total_events = db.query(SIEMEvent).count()
    events_by_severity = db.query(
        SIEMEvent.severity,
        func.count(SIEMEvent.id).label('count')
    ).group_by(SIEMEvent.severity).all()
    
    events_by_type = db.query(
        SIEMEvent.event_type,
        func.count(SIEMEvent.id).label('count')
    ).group_by(SIEMEvent.event_type).limit(10).all()
    
    # Recent activity
    recent_events = db.query(SIEMEvent).order_by(desc(SIEMEvent.created_at)).limit(5).all()
    
    return {
        "endpoints": {
            "total": total_endpoints,
            "online": online_endpoints,
            "offline": total_endpoints - online_endpoints
        },
        "events": {
            "total": total_events,
            "by_severity": {item.severity: item.count for item in events_by_severity},
            "by_type": {item.event_type: item.count for item in events_by_type}
        },
        "recent_activity": [
            {
                "event_id": ev.event_id,
                "type": ev.event_type,
                "severity": ev.severity,
                "created_at": ev.created_at
            }
            for ev in recent_events
        ]
    }

def run_scheduler():
    """Background scheduler function."""
    global scheduler_running
    while scheduler_running:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def schedule_data_fetch():
    """Schedule regular data fetching tasks."""
    import os
    print("DEBUG: ENABLE_ENDPOINT_FETCHING =", os.getenv("ENABLE_ENDPOINT_FETCHING"))
    print("DEBUG: ENABLE_SIEM_FETCHING =", os.getenv("ENABLE_SIEM_FETCHING"))
    # Fetch endpoints every 15 minutes (if enabled) for real-time status monitoring
    if os.getenv("ENABLE_ENDPOINT_FETCHING", "true").lower() == "true":
        schedule.every(15).minutes.do(lambda: sophos_client.fetch_endpoints(next(get_db()), 100))
    # Fetch events every 1 hour (if enabled) for better security monitoring
    if os.getenv("ENABLE_SIEM_FETCHING", "true").lower() == "true":
        schedule.every(1).hours.do(lambda: sophos_client.fetch_siem_events(next(get_db()), 100000))

@app.post("/scheduler/start")
async def start_scheduler():
    """Start the background scheduler."""
    global scheduler_running
    if not scheduler_running:
        scheduler_running = True
        schedule_data_fetch()
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        return {
            "message": "Scheduler started successfully",
            "scheduled_tasks": [
                "Fetch endpoints every 15 minutes",
                "Fetch events every 1 hour"
            ]
        }
    else:
        return {"message": "Scheduler is already running"}

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler_running
    scheduler_running = False
    schedule.clear()
    return {"message": "Scheduler stopped successfully"}

@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status."""
    jobs = schedule.get_jobs()
    endpoint_next = None
    siem_next = None
    for job in jobs:
        if "fetch_endpoints" in str(job.job_func):
            endpoint_next = job.next_run
        if "fetch_siem_events" in str(job.job_func):
            siem_next = job.next_run
    return {
        "running": scheduler_running,
        "next_endpoint_run": endpoint_next,
        "next_siem_run": siem_next
    } 