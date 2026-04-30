# 🚀 Azure Cloud Deployment for INTELLICA Logistics System

## Quick Start Deployment

### Option 1: Automated Script (Recommended)
```bash
# Make script executable
chmod +x deploy-to-azure.sh

# Run deployment script
./deploy-to-azure.sh
```

### Option 2: Manual Step-by-Step

1. **Install Azure CLI**
   ```bash
   # Windows (PowerShell as Admin)
   winget install -e --id Microsoft.AzureCLI

   # Or download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   ```

2. **Login to Azure**
   ```bash
   az login --use-device-code
   ```

3. **Run the deployment script**
   ```bash
   ./deploy-to-azure.sh
   ```

## What Gets Created

- ✅ **Resource Group**: `intellica-logistics-rg`
- ✅ **PostgreSQL Database**: Managed cloud database
- ✅ **App Service Plan**: B1 tier (scalable)
- ✅ **Web App**: Python 3.9 runtime
- ✅ **Environment Variables**: Pre-configured
- ✅ **Git Deployment**: Ready for code push

## Post-Deployment Setup

### 1. Set Solana Private Key
```bash
az webapp config appsettings set \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics \
  --setting SOLANA_PRIVATE_KEY="your-solana-private-key"
```

### 2. Deploy Your Code
```bash
# Add Azure remote
git remote add azure https://intellica-logistics.scm.azurewebsites.net/intellica-logistics.git

# Push to Azure
git push azure main
```

### 3. Access Your App
Your application will be available at:
```
https://intellica-logistics.azurewebsites.net
```

## File Structure for Deployment

```
├── app/                          # Your FastAPI application
├── requirements-azure.txt        # Azure-specific dependencies
├── startup.sh                    # Linux startup script
├── application.py                # Azure entry point
├── deploy-to-azure.sh           # Deployment automation script
├── AZURE_DEPLOYMENT_GUIDE.md    # Detailed deployment guide
└── .env.example                  # Environment variables template
```

## Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask/Django secret key | `your-secret-key` |
| `SOLANA_RPC_URL` | Solana network endpoint | `https://api.mainnet-beta.solana.com` |
| `SOLANA_PRIVATE_KEY` | Your Solana wallet private key | `base58-encoded-key` |

## Troubleshooting

### App Won't Start
```bash
# Check logs
az webapp log tail \
  --resource-group intellica-logistics-rg \
  --name intellica-logistics
```

### Database Connection Issues
- Verify DATABASE_URL format
- Check PostgreSQL firewall rules
- Ensure database exists

### Static Files Not Loading
- Check static file paths in templates
- Verify Azure storage configuration

## Cost Estimate

- **App Service (B1)**: ~$13/month
- **PostgreSQL (Basic)**: ~$25/month
- **Total**: ~$40/month for basic usage

## Security Notes

- 🔐 Store sensitive keys in Azure Key Vault (production)
- 🔒 Use managed identities for database access
- 🛡️ Enable Azure Defender for additional security
- 📊 Set up monitoring and alerts

## Need Help?

1. Check the detailed guide: `AZURE_DEPLOYMENT_GUIDE.md`
2. View Azure documentation: https://docs.microsoft.com/en-us/azure/app-service/
3. Check application logs using Azure portal or CLI

---

**🎯 Your logistics system will be live in the cloud in minutes!**</content>
<parameter name="filePath">c:\Users\acer\Documents\SLIIT UNI\Research Related\PP1\Solana Based Logistic Management System\AZURE_DEPLOYMENT_README.md