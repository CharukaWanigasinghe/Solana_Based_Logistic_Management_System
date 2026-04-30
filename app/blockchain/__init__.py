"""
Blockchain module for Solana integration
Provides client, transaction management, and verification services
"""

from .solana_client import (
    SolanaClient,
    SolanaWalletManager,
    get_solana_client,
    close_solana_client
)
from .solana_transactions import (
    SolanaTransactionManager,
    InstructionType,
    get_transaction_manager
)
from .solana_verifier import (
    TransactionVerifier,
    AuditTrailVerifier,
    SecurityValidator,
    get_transaction_verifier,
    get_audit_trail_verifier
)
from .config import BlockchainConfig, NetworkCluster

__all__ = [
    # Client
    "SolanaClient",
    "SolanaWalletManager",
    "get_solana_client",
    "close_solana_client",
    
    # Transactions
    "SolanaTransactionManager",
    "InstructionType",
    "get_transaction_manager",
    
    # Verification
    "TransactionVerifier",
    "AuditTrailVerifier",
    "SecurityValidator",
    "get_transaction_verifier",
    "get_audit_trail_verifier",
    
    # Configuration
    "BlockchainConfig",
    "NetworkCluster",
]
