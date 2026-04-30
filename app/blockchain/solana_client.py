"""
Solana blockchain client for logistics management
Handles all interactions with Solana network including wallet management and program interaction
"""

import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.responses import GetAccountInfoResp
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

from .config import BlockchainConfig

logger = logging.getLogger(__name__)


class SolanaWalletManager:
    """Manages Solana wallet operations"""
    
    def __init__(self, wallet_path: Optional[str] = None):
        """
        Initialize wallet manager
        
        Args:
            wallet_path: Path to wallet keypair file (defaults to config setting)
        """
        self.wallet_path = wallet_path or BlockchainConfig.WALLET_PATH
        self.keypair: Optional[Keypair] = None
        self._loaded = False
    
    def load_keypair(self) -> bool:
        """
        Load keypair from wallet file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not Path(self.wallet_path).exists():
                logger.error(f"Wallet file not found: {self.wallet_path}")
                return False
            
            with open(self.wallet_path, 'r') as f:
                secret_key = json.load(f)
            
            # Create keypair from secret key
            if isinstance(secret_key, list):
                # Solana CLI format (array of bytes)
                self.keypair = Keypair.from_secret_key(bytes(secret_key[:32]))
            else:
                logger.error("Invalid wallet format")
                return False
            
            self._loaded = True
            logger.info(f"Keypair loaded: {self.keypair.pubkey()}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load keypair: {e}")
            return False
    
    def get_public_key(self) -> Optional[str]:
        """Get public key (address) of the loaded keypair"""
        if not self._loaded and not self.load_keypair():
            return None
        return str(self.keypair.pubkey())
    
    def is_loaded(self) -> bool:
        """Check if keypair is loaded"""
        return self._loaded and self.keypair is not None


class SolanaClient:
    """Main Solana blockchain client"""
    
    def __init__(self, config: BlockchainConfig = BlockchainConfig):
        """
        Initialize Solana client
        
        Args:
            config: BlockchainConfig instance
        """
        self.config = config
        self.rpc_endpoint = config.get_rpc_endpoint()
        self.ws_endpoint = config.get_ws_endpoint()
        self.program_id = Pubkey(config.PROGRAM_ID) if config.PROGRAM_ID != "YOUR_PROGRAM_ID_HERE" else None
        
        self.client: Optional[AsyncClient] = None
        self.wallet_manager: Optional[SolanaWalletManager] = None
        self.idl: Optional[Dict[str, Any]] = None
        
        logger.info(f"SolanaClient initialized with RPC: {self.rpc_endpoint}")
    
    async def connect(self) -> bool:
        """
        Connect to Solana network
        
        Returns:
            bool: True if successful
        """
        try:
            self.client = AsyncClient(self.rpc_endpoint)
            
            # Test connection
            await self.client.is_connected()
            logger.info("Connected to Solana network")
            
            # Load wallet
            self.wallet_manager = SolanaWalletManager(self.config.WALLET_PATH)
            if not self.wallet_manager.load_keypair():
                logger.warning("Failed to load wallet, continuing without wallet")
            
            # Load IDL
            await self._load_idl()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect to Solana: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Solana network"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Solana network")
    
    async def _load_idl(self) -> bool:
        """
        Load IDL (Interface Definition Language) file
        
        Returns:
            bool: True if successful
        """
        try:
            idl_path = Path(self.config.IDL_PATH)
            if idl_path.exists():
                with open(idl_path, 'r') as f:
                    self.idl = json.load(f)
                logger.info(f"IDL loaded from {idl_path}")
                return True
            else:
                logger.warning(f"IDL file not found at {idl_path}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to load IDL: {e}")
            return False
    
    async def get_account_info(self, account_pubkey: str) -> Optional[Dict[str, Any]]:
        """
        Get account information from blockchain
        
        Args:
            account_pubkey: Public key of the account
        
        Returns:
            Account information or None if not found
        """
        if not self.client:
            logger.error("Client not connected")
            return None
        
        try:
            pubkey = Pubkey(account_pubkey)
            response = await self.client.get_account_info(pubkey)
            
            if response and response.value:
                return {
                    "owner": str(response.value.owner),
                    "lamports": response.value.lamports,
                    "data_length": len(response.value.data) if response.value.data else 0,
                    "executable": response.value.executable,
                    "rent_epoch": response.value.rent_epoch
                }
            return None
        
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return None
    
    async def get_network_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current network status
        
        Returns:
            Network status information
        """
        if not self.client:
            logger.error("Client not connected")
            return None
        
        try:
            # Get network slot
            slot = await self.client.get_slot(Confirmed)
            
            # Get network version
            version = await self.client.get_version()
            
            return {
                "slot": slot,
                "cluster": self.config.NETWORK_CLUSTER,
                "rpc_endpoint": self.rpc_endpoint,
                "version": version.value if version else None
            }
        
        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return None
    
    async def get_balance(self, pubkey: str) -> Optional[float]:
        """
        Get account balance in SOL
        
        Args:
            pubkey: Public key of the account
        
        Returns:
            Balance in SOL or None if error
        """
        if not self.client:
            logger.error("Client not connected")
            return None
        
        try:
            account_pubkey = Pubkey(pubkey)
            response = await self.client.get_balance(account_pubkey, Confirmed)
            
            if response:
                # Convert lamports to SOL (1 SOL = 1,000,000,000 lamports)
                return response.value / 1_000_000_000
            return None
        
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return None
    
    def get_wallet_pubkey(self) -> Optional[str]:
        """Get current wallet public key"""
        if self.wallet_manager:
            return self.wallet_manager.get_public_key()
        return None
    
    async def health_check(self) -> bool:
        """
        Perform health check on Solana connection
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if not self.client:
                return False
            
            # Try to get slot
            slot = await self.client.get_slot(Confirmed)
            return slot is not None
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global client instance
_client_instance: Optional[SolanaClient] = None


async def get_solana_client() -> SolanaClient:
    """
    Get or create global Solana client instance
    
    Returns:
        SolanaClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = SolanaClient()
        if not await _client_instance.connect():
            logger.error("Failed to initialize Solana client")
    
    return _client_instance


async def close_solana_client() -> None:
    """Close and cleanup global Solana client"""
    global _client_instance
    
    if _client_instance:
        await _client_instance.disconnect()
        _client_instance = None