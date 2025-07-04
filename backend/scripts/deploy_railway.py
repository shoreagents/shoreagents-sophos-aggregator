#!/usr/bin/env python3
"""
Railway deployment helper script for Sophos Aggregator
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime

def check_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
        else:
            print("❌ Railway CLI is not installed")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI is not installed")
        return False

def check_git_repo():
    """Check if we're in a git repository."""
    try:
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository found")
            return True
        else:
            print("❌ Not a git repository")
            return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        'SOPHOS_CLIENT_ID',
        'SOPHOS_CLIENT_SECRET', 
        'SOPHOS_TENANT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_dockerfile():
    """Check if Dockerfile exists."""
    if os.path.exists('Dockerfile'):
        print("✅ Dockerfile found")
        return True
    else:
        print("❌ Dockerfile not found")
        return False

def check_railway_json():
    """Check if railway.json exists."""
    if os.path.exists('railway.json'):
        print("✅ railway.json found")
        return True
    else:
        print("❌ railway.json not found")
        return False

def test_local_app():
    """Test if the local application can start."""
    print("🔧 Testing local application...")
    try:
        # Test database connection
        from app.database import create_tables
        create_tables()
        print("✅ Database connection successful")
        
        # Test Sophos API connection
        from app.sophos_client import SophosClient
        client = SophosClient()
        token = client.get_access_token()
        if token:
            print("✅ Sophos API connection successful")
        else:
            print("⚠️  Sophos API connection failed")
            
    except Exception as e:
        print(f"❌ Local application test failed: {e}")
        return False
    
    return True

def create_deployment_checklist():
    """Create a deployment checklist."""
    print("\n📋 Railway Deployment Checklist:")
    print("=" * 50)
    
    checks = [
        ("Railway CLI installed", check_railway_cli()),
        ("Git repository", check_git_repo()),
        ("Environment variables", check_environment_variables()),
        ("Dockerfile exists", check_dockerfile()),
        ("railway.json exists", check_railway_json()),
        ("Local app test", test_local_app())
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Ready for deployment.")
        return True
    else:
        print("⚠️  Some checks failed. Please fix issues before deploying.")
        return False

def generate_railway_commands():
    """Generate Railway deployment commands."""
    print("\n🚀 Railway Deployment Commands:")
    print("=" * 50)
    
    commands = [
        "# Login to Railway",
        "railway login",
        "",
        "# Initialize Railway project (if not already done)",
        "railway init",
        "",
        "# Link to existing project (if you have one)",
        "# railway link",
        "",
        "# Set environment variables",
        "railway variables set SOPHOS_CLIENT_ID=your_client_id",
        "railway variables set SOPHOS_CLIENT_SECRET=your_client_secret", 
        "railway variables set SOPHOS_TENANT_ID=your_tenant_id",
        "",
        "# Deploy to Railway",
        "railway up",
        "",
        "# Check deployment status",
        "railway status",
        "",
        "# View logs",
        "railway logs",
        "",
        "# Open the deployed app",
        "railway open"
    ]
    
    for cmd in commands:
        print(cmd)

def create_github_workflow():
    """Create GitHub Actions workflow for Railway deployment."""
    workflow_content = """name: Deploy to Railway

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        python -m pytest
    
    - name: Deploy to Railway
      uses: railway/deploy@v1
      with:
        service: ${{ secrets.RAILWAY_SERVICE }}
        token: ${{ secrets.RAILWAY_TOKEN }}
"""
    
    workflow_dir = ".github/workflows"
    os.makedirs(workflow_dir, exist_ok=True)
    
    with open(f"{workflow_dir}/railway-deploy.yml", "w") as f:
        f.write(workflow_content)
    
    print(f"✅ Created GitHub workflow: {workflow_dir}/railway-deploy.yml")

def main():
    """Main deployment helper function."""
    print("🚀 Railway Deployment Helper for Sophos Aggregator")
    print("=" * 60)
    
    # Run all checks
    deployment_ready = create_deployment_checklist()
    
    if deployment_ready:
        print("\n📝 Next Steps:")
        print("1. Push your code to GitHub")
        print("2. Create a Railway account at https://railway.app")
        print("3. Connect your GitHub repository to Railway")
        print("4. Add PostgreSQL service in Railway dashboard")
        print("5. Set environment variables in Railway")
        print("6. Deploy using the commands below:")
        
        generate_railway_commands()
        
        # Create GitHub workflow
        create_github_workflow()
        
        print("\n💡 Tips:")
        print("- Make sure your DATABASE_URL is set in Railway")
        print("- Monitor deployment logs for any issues")
        print("- Test the health endpoint after deployment")
        print("- Start the scheduler: POST /scheduler/start")
        
    else:
        print("\n🔧 Fix the failed checks before deploying.")
        print("Common issues:")
        print("- Install Railway CLI: npm install -g @railway/cli")
        print("- Set environment variables in .env file")
        print("- Ensure all files are committed to git")

if __name__ == "__main__":
    main() 