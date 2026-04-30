# Blockchain Integration - FAQ & Troubleshooting

## Frequently Asked Questions

### Q: Do I need to have Solana CLI installed to run the Python app?

**A:** No, but yes for building and deploying. Breaking it down:
- **NOT needed:** Running the Python app (it uses RPC)
- **NEEDED:** Building the Rust program (`cargo build-sbf`)
- **NEEDED:** Deploying to Solana (`solana deploy`)
- **NEEDED:** Managing wallets (`solana-keygen`)

### Q: What's the difference between RPC endpoint and running a validator?

**A:** 
- **RPC Endpoint:** Just reads blockchain data (what your Python app uses) - no setup needed
- **Validator:** Costs time/money - you probably don't need this

### Q: Can I test without spending money?

**A:** Yes! Devnet and Testnet are free with airdrops:
```bash
solana config set --url https://api.devnet.solana.com
solana airdrop 5  # Free SOL for testing
```

### Q: What's the Program ID and why do I need it?

**A:** It's the address of your deployed smart contract on Solana. You get it when you run:
```bash
solana deploy target/deploy/intellica_logistics_program.so --url devnet
```
Then put it in `.env` as `SOLANA_PROGRAM_ID`

### Q: Do I put my real wallet in `.env`?

**A:** Only use:
- **Devnet:** Test wallet is fine
- **Testnet:** Test wallet is fine  
- **Mainnet:** Use hardware wallet + secure secrets manager (never in .env file)

### Q: Why is my balance 0 after deploying?

**A:** You spent SOL on deployment fees. Deploy was successful!
```bash
solana balance  # Check remaining balance
solana airdrop 5 --url devnet  # Get more on devnet
```

### Q: What does "commitment level" mean?

**A:**
- `processed` - Seen by RPC, not confirmed. Fastest, least safe
- `confirmed` - Confirmed by most validators. Balanced (default)
- `finalized` - Finalized by network. Slowest, safest

Use `confirmed` for most cases.

### Q: Can my Python app work without a deployed program?

**A:** Yes! You can:
- Test wallet/balance queries
- Test transaction building
- Test without executing program instructions

But shipment tracking will need your program deployed.

---

## Troubleshooting

### Problem: "solana CLI not found" or "anchor not found"

**Symptom:** Command not recognized

**Solutions:**
```bash
# Check if installed
solana --version
anchor --version

# If not found, add to PATH (Linux/Mac)
export PATH="/home/$USER/.local/share/solana/install/active_release/bin:$PATH"

# Or reinstall
# Solana: https://docs.solana.com/cli/install-solana-cli-tools
# Anchor: https://book.anchor-lang.com/getting_started/installation.html
# Rust: https://rustup.rs/
```

### Problem: "rustc not found"

**Symptom:** Can't build Solana program

**Solution:**
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Or on Windows
# Visit https://rustup.rs/ and follow instructions
```

### Problem: "Build failed" or "error: linker not found"

**Symptom:** `cargo build-sbf` fails during build

**Solutions:**
```bash
# Update Rust
rustup update

# Install SBF toolchain
rustup install stable
rustup target add bpf-solana

# Clean and rebuild
cargo clean
./build.sh  # or build.bat
```

### Problem: "Python module not found: solders"

**Symptom:** `ImportError: No module named 'solders'`

**Solution:**
```bash
pip install solders>=0.18.0
pip install solana>=0.32.0
```

Or update all requirements:
```bash
pip install -r requirements.txt
```

### Problem: "Can't connect to Solana network"

**Symptom:** Connection timeout, "failed to connect"

**Check these:**
```bash
# 1. Internet connection
ping google.com

# 2. RPC endpoint is accessible
curl https://api.devnet.solana.com -X POST -H "Content-Type: application/json"

# 3. Correct network in .env
# SOLANA_NETWORK should be: devnet, testnet, or mainnet

# 4. Try pinging with Solana CLI
solana ping

# 5. Check RPC endpoint isn't rate limited
# If so, try a different RPC endpoint
```

### Problem: "Insufficient balance" when deploying

**Symptom:** Deploy fails - "Insufficient balance for rent"

**Solutions:**
```bash
# 1. Check balance
solana balance

# 2. On devnet, request airdrop
solana airdrop 5 --url devnet

# 3. On mainnet, you need actual SOL
# You can't proceed without it

# 4. Try another wallet with balance
solana-keygen new --outfile ~/.config/solana/id.json
solana config set --keypair ~/.config/solana/id.json
```

### Problem: "Account not found" when querying balance

**Symptom:** `get_balance()` returns `None` or error

**Reasons:**
1. Invalid public key format
2. Account hasn't received any SOL yet
3. Network timeout

**Solutions:**
```python
# Verify public key format
from solders.pubkey import Pubkey
try:
    pubkey = Pubkey("YOUR_ADDRESS")
except Exception as e:
    print(f"Invalid address: {e}")

# Send some SOL to the account first
# Or ensure account exists on that network
```

### Problem: "TransactionVersion not specified"

**Symptom:** Transaction fails with version error

**Solution:** Not a real error usually - the code handles this. Check:
```python
# Use correct commitment level
from solana.rpc.commitment import Confirmed

