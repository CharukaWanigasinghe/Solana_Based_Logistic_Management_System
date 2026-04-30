# 🚀 Quick Start - Solana Integration

## 30-Second Setup

```bash
# 1. Copy environment config
copy .env.example .env

# 2. Install Python packages
pip install -r requirements.txt

# 3. Test the setup
python test_blockchain_integration.py
```

## Build & Deploy (5 minutes)

```bash
# 1. Build your Solana program
cd solana-program
.\build.bat                    # Windows
# OR
./build.sh                     # Linux/Mac

# 2. Deploy to Solana
./deploy.sh devnet

# 3. Copy Program ID from output

# 4. Update .env with Program ID
SOLANA_PROGRAM_ID=xx...xx
```

## Edit Your .env

```env
# Network choice
SOLANA_NETWORK=devnet

# Your wallet (from 'solana address')
SOLANA_WALLET_PATH=~/.config/solana/id.json

# After deploying your program
SOLANA_PROGRAM_ID=YOUR_DEPLOYED_ID

# Enable blockchain features
USE_BLOCKCHAIN=true
BLOCKCHAIN_GPS_TRACKING=true
BLOCKCHAIN_DELIVERY_CONFIRMATION=true
```

## Verify Integration

```bash
# Run test script
python test_blockchain_integration.py

# Should see ✅ all tests passed
```

## Use in Your Code

```python
from app.blockchain import get_solana_client

async def track_shipment():
    client = await get_solana_client()
    
    # Get wallet balance
    balance = await client.get_balance("YOUR_WALLET_ADDRESS")
    print(f"Balance: {balance} SOL")
    
    # Use in your logistics tracking...
```

## Common Commands

```bash
# Check Solana setup
solana address
solana balance

# Get free SOL (devnet only)
solana airdrop 5 --url devnet

# Check program deployment
solana program show YOUR_PROGRAM_ID

# View program account
solana account YOUR_PROGRAM_ADDRESS
```

## Files Created

✅ `Anchor.toml` - Framework config
✅ `build.sh` / `build.bat` - Build scripts
✅ `deploy.sh` - Deploy script
✅ `app/blockchain/` - Python integration (4 files)
✅ `app/config.py` - Updated config
✅ `.env.example` - Config template
✅ Documentation files - Guides and references
✅ `test_blockchain_integration.py` - Test your setup
✅ `requirements.txt` - Updated dependencies

## Need Help?

📖 **Detailed Guide:** See `SOLANA_SETUP.md`
📋 **Status Check:** See `BLOCKCHAIN_INTEGRATION_STATUS.md`
🔍 **Full Details:** See `INTEGRATION_COMPLETE.md`

## Troubleshooting

**"Module not found: solders"**
```bash
pip install solders
```

**"Solana CLI not found"**
```bash
# Add to PATH or reinstall Solana CLI
solana --version
```

**"Network connection failed"**
- Check internet connection
- Verify SOLANA_NETWORK is correct
- Try pinging RPC: `solana ping`

**"Insufficient balance"**
```bash
solana airdrop 2  # On devnet/testnet
```

---

**All tools are connected and ready! 🎉**

Next: Follow SOLANA_SETUP.md for detailed instructions
