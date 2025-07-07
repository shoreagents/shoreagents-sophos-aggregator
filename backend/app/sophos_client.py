import requests
import json
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .database import Endpoint, SIEMEvent
import os

class SophosClient:
    def __init__(self):
        self.client_id = os.getenv("SOPHOS_CLIENT_ID", "")
        self.client_secret = os.getenv("SOPHOS_CLIENT_SECRET", "")
        self.tenant_id = os.getenv("SOPHOS_TENANT_ID", "")
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
        
        # Cap page_size at 500 for Sophos API
        page_size = min(page_size, 500)
        
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
            # Debug: Print first few endpoints to see available fields
            if not hasattr(self, '_debug_printed'):
                print(f"🔍 DEBUG: Sample endpoint data from Sophos API:")
                print(f"Available fields: {list(endpoint_data.keys())}")
                print(f"Full data sample: {endpoint_data}")
                self._debug_printed = True
            
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
                existing.ip_addresses = endpoint_data.get('ipv4Addresses', [])
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
                    ip_addresses=endpoint_data.get('ipv4Addresses', [])
                )
                db.add(new_endpoint)
            
            db.commit()
            
        except Exception as e:
            print(f"❌ Error storing endpoint: {e}")
            db.rollback()

    def _get_last_siem_event_timestamp(self):
        """Read the last SIEM event timestamp from file."""
        try:
            with open("last_siem_event_timestamp.txt", "r") as f:
                return f.read().strip()
        except Exception:
            return None

    def _set_last_siem_event_timestamp(self, timestamp):
        """Write the last SIEM event timestamp to file."""
        try:
            with open("last_siem_event_timestamp.txt", "w") as f:
                f.write(timestamp)
        except Exception as e:
            print(f"❌ Error writing last SIEM event timestamp: {e}")

    def fetch_siem_events(self, db: Session, max_events: int = 10000) -> Dict[str, Any]:
        """Fetch SIEM events and store in database, using 'since' polling with a 5-minute overlap. Limit to 5000 events on first run."""
        if not self.access_token:
            self.get_access_token()
            
        url = "https://api-us01.central.sophos.com/siem/v1/events"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Accept": "application/json"
        }
        
        params = {
            "limit": 200
        }
        
        last_timestamp = self._get_last_siem_event_timestamp()
        first_run = False
        if last_timestamp:
            try:
                from datetime import datetime, timedelta
                last_dt = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                buffered_dt = last_dt - timedelta(minutes=5)
                params["since"] = buffered_dt.isoformat().replace('+00:00', 'Z')
            except Exception as e:
                print(f"❌ Error parsing last timestamp for buffer: {e}")
                params["since"] = last_timestamp
        else:
            # First run: limit to 5000 events
            first_run = True
            max_events = 5000

        all_events = []
        latest_event_timestamp = last_timestamp

        try:
            while len(all_events) < max_events:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    events = data.get('items', [])
                    if not events:
                        break
                    for event_data in events:
                        if len(all_events) < max_events:
                            self._store_siem_event(db, event_data)
                            all_events.append(event_data)
                            event_ts = event_data.get('created_at') or event_data.get('when')
                            if event_ts and (not latest_event_timestamp or event_ts > latest_event_timestamp):
                                latest_event_timestamp = event_ts
                    pages_info = data.get('pages', {})
                    if not pages_info.get('nextKey'):
                        break
                    params['pageFromKey'] = pages_info['nextKey']
                    params['limit'] = min(max_events - len(all_events), 200)
                    time.sleep(0.1)
                else:
                    print(f"❌ Error: {response.status_code}")
                    break
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
        
        # Save the latest event timestamp for next polling
        if latest_event_timestamp:
            self._set_last_siem_event_timestamp(latest_event_timestamp)
        
        return {
            "success": True,
            "total_events": len(all_events),
            "latest_event_timestamp": latest_event_timestamp
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

 