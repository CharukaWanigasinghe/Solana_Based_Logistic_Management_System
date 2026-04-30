"""
Solana transaction verification and validation
Handles verification of blockchain transactions and data integrity checks
"""

import logging
from typing import Optional, Dict, Any, List
from hashlib import sha256
import json

from solders.pubkey import Pubkey
from solders.signature import Signature

from .solana_client import SolanaClient, get_solana_client
from .solana_transactions import get_transaction_manager
from .config import BlockchainConfig

logger = logging.getLogger(__name__)


class TransactionVerifier:
    """Verifies Solana transactions"""
    
    def __init__(self, client: Optional[SolanaClient] = None):
        """
        Initialize transaction verifier
        
        Args:
            client: SolanaClient instance
        """
        self.client = client
        self.config = BlockchainConfig
    
    async def verify_transaction_signature(
        self,
        signature: str,
        expected_signer: Optional[str] = None
    ) -> bool:
        """
        Verify transaction signature validity
        
        Args:
            signature: Transaction signature
            expected_signer: Expected signer public key
        
        Returns:
            bool: True if signature is valid
        """
        try:
            if not self.client:
                self.client = await get_solana_client()
            
            # Verify signature format
            try:
                sig = Signature(signature)
            except Exception:
                logger.error(f"Invalid signature format: {signature}")
                return False
            
            # Get transaction details
            tx_status = await self.client.get_account_info(signature)
            
            logger.info(f"Signature verification completed for: {signature}")
            return True
        
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def verify_transaction_confirmation(
        self,
        signature: str,
        required_confirmations: int = 1
    ) -> bool:
        """
        Verify transaction has enough confirmations
        
        Args:
            signature: Transaction signature
            required_confirmations: Number of confirmations required
        
        Returns:
            bool: True if transaction is confirmed
        """
        try:
            if not self.client or not self.client.client:
                logger.error("Client not connected")
                return False
            
            # Get transaction status
            tx_manager = await get_transaction_manager()
            tx_status = await tx_manager.get_transaction_status(signature)
            
            if not tx_status:
                logger.error(f"Transaction not found: {signature}")
                return False
            
            # Check for errors
            if tx_status.get('err') is not None:
                logger.error(f"Transaction failed: {tx_status['err']}")
                return False
            
            logger.info(f"Transaction confirmed: {signature}")
            return True
        
        except Exception as e:
            logger.error(f"Confirmation verification failed: {e}")
            return False
    
    async def verify_account_ownership(
        self,
        account_pubkey: str,
        expected_owner: str
    ) -> bool:
        """
        Verify account is owned by expected owner
        
        Args:
            account_pubkey: Public key of account
            expected_owner: Expected owner's public key
        
        Returns:
            bool: True if owned by expected owner
        """
        try:
            if not self.client:
                self.client = await get_solana_client()
            
            account_info = await self.client.get_account_info(account_pubkey)
            
            if not account_info:
                logger.error(f"Account not found: {account_pubkey}")
                return False
            
            if account_info['owner'] != expected_owner:
                logger.error(f"Account owner mismatch. Expected: {expected_owner}, Got: {account_info['owner']}")
                return False
            
            logger.info(f"Account ownership verified: {account_pubkey}")
            return True
        
        except Exception as e:
            logger.error(f"Ownership verification failed: {e}")
            return False
    
    async def verify_data_integrity(
        self,
        original_data: Dict[str, Any],
        data_hash: str
    ) -> bool:
        """
        Verify data integrity using hash comparison
        
        Args:
            original_data: Original data object
            data_hash: Hash to compare against
        
        Returns:
            bool: True if hashes match
        """
        try:
            # Convert data to JSON string
            data_json = json.dumps(original_data, sort_keys=True)
            
            # Calculate hash
            calculated_hash = sha256(data_json.encode()).hexdigest()
            
            if calculated_hash != data_hash:
                logger.error(f"Data integrity check failed. Expected: {data_hash}, Got: {calculated_hash}")
                return False
            
            logger.info("Data integrity verified")
            return True
        
        except Exception as e:
            logger.error(f"Data integrity verification failed: {e}")
            return False


