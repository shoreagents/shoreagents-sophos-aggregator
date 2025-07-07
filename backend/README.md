# Sophos Aggregator Backend

A FastAPI-based backend service that aggregates data from Sophos Central API and stores it in PostgreSQL database.

## Features

- **Endpoint Management**: Fetch and store endpoint inventory data
- **SIEM Events**: Collect and store security events
- **RESTful API**: Complete API for data retrieval and management
- **Database Storage**: PostgreSQL integration with SQLAlchemy ORM
- **Docker Support**: Containerized deployment

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Sophos Central API credentials

### Local Development

1. **Clone and setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your Sophos API credentials and database URL
   ```

3. **Run with Docker Compose** (recommended):
   ```bash
   docker-compose up --build
   ```

4. **Or run locally**:
   ```bash
   python run.py
   ```

### Railway Deployment

1. **Create Railway account** and connect your GitHub repository

2. **Add PostgreSQL service** in Railway dashboard

3. **Set environment variables** in Railway:
   - `DATABASE_URL`: Your Railway PostgreSQL URL
   - `SOPHOS_CLIENT_ID`: Your Sophos client ID
   - `SOPHOS_CLIENT_SECRET`: Your Sophos client secret
   - `SOPHOS_TENANT_ID`: Your Sophos tenant ID

4. **Deploy**: Railway will automatically deploy from your GitHub repository

## API Endpoints

### Data Fetching
- `POST /fetch/endpoints` - Fetch endpoint data
- `POST /fetch/events` - Fetch SIEM events


### Data Retrieval
- `GET /data/endpoints` - Get stored endpoints (with pagination)
- `GET /data/events` - Get stored events (with filtering)
- `GET /data/stats` - Get aggregated statistics



### System
- `GET /` - API information
- `GET /health` - Health check

## Automated Data Fetching

For automated data collection, use Railway's built-in cron functionality:

### Railway Cron Setup
1. In Railway dashboard, click "New Service" → Select "Cron"
2. Configure the cron job with your desired command and schedule
3. Set environment variables (DATABASE_URL, SOPHOS_CLIENT_ID, etc.)

### Example Commands

**Fetch Endpoints:**
```bash
cd backend && python -c "from app.sophos_client import SophosClient; from app.database import get_db, create_tables; create_tables(); client = SophosClient(); db = next(get_db()); client.fetch_endpoints(db, 100)"
```

**Fetch Events:**
```bash
cd backend && python -c "from app.sophos_client import SophosClient; from app.database import get_db, create_tables; create_tables(); client = SophosClient(); db = next(get_db()); client.fetch_siem_events(db, 100000)"
```

### Recommended Schedules
- **Endpoints**: Every 15 minutes (`*/15 * * * *`)
- **Events**: Every hour (`0 * * * *`)
- **Full sync**: Every 6 hours (`0 */6 * * *`)

## Database Schema

### Endpoints Table
- `id`: Primary key
- `endpoint_id`: Sophos endpoint ID
- `hostname`: Device hostname
- `os_name`: Operating system
- `endpoint_type`: Device type
- `online_status`: Online/offline status
- `health_status`: Device health
- `group_name`: Group assignment
- `ip_addresses`: IP addresses (JSON)
- `created_at`, `updated_at`: Timestamps

### SIEM Events Table
- `id`: Primary key
- `event_id`: Sophos event ID
- `endpoint_id`: Associated endpoint
- `event_type`: Event type
- `severity`: Event severity
- `source`: Event source
- `name`: Event name
- `location`: Event location
- `group`: Event group
- `created_at`, `when`: Event timestamps
- `raw_data`: Complete event data (JSON)
- `fetched_at`: When data was fetched



## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost/sophos_db` |
| `SOPHOS_CLIENT_ID` | Sophos API client ID | Required |
| `SOPHOS_CLIENT_SECRET` | Sophos API client secret | Required |
| `SOPHOS_TENANT_ID` | Sophos tenant ID | Required |
| `PORT` | Application port | `8000` |
| `ENVIRONMENT` | Environment name | `production` |

  


## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Database Migrations
```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Code Quality
```bash
# Install linting tools
pip install black flake8 isort

# Format code
black .
isort .

# Check code quality
flake8
```

## Deployment

### Railway
1. Connect your GitHub repository to Railway
2. Add PostgreSQL service
3. Set environment variables
4. Deploy automatically

### Docker
```bash
# Build image
docker build -t sophos-aggregator .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e SOPHOS_CLIENT_ID=your_client_id \
  -e SOPHOS_CLIENT_SECRET=your_client_secret \
  -e SOPHOS_TENANT_ID=your_tenant_id \
  sophos-aggregator
```

### Manual Deployment
1. Set up PostgreSQL database
2. Install Python dependencies
3. Set environment variables
4. Run with `python run.py` or `uvicorn app.main:app`

## Monitoring

### Health Checks
- Application health: `GET /health`
- Database connectivity: Built into health check
- API accessibility: Stored in database

### Logging
- Application logs: Standard output
- Database queries: SQLAlchemy logging
- API requests: Request/response logging

## Security

- **Environment Variables**: Sensitive data stored in environment variables
- **Database**: PostgreSQL with proper authentication
- **API**: FastAPI with CORS configuration
- **Docker**: Non-root user in container

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details 