# Azure Cloud Deployment Guide for INTELLICA Logistics System

## Overview
This guide will help you deploy your Solana-based logistics management system to Microsoft Azure cloud. We'll use Azure App Service for a simple, scalable deployment.

## Prerequisites
- Azure account with active subscription
- Azure CLI installed (`az` command)
- Git repository with your code
- Basic understanding of cloud concepts

## Step 1: Prepare Your Application for Cloud Deployment

### 1.1 Update Database Configuration
Your current SQLite database won't work well in the cloud. Let's upgrade to Azure Database for PostgreSQL:

**Create `app/config.py` (if not exists):**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    SOLANA_PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
```

**Update `app/database.py`:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Config

# Use PostgreSQL for cloud deployment
DATABASE_URL = Config.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### 1.2 Create Azure-Specific Files

**Create `requirements-azure.txt`:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
solana==0.32.0
solders>=0.18.0
websockets==12.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-decouple==3.8
pandas==2.1.4
openpyxl==3.1.2
python-dotenv>=1.0.0
psycopg2-binary==2.9.7
azure-storage-blob==12.17.0
gunicorn==21.2.0
```

**Create `startup.sh` (Linux startup script):**
```bash
#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y libpq-dev gcc

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements-azure.txt

# Run database migrations
alembic upgrade head

# Collect static files (if needed)
# python manage.py collectstatic --noinput

# Start the application
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Create `web.config` (Windows/IIS):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" scriptProcessor="D:\home\Python364-x64\python.exe|D:\home\Python364-x64\wfastcgi.py" resourceType="Unspecified" />
    </handlers>
    <rewrite>
      <rules>
        <rule name="Static Files" stopProcessing="true">
          <match url="^/static/(.*)$" />
          <action type="None" />
        </rule>
        <rule name="Configure Python" stopProcessing="true">
          <match url="(.*)" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_URI}" negate="true" pattern="^/static/" />
          </conditions>
          <action type="Rewrite" url="handler.fcgi/{R:1}" />
        </conditions>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

**Create `application.py` (Azure App Service entry point):**
```python
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the app
from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

## Step 2: Set Up Azure Resources

### 2.1 Create Resource Group
```bash
# Login to Azure
az login

# Create resource group
az group create --name intellica-logistics-rg --location eastus
```

### 2.2 Create Azure Database for PostgreSQL
```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group intellica-logistics-rg \
  --name intellica-postgres \
  --location eastus \
  --admin-user intellicaadmin \
  --admin-password YourSecurePassword123! \
  --sku-name B_Gen5_1 \
  --version 13

# Create database
az postgres db create \
  --resource-group intellica-logistics-rg \
  --server-name intellica-postgres \
  --name logistics_db

# Configure firewall (allow Azure services)
az postgres server firewall-rule create \
  --resource-group intellica-logistics-rg \
  --server-name intellica-postgres \
  --name AllowAllAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

### 2.3 Create Azure App Service Plan
```bash
# Create App Service plan
az appservice plan create \
  --name intellica-plan \
  --resource-group intellica-logistics-rg \
  --location eastus \
  --sku B1 \
  --is-linux
```

### 2.4 Create Web App
```bash
# Create web app
az webapp create \
  --resource-group intellica-logistics-rg \
  --plan intellica-plan \
  --name intellica-logistics \
  --runtime "PYTHON|3.9" \
  --deployment-local-git
```

## Step 3: Configure Environment Variables

### 3.1 Set App Settings
```bash
# Database connection
az webapp config appsettings set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --setting DATABASE_URL="postgresql://intellicaadmin@intellica-postgres:YourSecurePassword123!@intellica-postgres.postgres.database.azure.com:5432/logistics_db"

# Secret key
az webapp config appsettings set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --setting SECRET_KEY="your-super-secret-key-here"

# Solana configuration
az webapp config appsettings set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --setting SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"

# Optional: Solana private key (use Key Vault for production)
az webapp config appsettings set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --setting SOLANA_PRIVATE_KEY="your-solana-private-key"
```

### 3.2 Configure Startup Command
```bash
az webapp config set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --startup-file "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
```

## Step 4: Deploy Your Code

### 4.1 Push to Azure
```bash
# Get deployment URL
az webapp deployment source show \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --query url -o tsv

