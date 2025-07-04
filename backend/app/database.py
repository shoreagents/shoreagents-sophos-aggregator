from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/sophos_db")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class Endpoint(Base):
    __tablename__ = "endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(String, unique=True, index=True)
    hostname = Column(String)
    os_name = Column(String)
    endpoint_type = Column(String)
    online_status = Column(Boolean)
    health_status = Column(String)
    group_name = Column(String)
    ip_addresses = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SIEMEvent(Base):
    __tablename__ = "siem_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    endpoint_id = Column(String, index=True)
    event_type = Column(String)
    severity = Column(String)
    source = Column(String)
    name = Column(Text)
    location = Column(String)
    group = Column(String)
    created_at = Column(DateTime)
    when = Column(DateTime)
    raw_data = Column(JSON)
    fetched_at = Column(DateTime, default=datetime.utcnow)

class EndpointEvent(Base):
    __tablename__ = "endpoint_events"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_name = Column(String, index=True)
    endpoint_id = Column(String, index=True)
    events_count = Column(Integer)
    latest_event_time = Column(DateTime)
    most_common_type = Column(String)
    events_data = Column(JSON)
    fetched_at = Column(DateTime, default=datetime.utcnow)



# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 