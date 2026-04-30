"""
Blockchain configuration for Solana integration
Handles environment-specific settings for Solana network connections
"""

import os
from enum import Enum
from typing import Optional


class NetworkCluster(Enum):
    """Solana network clusters"""
    DEVNET = "https://api.devnet.solana.com"
    TESTNET = "https://api.testnet.solana.com"
    MAINNET = "https://api.mainnet-beta.solana.com"
    LOCALHOST = "http://localhost:8899"


class BlockchainConfig:
    """Blockchain configuration settings"""
    
    # Network settings
    NETWORK_CLUSTER = os.getenv("SOLANA_NETWORK", "devnet").lower()
    # Map string to NetworkCluster enum
    CLUSTER_MAP = {
        "devnet": NetworkCluster.DEVNET,
        "testnet": NetworkCluster.TESTNET,
        "mainnet": NetworkCluster.MAINNET,
        "localhost": NetworkCluster.LOCALHOST,
    }
    SELECTED_CLUSTER = CLUSTER_MAP.get(NETWORK_CLUSTER, NetworkCluster.DEVNET)
    RPC_ENDPOINT = os.getenv("SOLANA_RPC_ENDPOINT", SELECTED_CLUSTER.value)
    WS_ENDPOINT = os.getenv("SOLANA_WS_ENDPOINT", f"wss://api.{NETWORK_CLUSTER}.solana.com")
        @staticmethod
        def get_explorer_url(address: str, cluster: Optional[str] = None) -> str:
            """
            Generate a Solana Explorer URL for an address on the selected cluster.
            Args:
                address (str): The account or transaction address.
                cluster (str, optional): 'devnet', 'testnet', 'mainnet', etc. Defaults to current config.
            Returns:
                str: Solana Explorer URL.
            """
            cluster = (cluster or BlockchainConfig.NETWORK_CLUSTER).lower()
            return f"https://explorer.solana.com/address/{address}?cluster={cluster}"
    
    # Program configuration
    PROGRAM_ID = os.getenv("SOLANA_PROGRAM_ID", "YOUR_PROGRAM_ID_HERE")
    IDL_PATH = os.getenv("IDL_PATH", "./solana-program/target/idl/intellica_logistics_program.json")
    
    # Wallet configuration
    WALLET_PATH = os.getenv("SOLANA_WALLET_PATH", os.path.expanduser("~/.config/solana/id.json"))
    
    # Transaction settings
    COMMITMENT = os.getenv("SOLANA_COMMITMENT", "confirmed")  # processed, confirmed, finalized
    PREFLIGHT_CHECKS = os.getenv("SOLANA_PREFLIGHT_CHECKS", "true").lower() == "true"
    
    # Feature flags
    USE_BLOCKCHAIN = os.getenv("USE_BLOCKCHAIN", "true").lower() == "true"
    VERIFY_SIGNATURES = os.getenv("VERIFY_SIGNATURES", "true").lower() == "true"
    LOG_BLOCKCHAIN_OPERATIONS = os.getenv("LOG_BLOCKCHAIN_OPERATIONS", "false").lower() == "true"
    
    # Retry settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))  # seconds
    
    # Gas/Fee settings (in lamports)
    PRIORITY_FEE = int(os.getenv("PRIORITY_FEE", "1000"))
    
    @classmethod
    def get_rpc_endpoint(cls) -> str:
        """Get the RPC endpoint based on cluster configuration"""
        cluster_map = {
            "devnet": NetworkCluster.DEVNET.value,
            "testnet": NetworkCluster.TESTNET.value,
            "mainnet": NetworkCluster.MAINNET.value,
            "localhost": NetworkCluster.LOCALHOST.value,
        }
        return cluster_map.get(cls.NETWORK_CLUSTER, NetworkCluster.DEVNET.value)
    
    @classmethod
    def get_ws_endpoint(cls) -> str:
        """Get the WebSocket endpoint based on cluster configuration"""
        cluster_map = {
            "devnet": "wss://api.devnet.solana.com",
            "testnet": "wss://api.testnet.solana.com",
            "mainnet": "wss://api.mainnet-beta.solana.com",
            "localhost": "ws://localhost:8900",
        }
        return cluster_map.get(cls.NETWORK_CLUSTER, "wss://api.devnet.solana.com")
    
    @classmethod
    def validate_config(cls) -> tuple[bool, Optional[str]]:
        """Validate critical configuration settings"""
        if cls.PROGRAM_ID == "YOUR_PROGRAM_ID_HERE":
            return False, "SOLANA_PROGRAM_ID environment variable not set"
        
        if not os.path.exists(cls.IDL_PATH):
            return False, f"IDL file not found at {cls.IDL_PATH}"
        
        return True, None
