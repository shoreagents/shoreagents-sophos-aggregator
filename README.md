# Sophos Central API Integration

A comprehensive backend system for aggregating and analyzing Sophos Central security data with PostgreSQL storage and Railway deployment.

## 🚀 Quick Start

### Backend Deployment (Railway)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd sophos
   ```

2. **Set up Railway**:
   - Create account at [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Add PostgreSQL service in Railway dashboard

3. **Configure Environment Variables** in Railway:
   ```
   DATABASE_URL=your_railway_postgresql_url
   SOPHOS_CLIENT_ID=your_sophos_client_id
   SOPHOS_CLIENT_SECRET=your_sophos_client_secret
   SOPHOS_TENANT_ID=your_sophos_tenant_id
   ```

4. **Deploy**: Railway will automatically deploy from your GitHub repository

### Local Development

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

3. **Initialize database**:
   ```bash
   python scripts/init_db.py
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

## 📁 Project Structure

```
sophos/
├── backend/                 # FastAPI backend application
│   ├── app/                # Application code
│   │   ├── database.py     # Database models and configuration
│   │   ├── sophos_client.py # Sophos API client
│   │   └── main.py         # FastAPI application
│   ├── scripts/            # Utility scripts
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Container configuration
│   ├── docker-compose.yml  # Local development setup
│   └── railway.json        # Railway deployment config
├── data/                   # Data exports
├── docs/                   # Documentation
└── *.py                    # Original Python scripts
```

## 🔧 Backend Features

### Core Functionality
- **Endpoint Management**: Fetch and store endpoint inventory
- **SIEM Events**: Collect and analyze security events


- **RESTful API**: Complete data access endpoints

### Database Schema
- **Endpoints**: Device inventory and status
- **SIEM Events**: Security event data with metadata


### API Endpoints

#### Data Fetching
- `POST /fetch/endpoints` - Fetch endpoint data
- `POST /fetch/events` - Fetch SIEM events  
- `POST /test/api` - Test API accessibility

#### Data Retrieval
- `GET /data/endpoints` - Get stored endpoints
- `GET /data/events` - Get stored events
- `GET /data/stats` - Get aggregated statistics



## 🐳 Docker Deployment

### Local with Docker Compose
```bash
cd backend
docker-compose up --build
```

### Production Docker
```bash
cd backend
docker build -t sophos-aggregator .
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e SOPHOS_CLIENT_ID=your_client_id \
  -e SOPHOS_CLIENT_SECRET=your_client_secret \
  -e SOPHOS_TENANT_ID=your_tenant_id \
  sophos-aggregator
```

## 📊 Data Collection

### Manual Data Fetching
```bash
# Fetch endpoints
curl -X POST http://localhost:8000/fetch/endpoints

# Fetch events
curl -X POST http://localhost:8000/fetch/events
```

### Automated Data Fetching with Railway Cron

For automated data collection, use Railway's built-in cron functionality. See [Railway Cron Setup](docs/RAILWAY_CRON.md) for detailed instructions.

**Quick Setup:**
1. In Railway dashboard, click "New Service" → Select "Cron"
2. Set command and schedule
3. Configure environment variables
4. Monitor job execution in Railway dashboard



## 🔍 Monitoring & Health

### Health Checks
- Application: `GET /health`
- Database connectivity: Built into health check
- API accessibility: Stored in database

### Logging
- Application logs: Standard output
- Database queries: SQLAlchemy logging
- API requests: Request/response logging

## 🛠️ Development

### Code Quality
```bash
cd backend
pip install black flake8 isort
black .
isort .
flake8
```

### Testing
```bash
cd backend
pip install pytest pytest-asyncio
pytest
```

### Database Migrations
```bash
cd backend
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🔐 Security

- **Environment Variables**: Sensitive data stored securely
- **Database**: PostgreSQL with proper authentication
- **API**: FastAPI with CORS configuration
- **Docker**: Non-root user in container

## 📈 Usage Examples

### Get Endpoint Statistics
```bash
curl http://localhost:8000/data/stats
```

### Filter Events by Severity
```bash
curl "http://localhost:8000/data/events?severity=high&limit=50"
```

### Get Online Endpoints Only
```bash
curl "http://localhost:8000/data/endpoints?online_only=true"
```

## 🚀 Railway Deployment Steps

1. **Create Railway Account**
   - Sign up at [Railway.app](https://railway.app)
   - Connect your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your sophos repository

3. **Add PostgreSQL Service**
   - Click "New Service"
   - Select "PostgreSQL"
   - Railway will provide the DATABASE_URL

4. **Configure Environment Variables**
   - Go to your app service
   - Click "Variables" tab
   - Add all required environment variables

5. **Deploy**
   - Railway will automatically deploy from your GitHub repository
   - Monitor the deployment logs

6. **Verify Deployment**
   - Check the health endpoint: `https://your-app.railway.app/health`
   - Test data fetching: `POST https://your-app.railway.app/fetch/endpoints`

## 📚 Documentation

- [Backend API Documentation](backend/README.md)
- [Sophos API Documentation](https://developer.sophos.com/)
- [Railway Documentation](https://docs.railway.app/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details 