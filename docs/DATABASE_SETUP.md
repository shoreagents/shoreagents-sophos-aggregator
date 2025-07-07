# Database URL Setup Guide

This guide explains the difference between `DATABASE_URL` and `DATABASE_PUBLIC_URL` and when to use each.

## Railway Database URLs

Railway provides two different database connection strings:

### DATABASE_URL (Internal)
- **Purpose**: Internal connection within Railway's network
- **Security**: Private and secure
- **Speed**: Faster (internal network)
- **Use case**: Your FastAPI application
- **Format**: `postgresql://username:password@internal-host:port/database`

### DATABASE_PUBLIC_URL (Public)
- **Purpose**: Public connection for external access
- **Security**: Publicly accessible
- **Speed**: Slower (external network)
- **Use case**: Local development, external tools
- **Format**: `postgresql://username:password@public-host:port/database`

## When to Use Which

### ✅ Use DATABASE_URL for:
- **Railway deployment** (your FastAPI app)
- **Railway cron jobs** (if available)
- **Any service running inside Railway**

### ✅ Use DATABASE_PUBLIC_URL for:
- **Local development**
- **Database management tools** (pgAdmin, DBeaver, etc.)
- **GitHub Actions** (if connecting directly to database)
- **External services** outside Railway

## Setup Instructions

### 1. Railway Environment Variables
In your Railway project, set these environment variables:

**For your main FastAPI service:**
```
DATABASE_URL=postgresql://username:password@internal-host:port/database
```

**For external access (optional):**
```
DATABASE_PUBLIC_URL=postgresql://username:password@public-host:port/database
```

### 2. Local Development
For local development, use the public URL:

```bash
# In your .env file
DATABASE_URL=postgresql://username:password@public-host:port/database
```

### 3. GitHub Actions
If using GitHub Actions for cron jobs, you can either:

**Option A: Use API endpoints (Recommended)**
```yaml
# .github/workflows/cron-fetch.yml
- name: Fetch Data
  run: |
    curl -X POST ${{ secrets.RAILWAY_APP_URL }}/fetch/endpoints
```

**Option B: Connect directly to database**
```yaml
# .github/workflows/cron-fetch.yml
- name: Fetch Data
  run: |
    # Use DATABASE_PUBLIC_URL here
    python scripts/fetch_data.py
  env:
    DATABASE_URL: ${{ secrets.DATABASE_PUBLIC_URL }}
```

## Security Considerations

### DATABASE_URL (Internal)
- ✅ Safe to use in Railway services
- ✅ No external access
- ✅ Faster performance

### DATABASE_PUBLIC_URL (Public)
- ⚠️ Be careful with this in public repositories
- ⚠️ Use GitHub Secrets for sensitive data
- ⚠️ Consider IP restrictions if possible

## Example Configuration

### Railway Service (.env)
```bash
# Your FastAPI app uses this
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway

# For external tools (optional)
DATABASE_PUBLIC_URL=postgresql://postgres:password@viaduct.proxy.rlwy.net:5432/railway
```

### Local Development (.env)
```bash
# Use public URL for local development
DATABASE_URL=postgresql://postgres:password@viaduct.proxy.rlwy.net:5432/railway
```

### GitHub Actions (Secrets)
```
RAILWAY_APP_URL=https://your-app.railway.app
DATABASE_PUBLIC_URL=postgresql://postgres:password@viaduct.proxy.rlwy.net:5432/railway
```

## Troubleshooting

### Connection Issues
- **Internal connection fails**: Check if `DATABASE_URL` is correct
- **External connection fails**: Check if `DATABASE_PUBLIC_URL` is correct
- **Local connection fails**: Use `DATABASE_PUBLIC_URL` for local development

### Performance Issues
- **Slow queries**: Use `DATABASE_URL` for internal connections
- **Timeout errors**: Check network connectivity for external connections

## Summary

| Use Case | URL Type | Example |
|----------|----------|---------|
| Railway App | `DATABASE_URL` | Internal Railway URL |
| Local Dev | `DATABASE_PUBLIC_URL` | Public Railway URL |
| External Tools | `DATABASE_PUBLIC_URL` | Public Railway URL |
| GitHub Actions | `DATABASE_PUBLIC_URL` | Public Railway URL | 