# Make sure client is using Confirmed commitment
```

### Problem: "IDL file not found"

**Symptom:** Warning about missing IDL file on startup

**Solution:**
```bash
# Generate IDL with Anchor
cd solana-program
anchor idl init -f ./src/lib.rs

# Or update IDL_PATH in .env to correct location
IDL_PATH=./solana-program/target/idl/intellica_logistics_program.json
```

Note: IDL is optional for basic operation but needed for full feature support.

### Problem: "Program account not found"

**Symptom:** Can't find your deployed program

**Solutions:**
```bash
# 1. Verify Program ID is correct
echo $SOLANA_PROGRAM_ID

# 2. Check it's deployed on current network
solana program show YOUR_PROGRAM_ID

# 3. Ensure you're on the right network
solana config get

# 4. If not found, redeploy
cd solana-program
./deploy.sh devnet
```

### Problem: "Permission denied" on shell scripts

**Symptom:** `./build.sh: Permission denied`

**Solution (Linux/Mac):**
```bash
chmod +x build.sh deploy.sh
./build.sh
```

### Problem: "Network cluster is unstable" or "slot generation lagging"

**Symptom:** Transactions fail or timeout

**Solutions:**
```bash
# 1. Check network health
solana cluster-version

# 2. Wait a moment and retry
# (Network might be catching up)

# 3. Try a different RPC endpoint
# Public endpoints sometimes have issues
# Consider using a dedicated RPC provider

# 4. Increase timeout in code
# (Pending implementation in transaction manager)
```

### Problem: "Lamports" vs "SOL" confusion

**Relationship:**
- 1 SOL = 1,000,000,000 lamports
- Blockchain stores values in lamports (smallest unit)
- Python code displays as SOL

Example:
```python
lamports = 5_000_000_000
sol = lamports / 1_000_000_000
print(f"{sol} SOL = {lamports} lamports")  # 5.0 SOL = 5000000000 lamports
```

---

## Performance Tuning

### Slow Transactions?

1. **Increase priority fee** (faster inclusion)
   ```env
   PRIORITY_FEE=5000
   ```

2. **Use different commitment level**
   ```python
   # Change from Confirmed to Processed for speed
   # (less safe, but faster)
   ```

3. **Use public RPC vs private**
   - Public (free): api.devnet.solana.com
   - Private (paid): Alchemy, QuickNode, etc.

### Network Polling?

1. **Check your internet connection**
2. **Monitor RPC endpoint latency**
3. **Use WebSocket for streaming** (future enhancement)

---

## Debugging

### Enable logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed blockchain operations.

### Check blockchain logs:
```bash
# View recent transactions of account
solana address
solana tx <TRANSACTION_SIGNATURE>

# View program state
solana account <ACCOUNT_ADDRESS>
```

### Verify configuration:
```python
from app.blockchain.config import BlockchainConfig

config = BlockchainConfig()
print(f"Network: {config.NETWORK_CLUSTER}")
print(f"RPC: {config.get_rpc_endpoint()}")
print(f"Program: {config.PROGRAM_ID}")
print(f"Wallet: {config.WALLET_PATH}")
```

---

## Network-Specific Notes

### Devnet
✅ Free airdrops
✅ For testing only
❌ Data gets cleared
⏲️ ~30 minute airdrops (rate limited)

### Testnet
✅ More stable than devnet
✅ Free airdrops
❌ Still for testing only
⏲️ Airdrops less frequent

### Mainnet
⚠️ Real SOL costs money
⚠️ Transactions are permanent
✅ Production ready
✅ Most stable

**Recommendation:** Test on devnet, move to mainnet only when ready.

---

## Security Reminders

🔐 **Critical:**
1. Never commit real keypairs in `.env`
2. Never log private keys
3. Use environment variables for secrets
4. Use hardware wallet for mainnet
5. Verify transaction details before signing

⚠️ **Before going mainnet:**
1. Test thoroughly on devnet
2. Audit smart contract code
3. Security review of integration
4. Monitor transactions after launch

---

## Still Having Issues?

1. **Check the detailed guides:**
   - `SOLANA_SETUP.md` - Full setup instructions
   - `BLOCKCHAIN_INTEGRATION_STATUS.md` - System overview
   - `INTEGRATION_COMPLETE.md` - Complete reference

2. **Run the test script:**
   ```bash
   python test_blockchain_integration.py
   ```
   The test output will identify which component is failing.

3. **Check logs:**
   ```python
   # Enable debug logging
   import logging
   logging.getLogger("app").setLevel(logging.DEBUG)
   ```

4. **Verify installations:**
   ```bash
   solana --version
   anchor --version
   rustc --version
   cargo --version
   python -c "import solders; import solana; print('OK')"
   ```

5. **Consult documentation:**
   - Solana: https://docs.solana.com/
   - Anchor: https://book.anchor-lang.com/
   - GitHub issues: https://github.com/solana-labs/solana/issues

---

**Remember:** Most issues are resolved by:
1. Checking your `.env` configuration
2. Verifying tools are installed and in PATH
3. Ensuring you're on the right network
4. Requesting fresh airdrops on devnet (they expire)
5. Running the test script to identify the issue

Good luck! 🚀
