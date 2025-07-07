# Railway Cron Setup

This guide explains how to set up automated data fetching using Railway's built-in cron functionality.

## Quick Setup

### 1. Add Cron Service
1. In your Railway dashboard, click "New Service"
2. Select "Cron" as the service type
3. Configure the cron job

### 2. Configure Cron Job

**Command:**
```bash
cd backend && python -c "from app.sophos_client import SophosClient; from app.database import get_db, create_tables; create_tables(); client = SophosClient(); db = next(get_db()); client.fetch_endpoints(db, 100)"
```

**Schedule:**
```bash
*/15 * * * *  # Every 15 minutes
```

### 3. Set Environment Variables
Make sure these are set in your cron service:
- `DATABASE_URL`
- `SOPHOS_CLIENT_ID`
- `SOPHOS_CLIENT_SECRET`
- `SOPHOS_TENANT_ID`

## Multiple Cron Jobs

Create separate cron services for different schedules:

### Endpoints (Every 15 minutes)
- **Command:** `cd backend && python -c "from app.sophos_client import SophosClient; from app.database import get_db, create_tables; create_tables(); client = SophosClient(); db = next(get_db()); client.fetch_endpoints(db, 100)"`
- **Schedule:** `*/15 * * * *`

### Events (Every hour)
- **Command:** `cd backend && python -c "from app.sophos_client import SophosClient; from app.database import get_db, create_tables; create_tables(); client = SophosClient(); db = next(get_db()); client.fetch_siem_events(db, 100000)"`
- **Schedule:** `0 * * * *`

### Full Sync (Every 6 hours)
- **Command:** `cd backend && python -c "from app.sophos_client import SophosClient; from app.database import get_db, create_tables; create_tables(); client = SophosClient(); db = next(get_db()); client.fetch_endpoints(db, 100); client.fetch_siem_events(db, 100000)"`
- **Schedule:** `0 */6 * * *`

## Monitoring

- Check Railway dashboard for job execution status
- View logs for each cron service
- Monitor success/failure rates

## Benefits

- **Native integration** with Railway
- **Automatic scheduling** and execution
- **Built-in monitoring** and logging
- **Cost-effective** - only pay for execution time
- **Reliable** - Railway's infrastructure ensures jobs run 