import requests
import json
from datetime import datetime, timedelta
import time

def get_access_token(client_id, client_secret):
    """Get access token from Sophos API."""
    token_url = "https://id.sophos.com/api/v2/oauth2/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "token"
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def get_siem_events(access_token, tenant_id, event_type=None, days_back=7, page_size=200):
    """Get SIEM events with optional filtering."""
    base_url = "https://api-us01.central.sophos.com/siem/v1/events"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Tenant-ID": tenant_id
    }
    
    # Calculate date range (use UTC)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        "pageSize": page_size,
        "from": start_date.isoformat() + "Z",
        "to": end_date.isoformat() + "Z"
    }
    
    if event_type:
        params["eventType"] = event_type
    
    all_events = []
    has_more = True
    
    print(f"📡 Fetching SIEM events from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    if event_type:
        print(f"   Filter: {event_type}")
    
    while has_more:
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            events = data.get("items", [])
            all_events.extend(events)
            
            print(f"   ✅ Retrieved {len(events)} events (Total: {len(all_events)})")
            
            has_more = data.get("has_more", False)
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error fetching events: {e}")
            break
    
    return all_events

def analyze_events(events):
    """Analyze events and provide statistics."""
    if not events:
        print("❌ No events to analyze")
        return
    
    print(f"\n📊 SIEM EVENTS ANALYSIS")
    print("=" * 60)
    print(f"Total Events: {len(events)}")
    
    # Event type analysis
    event_types = {}
    severity_counts = {}
    endpoint_counts = {}
    user_counts = {}
    group_counts = {}
    
    for event in events:
        # Event type
        event_type = event.get("type", "Unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Severity
        severity = event.get("severity", "Unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Endpoint
        endpoint_id = event.get("endpoint_id", "Unknown")
        endpoint_counts[endpoint_id] = endpoint_counts.get(endpoint_id, 0) + 1
        
        # User
        user_id = event.get("user_id", "Unknown")
        user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        # Group
        group = event.get("group", "Unknown")
        group_counts[group] = group_counts.get(group, 0) + 1
    
    # Display statistics
    print(f"\n🔍 Event Types:")
    for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   {event_type}: {count}")
    
    print(f"\n⚠️  Severity Levels:")
    for severity, count in sorted(severity_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {severity}: {count}")
    
    print(f"\n🖥️  Top Endpoints (by event count):")
    for endpoint_id, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {endpoint_id}: {count} events")
    
    print(f"\n👥 Top Users (by event count):")
    for user_id, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {user_id}: {count} events")
    
    print(f"\n📂 Event Groups:")
    for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {group}: {count}")

def display_recent_events(events, limit=20):
    """Display recent events in a formatted table."""
    if not events:
        print("❌ No events to display")
        return
    
    print(f"\n📋 RECENT SIEM EVENTS (Last {limit})")
    print("=" * 120)
    print(f"{'Time':<20} {'Type':<35} {'Severity':<8} {'Source':<25} {'Name':<30}")
    print("=" * 120)
    
    # Sort by creation time (newest first)
    sorted_events = sorted(events, key=lambda x: x.get("created_at", ""), reverse=True)
    
    for event in sorted_events[:limit]:
        created_at = event.get("created_at", "")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = created_at[:19]
        else:
            time_str = "Unknown"
        
        event_type = event.get("type", "Unknown")
        severity = event.get("severity", "Unknown")
        source = event.get("source", "Unknown")
        name = event.get("name", "Unknown")
        
        # Truncate long strings
        event_type = event_type[:34] + "..." if len(event_type) > 34 else event_type
        source = source[:24] + "..." if len(source) > 24 else source
        name = name[:29] + "..." if len(name) > 29 else name
        
        print(f"{time_str:<20} {event_type:<35} {severity:<8} {source:<25} {name:<30}")
    
    print("=" * 120)

def get_events_by_type(access_token, tenant_id, event_types=None):
    """Get events filtered by specific types."""
    if not event_types:
        event_types = ["threat", "malware", "firewall", "dlp", "web", "device", "user", "system"]
    
    print(f"\n🔍 Fetching Events by Type")
    print("=" * 60)
    
    all_events_by_type = {}
    
    for event_type in event_types:
        print(f"📡 Fetching {event_type} events...")
        events = get_siem_events(access_token, tenant_id, event_type=event_type, days_back=7)
        all_events_by_type[event_type] = events
        print(f"   ✅ Retrieved {len(events)} {event_type} events")
    
    return all_events_by_type

def export_events_to_json(events, filename="sophos_siem_events.json"):
    """Export events to JSON file."""
    try:
        # Ensure data folder exists
        import os
        os.makedirs("data", exist_ok=True)
        
        # Save to data folder
        filepath = os.path.join("data", filename)
        with open(filepath, 'w') as f:
            json.dump(events, f, indent=2)
        print(f"✅ Events exported to {filepath}")
    except Exception as e:
        print(f"❌ Error exporting events: {e}")

def export_events_by_type_to_json(events_by_type, filename="sophos_siem_events_by_type.json"):
    """Export events grouped by type to JSON file."""
    try:
        # Ensure data folder exists
        import os
        os.makedirs("data", exist_ok=True)
        
        # Save to data folder
        filepath = os.path.join("data", filename)
        with open(filepath, 'w') as f:
            json.dump(events_by_type, f, indent=2)
        print(f"✅ Events by type exported to {filepath}")
    except Exception as e:
        print(f"❌ Error exporting events by type: {e}")

def main():
    # Your credentials and tenant ID
    CLIENT_ID = "ab896b4f-0ff5-4fa9-9f8f-debce01cbcb5"
    CLIENT_SECRET = "680ab56f596036e8947561151e1284b617331a6a6880e6e3d9c80bd3de59b0a20b85aad1e201f510ce335a3222de04d4f543"
    TENANT_ID = "7b6f33dc-7e03-4d71-9729-689e43882c47"
    
    print("🔍 Sophos Central SIEM Events Retrieval")
    print("=" * 60)
    
    # Get access token
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    if not access_token:
        print("❌ Failed to get access token")
        return
    
    print("✅ Access token obtained successfully")
    
    # Get all SIEM events (last 7 days)
    print(f"\n📡 Fetching all SIEM events...")
    all_events = get_siem_events(access_token, TENANT_ID, days_back=7, page_size=200)
    
    if all_events:
        # Analyze events
        analyze_events(all_events)
        
        # Display recent events
        display_recent_events(all_events, limit=20)
        
        # Export all events
        export_events_to_json(all_events)
        
        # Get events by type
        events_by_type = get_events_by_type(access_token, TENANT_ID)
        export_events_by_type_to_json(events_by_type)
        
        print(f"\n🎉 SIEM Events retrieval completed!")
        print(f"   Total events retrieved: {len(all_events)}")
        print(f"   Time range: Last 7 days")
        print(f"   Files created: data/sophos_siem_events.json, data/sophos_siem_events_by_type.json")
    else:
        print("❌ No SIEM events found")

if __name__ == "__main__":
    main() 