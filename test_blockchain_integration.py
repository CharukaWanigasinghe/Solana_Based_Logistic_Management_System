#!/usr/bin/env python3
"""
Test script to verify Solana blockchain integration
Run this to ensure everything is set up correctly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.blockchain import (
    get_solana_client,
    BlockchainConfig,
    SecurityValidator
)


async def test_environment_config():
    """Test environment configuration"""
    print("\n" + "="*50)
    print("1. Testing Environment Configuration")
    print("="*50)
    
    config = BlockchainConfig()
    
    print(f"Network Cluster: {config.NETWORK_CLUSTER}")
    print(f"RPC Endpoint: {config.get_rpc_endpoint()}")
    print(f"WS Endpoint: {config.get_ws_endpoint()}")
    print(f"Program ID: {config.PROGRAM_ID}")
    print(f"Wallet Path: {config.WALLET_PATH}")
    print(f"IDL Path: {config.IDL_PATH}")
    print(f"Use Blockchain: {config.USE_BLOCKCHAIN}")
    
    # Validate config
    is_valid, error_msg = config.validate_config()
    if not is_valid:
        print(f"⚠️  Config Warning: {error_msg}")
    else:
        print("✅ Configuration Valid")
    
    return is_valid


async def test_solana_connection():
    """Test Solana network connection"""
    print("\n" + "="*50)
    print("2. Testing Solana Network Connection")
    print("="*50)
    
    try:
        client = await get_solana_client()
        print("✅ Solana client created")
        
        # Test health check
        is_healthy = await client.health_check()
        if is_healthy:
            print("✅ Network health check passed")
        else:
            print("❌ Network health check failed")
            return False
        
        # Get network status
        status = await client.get_network_status()
        if status:
            print(f"✅ Network status retrieved:")
            print(f"   Slot: {status.get('slot')}")
            print(f"   Cluster: {status.get('cluster')}")
            print(f"   RPC: {status.get('rpc_endpoint')}")
        
        return True
    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


async def test_wallet():
    """Test wallet loading"""
    print("\n" + "="*50)
    print("3. Testing Wallet Configuration")
    print("="*50)
    
    try:
        client = await get_solana_client()
        
        if client.wallet_manager and client.wallet_manager.is_loaded():
            pubkey = client.wallet_manager.get_public_key()
            print(f"✅ Wallet loaded: {pubkey}")
            
            # Try to get balance
            balance = await client.get_balance(pubkey)
            if balance is not None:
                print(f"✅ Wallet balance: {balance:.4f} SOL")
            else:
                print(f"⚠️  Could not retrieve balance (account may not exist)")
            
            return True
        else:
            print("⚠️  Wallet not loaded (optional, continue with public key only)")
            return True
    
    except Exception as e:
        print(f"❌ Wallet error: {e}")
        return False


async def test_validators():
    """Test security validators"""
    print("\n" + "="*50)
    print("4. Testing Security Validators")
    print("="*50)
    
    try:
        # Test public key validation
        test_pubkey = "11111111111111111111111111111112"
        is_valid = await SecurityValidator.validate_pubkey(test_pubkey)
        print(f"✅ Public key validation: {is_valid}")
        
        # Test amount validation
        is_valid = await SecurityValidator.validate_amount(1.5, 2.0)
        print(f"✅ Amount validation: {is_valid}")
        
        # Test shipment data validation
        test_data = {
            'shipment_id': 1,
            'destination': 'New York',
            'product_line': 'Electronics',
            'quantity': 100
        }
        is_valid = await SecurityValidator.validate_shipment_data(test_data)
        print(f"✅ Shipment data validation: {is_valid}")
        
        return True
    
    except Exception as e:
        print(f"❌ Validator error: {e}")
        return False


async def show_next_steps():
    """Show next steps"""
    print("\n" + "="*50)
    print("Next Steps")
    print("="*50)
    print("""
1. Build the Solana program:
   cd solana-program
   ./build.sh (Linux/Mac) or .\\build.bat (Windows)

2. Deploy to Solana:
   ./deploy.sh devnet

3. Update .env with your Program ID

4. Integrate blockchain calls in your routes

5. Test end-to-end workflows
    """)


async def main():
    """Run all tests"""
    print("\n" + "🚀 Solana Blockchain Integration Test")
    print("=" * 50)
    
    results = {
        "Environment Config": False,
        "Solana Connection": False,
        "Wallet": False,
        "Validators": False
    }
    
    # Run tests
    results["Environment Config"] = await test_environment_config()
    results["Solana Connection"] = await test_solana_connection()
    results["Wallet"] = await test_wallet()
    results["Validators"] = await test_validators()
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ All tests passed! Your setup is ready.")
        await show_next_steps()
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    # Cleanup
    from app.blockchain import close_solana_client
    await close_solana_client()


if __name__ == "__main__":
    asyncio.run(main())
