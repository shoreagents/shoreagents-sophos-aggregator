#!/usr/bin/env python3
"""
Script to delete data from the database.
Usage: python delete_data.py [events|endpoints] [all|days_older]
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, Endpoint, SIEMEvent

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/sophos_db")

def delete_events(session, all_events=False, days_older=None):
    """Delete SIEM events."""
    if all_events:
        deleted_count = session.query(SIEMEvent).delete()
        print(f"✅ Deleted all {deleted_count} events")
    elif days_older:
        cutoff_date = datetime.utcnow() - timedelta(days=days_older)
        deleted_count = session.query(SIEMEvent).filter(
            SIEMEvent.created_at < cutoff_date
        ).delete()
        print(f"✅ Deleted {deleted_count} events older than {days_older} days")
    else:
        print("❌ Must specify 'all' or 'days_older'")
        return False
    
    session.commit()
    return True

def delete_endpoints(session, all_endpoints=False):
    """Delete endpoints."""
    if all_endpoints:
        deleted_count = session.query(Endpoint).delete()
        print(f"✅ Deleted all {deleted_count} endpoints")
        session.commit()
        return True
    else:
        print("❌ Must specify 'all'")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python delete_data.py [events|endpoints] [all|days_older]")
        print("Examples:")
        print("  python delete_data.py events all")
        print("  python delete_data.py events 7")
        print("  python delete_data.py endpoints all")
        return

    data_type = sys.argv[1].lower()
    action = sys.argv[2].lower()

    # Create database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        if data_type == "events":
            if action == "all":
                delete_events(session, all_events=True)
            elif action.isdigit():
                delete_events(session, days_older=int(action))
            else:
                print("❌ For events, use 'all' or a number of days")
        
        elif data_type == "endpoints":
            if action == "all":
                delete_endpoints(session, all_endpoints=True)
            else:
                print("❌ For endpoints, use 'all'")
        
        else:
            print("❌ Data type must be 'events' or 'endpoints'")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main() 