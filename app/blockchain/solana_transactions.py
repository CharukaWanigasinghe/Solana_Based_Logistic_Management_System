"""
Solana transaction management
Handles creating, signing, and submitting transactions to the Solana network
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

from .solana_client import SolanaClient, get_solana_client
from .config import BlockchainConfig

logger = logging.getLogger(__name__)


class InstructionType(Enum):
    """Logistics instruction types"""
    CREATE_SHIPMENT = 0
    TRANSFER_OWNERSHIP = 1
    CONFIRM_DELIVERY = 2
    UPDATE_GPS = 3


@dataclass
class ShipmentInstruction:
    """Shipment creation instruction data"""
    shipment_id: int
    destination: str
    product_line: str
    quantity: int
    gps_hash: str


@dataclass
class TransferOwnershipInstruction:
    """Ownership transfer instruction data"""
    shipment_id: int
    new_owner: str


@dataclass
class ConfirmDeliveryInstruction:
    """Delivery confirmation instruction data"""
    shipment_id: int
    delivery_confirmation_hash: str
    final_gps_hash: str


@dataclass
class UpdateGpsInstruction:
    """GPS update instruction data"""
    shipment_id: int
    new_gps_hash: str


class SolanaTransactionManager:
    """Manages Solana transactions"""
    
    def __init__(self, client: Optional[SolanaClient] = None):
        """
        Initialize transaction manager
        
        Args:
            client: SolanaClient instance
        """
        self.client = client
        self.config = BlockchainConfig
    
    async def create_transaction(
        self,
        instructions: List[Instruction],
        payer_pubkey: str,
        recent_blockhash: Optional[str] = None
    ) -> Optional[Transaction]:
        """
        Create a transaction with given instructions
        
        Args:
            instructions: List of instructions to include
            payer_pubkey: Public key of transaction payer
            recent_blockhash: Recent blockhash for transaction
        
        Returns:
            Signed transaction or None if error
        """
        try:
            if not self.client:
                self.client = await get_solana_client()
            
            # Get recent blockhash if not provided
            if not recent_blockhash:
                if not self.client.client:
                    logger.error("Client not connected")
                    return None
                
                response = await self.client.client.get_latest_blockhash()
                recent_blockhash = str(response.value.blockhash)
            
            # Create message
            payer = Pubkey(payer_pubkey)
            message = Message.new_with_blockhash(
                instructions,
                [payer],
                recent_blockhash
            )
            
            # Create transaction
            tx = Transaction([self.client.wallet_manager.keypair], message, recent_blockhash)
            
            logger.info(f"Transaction created: {len(instructions)} instructions")
            return tx
        
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            return None
    
    async def submit_transaction(
        self,
        transaction: Transaction,
        skip_preflight: bool = False
    ) -> Optional[str]:
        """
        Submit transaction to Solana network
        
        Args:
            transaction: Transaction to submit
            skip_preflight: Whether to skip preflight checks
        
        Returns:
            Transaction signature or None if error
        """
        try:
            if not self.client or not self.client.client:
                logger.error("Client not connected")
                return None
            
            # Submit transaction
            opts = TxOpts(skip_preflight=skip_preflight, preflight_commitment=Confirmed)
            signature = await self.client.client.send_transaction(transaction, opts=opts)
            
            logger.info(f"Transaction submitted: {signature}")
            return str(signature)
        
        except Exception as e:
            logger.error(f"Failed to submit transaction: {e}")
            return None
    
    async def get_transaction_status(self, signature: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction status
        
        Args:
            signature: Transaction signature
        
        Returns:
            Transaction status information
        """
        try:
            if not self.client or not self.client.client:
                logger.error("Client not connected")
                return None
            
            response = await self.client.client.get_transaction(
                signature,
                max_supported_transaction_version=0
            )
            
            if response and response.value:
                return {
                    "signature": signature,
                    "slot": response.value.slot,
                    "block_time": response.value.block_time,
                    "err": response.value.transaction.meta.err if response.value.transaction.meta else None
                }
            return None
        
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return None
    
    async def confirm_transaction(
        self,
        signature: str,
        max_wait_time: int = 30
    ) -> bool:
        """
        Wait for transaction confirmation
        
        Args:
            signature: Transaction signature
            max_wait_time: Maximum time to wait in seconds
        
        Returns:
            bool: True if confirmed, False otherwise
        """
        try:
            if not self.client or not self.client.client:
                logger.error("Client not connected")
                return False
            
            # Wait for confirmation
            await self.client.client.confirm_transaction(signature, Confirmed)
            logger.info(f"Transaction confirmed: {signature}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to confirm transaction: {e}")
            return False
    
    async def estimate_transaction_fee(
        self,
        instructions: List[Instruction],
        payer_pubkey: str
    ) -> Optional[float]:
        """
        Estimate transaction fee in SOL
        
        Args:
            instructions: List of instructions
            payer_pubkey: Public key of payer
        
        Returns:
            Estimated fee in SOL or None if error
        """
        try:
            if not self.client or not self.client.client:
                logger.error("Client not connected")
                return None
            
            # Get priority fees (in lamports)
            priority_fee = self.config.PRIORITY_FEE
            
            # Base fee is typically 5000 lamports per signature
            base_fee = 5000
            num_signatures = 1
            
            total_fee_lamports = base_fee * num_signatures + priority_fee
            
            # Convert to SOL
            return total_fee_lamports / 1_000_000_000
        
        except Exception as e:
            logger.error(f"Failed to estimate fee: {e}")
            return None
    
    @staticmethod
    def create_instruction(
        program_id: str,
        instruction_type: InstructionType,
        accounts: List[Dict[str, Any]],
        data: bytes
    ) -> Optional[Instruction]:
        """
        Create a program instruction
        
        Args:
            program_id: Program ID
            instruction_type: Type of instruction
            accounts: List of account metadata
            data: Instruction data
        
        Returns:
            Instruction or None if error
        """
        try:
            program_pubkey = Pubkey(program_id)
            
            # Create account metas
            account_metas = []
            for account in accounts:
                meta = AccountMeta(
                    pubkey=Pubkey(account['pubkey']),
                    is_signer=account.get('is_signer', False),
                    is_writable=account.get('is_writable', False)
                )
                account_metas.append(meta)
            
            # Create instruction
            instruction = Instruction(
                program_id=program_pubkey,
                accounts=account_metas,
                data=data
            )
            
            return instruction
        
        except Exception as e:
            logger.error(f"Failed to create instruction: {e}")
            return None


# Global transaction manager instance
_tx_manager: Optional[SolanaTransactionManager] = None


async def get_transaction_manager() -> SolanaTransactionManager:
    """
    Get or create global transaction manager
    
    Returns:
        SolanaTransactionManager instance
    """
    global _tx_manager
    
    if _tx_manager is None:
        client = await get_solana_client()
        _tx_manager = SolanaTransactionManager(client)
    
    return _tx_manager