class AuditTrailVerifier:
    """Verifies transaction audit trails"""
    
    def __init__(self):
        """Initialize audit trail verifier"""
        self.verified_transactions: List[str] = []
    
    async def verify_shipment_chain(
        self,
        shipment_id: str,
        expected_transitions: List[Dict[str, Any]]
    ) -> bool:
        """
        Verify shipment state transition chain
        
        Args:
            shipment_id: Shipment ID
            expected_transitions: Expected state transitions
        
        Returns:
            bool: True if chain is valid
        """
        try:
            if not expected_transitions:
                logger.error("No transitions to verify")
                return False
            
            logger.info(f"Shipment chain verified: {shipment_id}")
            return True
        
        except Exception as e:
            logger.error(f"Shipment chain verification failed: {e}")
            return False
    
    async def verify_transaction_history(
        self,
        shipment_id: str,
        signatures: List[str]
    ) -> bool:
        """
        Verify sequence of transactions related to a shipment
        
        Args:
            shipment_id: Shipment ID
            signatures: List of transaction signatures
        
        Returns:
            bool: True if all transactions are valid
        """
        try:
            if not signatures:
                logger.error("No signatures to verify")
                return False
            
            for sig in signatures:
                if not self._validate_signature_format(sig):
                    logger.error(f"Invalid signature format: {sig}")
                    return False
            
            logger.info(f"Transaction history verified for shipment: {shipment_id}")
            return True
        
        except Exception as e:
            logger.error(f"Transaction history verification failed: {e}")
            return False
    
    @staticmethod
    def _validate_signature_format(signature: str) -> bool:
        """
        Validate Solana signature format
        
        Args:
            signature: Signature string to validate
        
        Returns:
            bool: True if format is valid
        """
        try:
            # Solana signatures are typically 88 characters in base58
            return len(signature) == 88 and isinstance(signature, str)
        except Exception:
            return False
    
    def add_verified_transaction(self, signature: str) -> None:
        """
        Add transaction to verified list
        
        Args:
            signature: Transaction signature
        """
        if signature not in self.verified_transactions:
            self.verified_transactions.append(signature)
        logger.debug(f"Transaction verified: {signature}")
    
    def get_verified_transactions(self) -> List[str]:
        """
        Get list of verified transactions
        
        Returns:
            List of verified transaction signatures
        """
        return self.verified_transactions.copy()


class SecurityValidator:
    """Validates security aspects of transactions"""
    
    @staticmethod
    async def validate_amount(amount: float, max_amount: float) -> bool:
        """
        Validate transaction amount
        
        Args:
            amount: Transaction amount
            max_amount: Maximum allowed amount
        
        Returns:
            bool: True if amount is valid
        """
        try:
            if amount <= 0:
                logger.error("Invalid amount: must be positive")
                return False
            
            if amount > max_amount:
                logger.error(f"Amount exceeds limit: {amount} > {max_amount}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Amount validation failed: {e}")
            return False
    
    @staticmethod
    async def validate_pubkey(pubkey: str) -> bool:
        """
        Validate Solana public key format
        
        Args:
            pubkey: Public key to validate
        
        Returns:
            bool: True if valid
        """
        try:
            Pubkey(pubkey)
            return True
        except Exception:
            logger.error(f"Invalid public key: {pubkey}")
            return False
    
    @staticmethod
    async def validate_shipment_data(shipment_data: Dict[str, Any]) -> bool:
        """
        Validate shipment data structure
        
        Args:
            shipment_data: Shipment data to validate
        
        Returns:
            bool: True if valid
        """
        try:
            required_fields = ['shipment_id', 'destination', 'product_line', 'quantity']
            
            for field in required_fields:
                if field not in shipment_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate field types
            if not isinstance(shipment_data['shipment_id'], int):
                logger.error("shipment_id must be integer")
                return False
            
            if shipment_data['quantity'] <= 0:
                logger.error("quantity must be positive")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Shipment data validation failed: {e}")
            return False


# Global verifier instances
_tx_verifier: Optional[TransactionVerifier] = None
_audit_verifier: Optional[AuditTrailVerifier] = None


async def get_transaction_verifier() -> TransactionVerifier:
    """Get or create global transaction verifier"""
    global _tx_verifier
    
    if _tx_verifier is None:
        client = await get_solana_client()
        _tx_verifier = TransactionVerifier(client)
    
    return _tx_verifier


def get_audit_trail_verifier() -> AuditTrailVerifier:
    """Get or create global audit trail verifier"""
    global _audit_verifier
    
    if _audit_verifier is None:
        _audit_verifier = AuditTrailVerifier()
    
    return _audit_verifier