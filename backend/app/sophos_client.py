import requests
import json
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .database import Endpoint, SIEMEvent, EndpointEvent
import os

class SophosClient:
    def __init__(self):
        self.client_id = os.getenv("SOPHOS_CLIENT_ID", "ab896b4f-0ff5-4fa9-9f8f-debce01cbcb5")
        self.client_secret = os.getenv("SOPHOS_CLIENT_SECRET", "680ab56f596036e8947561151e1284b617331a6a6880e6e3d9c80bd3de59b0a20b85aad1e201f510ce335a3222de04d4f543")
        self.tenant_id = os.getenv("SOPHOS_TENANT_ID", "7b6f33dc-7e03-4d71-9729-689e43882c47")
        self.access_token = None
        
    def get_access_token(self):
        """Get access token from Sophos API."""
        token_url = "https://id.sophos.com/api/v2/oauth2/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "token"
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            return self.access_token
        except Exception as e:
            print(f"❌ Error getting access token: {e}")
            return None

    def fetch_endpoints(self, db: Session, page_size: int = 100) -> Dict[str, Any]:
        """Fetch all endpoints and store in database."""
        if not self.access_token:
            self.get_access_token()
            
        base_url = "https://api-us01.central.sophos.com/endpoint/v1/endpoints"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Accept": "application/json"
        }
        
        all_endpoints = []
        page_count = 0
        
        try:
            while True:
                page_count += 1
                
                params = {
                    "pageSize": page_size
                }
                
                if page_count > 1 and hasattr(self, 'next_key'):
                    params['pageFromKey'] = self.next_key
                
                response = requests.get(base_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    endpoints = data.get('items', [])
                    
                    if not endpoints:
                        break
                    
                    all_endpoints.extend(endpoints)
                    
                    # Store endpoints in database
                    for endpoint_data in endpoints:
                        self._store_endpoint(db, endpoint_data)
                    
                    pages_info = data.get('pages', {})
                    if not pages_info.get('nextKey'):
                        break
                    
                    self.next_key = pages_info['nextKey']
                    time.sleep(0.1)
                    
                else:
                    print(f"❌ Error: {response.status_code}")
                    break
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "total_endpoints": len(all_endpoints),
            "pages_processed": page_count
        }

    def _store_endpoint(self, db: Session, endpoint_data: Dict[str, Any]):
        """Store endpoint data in database."""
        try:
            # Check if endpoint already exists
            existing = db.query(Endpoint).filter(Endpoint.endpoint_id == endpoint_data.get('id')).first()
            
            if existing:
                # Update existing endpoint
                existing.hostname = endpoint_data.get('hostname')
                existing.os_name = endpoint_data.get('os', {}).get('name')
                existing.endpoint_type = endpoint_data.get('type')
                existing.online_status = endpoint_data.get('online', False)
                existing.health_status = endpoint_data.get('health', {}).get('overall')
                existing.group_name = endpoint_data.get('group', {}).get('name')
                existing.ip_addresses = endpoint_data.get('ipAddresses', [])
                existing.updated_at = datetime.utcnow()
            else:
                # Create new endpoint
                new_endpoint = Endpoint(
                    endpoint_id=endpoint_data.get('id'),
                    hostname=endpoint_data.get('hostname'),
                    os_name=endpoint_data.get('os', {}).get('name'),
                    endpoint_type=endpoint_data.get('type'),
                    online_status=endpoint_data.get('online', False),
                    health_status=endpoint_data.get('health', {}).get('overall'),
                    group_name=endpoint_data.get('group', {}).get('name'),
                    ip_addresses=endpoint_data.get('ipAddresses', [])
                )
                db.add(new_endpoint)
            
            db.commit()
            
        except Exception as e:
            print(f"❌ Error storing endpoint: {e}")
            db.rollback()

    def fetch_siem_events(self, db: Session, max_events: int = 100000) -> Dict[str, Any]:
        """Fetch SIEM events and store in database."""
        if not self.access_token:
            self.get_access_token()
            
        url = "https://api-us01.central.sophos.com/siem/v1/events"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Accept": "application/json"
        }
        
        # No time range limit - fetch all events
        params = {
            "pageSize": min(max_events, 500)
        }
        
        all_events = []
        
        try:
            while len(all_events) < max_events:
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    events = data.get('items', [])
                    
                    if not events:
                        break
                    
                    # Store events in database
                    for event_data in events:
                        if len(all_events) < max_events:
                            self._store_siem_event(db, event_data)
                            all_events.append(event_data)
                    
                    # Check for next page
                    pages_info = data.get('pages', {})
                    if not pages_info.get('nextKey'):
                        break
                    
                    params['pageFromKey'] = pages_info['nextKey']
                    time.sleep(0.1)
                    
                else:
                    print(f"❌ Error: {response.status_code}")
                    break
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "total_events": len(all_events)
        }

    def _store_siem_event(self, db: Session, event_data: Dict[str, Any]):
        """Store SIEM event data in database."""
        try:
            # Check if event already exists
            existing = db.query(SIEMEvent).filter(SIEMEvent.event_id == event_data.get('id')).first()
            
            if not existing:
                # Create new event
                new_event = SIEMEvent(
                    event_id=event_data.get('id'),
                    endpoint_id=event_data.get('endpoint_id'),
                    event_type=event_data.get('type'),
                    severity=event_data.get('severity'),
                    source=event_data.get('source'),
                    name=event_data.get('name'),
                    location=event_data.get('location'),
                    group=event_data.get('group'),
                    created_at=datetime.fromisoformat(event_data.get('created_at', '').replace('Z', '+00:00')) if event_data.get('created_at') else None,
                    when=datetime.fromisoformat(event_data.get('when', '').replace('Z', '+00:00')) if event_data.get('when') else None,
                    raw_data=event_data
                )
                db.add(new_event)
                db.commit()
                
        except Exception as e:
            print(f"❌ Error storing SIEM event: {e}")
            db.rollback()

 