# Add Azure as remote (replace URL with your deployment URL)
git remote add azure https://intellica-logistics.scm.azurewebsites.net/intellica-logistics.git

# Push to Azure
git push azure main
```

### 4.2 Alternative: Deploy via ZIP
```bash
# Create deployment package
az webapp deployment source config-zip \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --src deployment-package.zip
```

## Step 5: Configure Custom Domain (Optional)

### 5.1 Add Custom Domain
```bash
# Add custom domain
az webapp config hostname set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --hostname www.intellica-logistics.com
```

## Step 6: Set Up Monitoring and Logging

### 6.1 Enable Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app intellica-insights \
  --location eastus \
  --resource-group intellica-logistics-rg \
  --application-type web

# Connect to web app
az webapp config appsettings set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --setting APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

### 6.2 View Logs
```bash
# Stream logs
az webapp log tail \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics
```

## Step 7: Set Up CI/CD Pipeline (Optional)

### 7.1 Create GitHub Actions Workflow
Create `.github/workflows/azure-deploy.yml`:
```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements-azure.txt

    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: intellica-logistics
        slot-name: production
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: .
```

## Step 8: Security Best Practices

### 8.1 Set Up Azure Key Vault
```bash
# Create Key Vault
az keyvault create \
  --name intellica-keyvault \
  --resource-group intellica-logistics-rg \
  --location eastus

# Store secrets
az keyvault secret set \
  --vault-name intellica-keyvault \
  --name solana-private-key \
  --value "your-solana-private-key"
```

### 8.2 Configure Networking
```bash
# Enable VNet integration
az webapp vnet-integration add \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --vnet myVNet \
  --subnet mySubnet
```

## Step 9: Testing and Verification

### 9.1 Test Your Deployment
1. Open browser to `https://intellica-logistics.azurewebsites.net`
2. Test all functionality:
   - User login with Phantom wallet
   - Shipment creation
   - Tracking events
   - History viewing
   - GPS verification

### 9.2 Monitor Performance
```bash
# Check app status
az webapp show \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --query state

# View metrics
az monitor metrics list \
  --resource /subscriptions/.../resourceGroups/intellica-logistics-rg/providers/Microsoft.Web/sites/intellica-logistics \
  --metric "HttpResponseTime"
```

## Step 10: Cost Optimization

### 10.1 Set Up Auto-scaling
```bash
# Configure auto-scaling
az monitor autoscale create \
  --resource-group intellica-logistics-rg \
  --name intellica-autoscale \
  --resource /subscriptions/.../resourceGroups/intellica-logistics-rg/providers/Microsoft.Web/serverfarms/intellica-plan \
  --min-count 1 \
  --max-count 3 \
  --count 1
```

### 10.2 Set Up Cost Alerts
```bash
# Create budget alert
az consumption budget create \
  --resource-group intellica-logistics-rg \
  --name monthly-budget \
  --amount 100 \
  --time-grain Monthly \
  --category Cost
```

## Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify PostgreSQL firewall rules
   - Ensure database exists

2. **Static Files Not Loading**
   - Check static file configuration
   - Verify file paths in templates

3. **Blockchain Connection Issues**
   - Verify SOLANA_RPC_URL
   - Check network connectivity
   - Validate wallet configuration

4. **Application Startup Errors**
   - Check application logs: `az webapp log tail`
   - Verify Python dependencies
   - Check environment variables

## Cost Estimate

### Monthly Costs (Approximate):
- **App Service (B1)**: $13.14/month
- **PostgreSQL (Basic, 1GB)**: $25/month
- **Storage (Hot LRS, 100GB)**: $2.40/month
- **Bandwidth**: $0.09/GB
- **Total**: ~$40-50/month for basic usage

## Summary

Your INTELLICA logistics system is now deployed to Azure cloud with:
- ✅ Scalable web application
- ✅ Managed PostgreSQL database
- ✅ Secure environment configuration
- ✅ Monitoring and logging
- ✅ Production-ready architecture

Access your application at: `https://intellica-logistics.azurewebsites.net`</content>
<parameter name="filePath">c:\Users\acer\Documents\SLIIT UNI\Research Related\PP1\Solana Based Logistic Management System\AZURE_DEPLOYMENT_GUIDE.md