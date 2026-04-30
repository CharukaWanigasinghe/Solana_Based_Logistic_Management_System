# Solana Blockchain Integration Setup Guide

## Overview

This guide walks you through connecting Solana CLI, Rust, and Anchor Framework to your Solana-based Logistics Management System.

## Prerequisites

You've already installed:
- ✅ Solana CLI
- ✅ Rust
- ✅ Anchor Framework

## Step 1: Verify Your Installations

### Windows (PowerShell)
```powershell
# Check Solana CLI
solana --version

# Check Rust
rustc --version
cargo --version

# Check Anchor
anchor --version
```

### Linux/Mac
```bash
# Check Solana CLI
solana --version

# Check Rust
rustc --version
cargo --version

# Check Anchor
anchor --version
```

## Step 2: Configure Solana CLI

### Create/Use Wallet
```bash
# Create a new keypair (if you don't have one)
solana-keygen new --outfile ~/.config/solana/id.json

# Check your wallet address
solana address

# View wallet balance
solana balance
```

### Set Network Cluster
```bash
# For Devnet (development, with free airdrops)
solana config set --url https://api.devnet.solana.com

# For Testnet
solana config set --url https://api.testnet.solana.com

# For Localhost (local validator)
solana config set --url http://localhost:8899
```

### Airdrop SOL (Devnet/Testnet only)
```bash
# Request SOL for testing
solana airdrop 2
```

## Step 3: Configure Environment

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```bash
   # Set your Solana network
   SOLANA_NETWORK=devnet

   # Set your wallet path (from Step 2)
   SOLANA_WALLET_PATH=~/.config/solana/id.json

   # Update after deploying your program
   SOLANA_PROGRAM_ID=<your-deployed-program-id>
   ```

## Step 4: Build the Solana Program

### Using Build Scripts

#### On Linux/Mac:
```bash
cd solana-program
chmod +x build.sh deploy.sh
./build.sh
```

#### On Windows:
```powershell
cd solana-program
.\build.bat
```

### Or Using Anchor directly:
```bash
cd solana-program
anchor build
```

The compiled program will be at: `solana-program/target/deploy/intellica_logistics_program.so`

## Step 5: Deploy to Solana

### Automatic Deployment Script

#### On Linux/Mac:
```bash
cd solana-program
./deploy.sh devnet
```

#### On Windows (Manual):
```bash
cd solana-program
solana deploy target/deploy/intellica_logistics_program.so --url devnet
```

### Get Your Program ID
The deployment output will show your Program ID:
```
Program Id: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Signature: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Update Configuration
Update your `.env` file with the Program ID:
```
SOLANA_PROGRAM_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Also update `solana-program/Anchor.toml`:
```toml
[programs.devnet]
intellica_logistics_program = "YOUR_PROGRAM_ID_HERE"
```

## Step 6: Install Python Dependencies

```bash
# Install required Python packages
pip install solders
pip install solana
pip install python-dotenv

# Or use the requirements.txt
pip install -r requirements.txt
```

Make sure `requirements.txt` contains:
```
solders>=0.18.0
solana>=0.29.0
python-dotenv>=1.0.0
```

## Step 7: Test the Integration

### Test Solana Connection
```python
# Create a test script: test_solana_connection.py
from app.blockchain.solana_client import SolanaClient, get_solana_client
from app.blockchain.config import BlockchainConfig
import asyncio

async def test_connection():
    # Get client
    client = await get_solana_client()
    
    # Check health
    is_healthy = await client.health_check()
    print(f"Network healthy: {is_healthy}")
    
    # Get network status
    status = await client.get_network_status()
    print(f"Network status: {status}")
    
    # Check wallet
    wallet_pk = client.get_wallet_pubkey()
    print(f"Wallet: {wallet_pk}")
    
    # Get balance
    if wallet_pk:
        balance = await client.get_balance(wallet_pk)
        print(f"Balance: {balance} SOL")

# Run test
asyncio.run(test_connection())
```

Then run:
```bash
python test_solana_connection.py
```

## Step 8: Verify IDL Generation

The IDL (Interface Definition Language) file is needed for program interaction.

### Generate IDL with Anchor
```bash
cd solana-program
anchor idl init -f ./src/lib.rs
```

This creates the IDL at: `target/idl/intellica_logistics_program.json`

Update in `.env`:
```
IDL_PATH=./solana-program/target/idl/intellica_logistics_program.json
```

## Common Issues & Solutions

### Issue: "Solana CLI not found"
**Solution:** Add Solana to PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/$USER/.local/share/solana/install/active_release/bin:$PATH"
```

### Issue: "Anchor not found"
**Solution:** Install Anchor:
```bash
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest
```

### Issue: "Insufficient balance"
**Solution:** Request airdrop on devnet/testnet:
```bash
solana airdrop 5
```

### Issue: "Program not deployed"
**Solution:** Check if deployment was successful:
```bash
solana program show <PROGRAM_ID>
```

### Issue: Python import errors
**Solution:** Make sure packages are installed:
```bash
pip install solders solana python-dotenv
```

## File Structure Reference

```
solana-program/
├── Anchor.toml              # Anchor configuration
├── Cargo.toml              # Rust dependencies
├── build.sh               # Build script (Linux/Mac)
├── build.bat              # Build script (Windows)
├── deploy.sh              # Deploy script
├── src/
│   └── lib.rs             # Solana program code
└── target/
    ├── deploy/
    │   └── intellica_logistics_program.so
    └── idl/
        └── intellica_logistics_program.json

app/
├── blockchain/
│   ├── config.py          # Blockchain configuration
│   ├── solana_client.py   # Solana client (CONNECTED ✅)
│   ├── solana_transactions.py  # Transaction handling (CONNECTED ✅)
│   └── solana_verifier.py # Transaction verification (CONNECTED ✅)
├── config.py              # App configuration (UPDATED ✅)
└── main.py               # FastAPI app

.env                        # Your configuration (CREATE with .env.example)
.env.example               # Template (CREATE ✅)
```

## Next Steps

1. **Run the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Test blockchain endpoints:**
   - Visit `http://localhost:8000/blockchain/status`
   - Visit `http://localhost:8000/blockchain/balance`

3. **Integrate with logistics features:**
   - Shipment creation on blockchain
   - GPS tracking recording
   - Delivery confirmation

4. **Deploy to production:**
   - Use mainnet (when ready)
   - Configure proper wallet security
   - Set environment variables via secrets manager

## Security Notes

⚠️ **Important:**
- Never commit `.env` files with real keypairs
- Use environment variables in production
- Rotate keys regularly
- Keep wallet seeds secure (don't version control)
- Use hardware wallets for mainnet

## Resources

- [Solana Documentation](https://docs.solana.com/)
- [Anchor Book](https://book.anchor-lang.com/)
- [Solana CLI Reference](https://docs.solana.com/cli)
- [Rust Book](https://doc.rust-lang.org/book/)
- [solders (Python library)](https://github.com/kevinheavey/solders)

## Support

For issues with:
- **Solana CLI:** https://github.com/solana-labs/solana
- **Anchor:** https://github.com/coral-xyz/anchor
- **Python integration:** Check blockchain module logs

---

**Successfully integrated! Your Solana blockchain setup is ready to use.** ✅
