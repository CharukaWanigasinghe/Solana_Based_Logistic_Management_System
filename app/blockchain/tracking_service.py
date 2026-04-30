# ============================================================================
# INTELLICA LOGISTICS - Blockchain Tracking Service
# Handles on-chain shipment tracking with hybrid storage model
# ============================================================================

import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime

# In-memory event store (in production, use IPFS or off-chain storage)
TRACKING_EVENTS_DB = {}
GPS_DATA_STORE = {}

class TrackingService:
    """
    Service for managing blockchain-based shipment tracking
    Implements hybrid model: critical events on-chain, detailed data off-chain
    """

    @staticmethod
    def create_shipment_hash(shipment_id: str, product_line: str, quantity: int) -> str:
        """Create hash for shipment creation"""
        data = f"{shipment_id}{product_line}{quantity}{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def create_gps_location_hash(latitude: float, longitude: float, timestamp: int) -> str:
        """Create hash for GPS location data (off-chain data, on-chain hash)"""
        gps_data = f"{latitude}{longitude}{timestamp}"
        return hashlib.sha256(gps_data.encode()).hexdigest()

    @staticmethod
    def create_delivery_confirmation_hash(shipment_id: str, recipient_name: str, proof: str) -> str:
        """Create hash for delivery confirmation (off-chain proof, on-chain hash)"""
        data = f"{shipment_id}{recipient_name}{proof}{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def store_gps_data(shipment_id: str, gps_data: Dict) -> str:
        """
        Store GPS data off-chain and return hash
        In production, store in IPFS or Arweave
        """
        gps_hash = TrackingService.create_gps_location_hash(
            gps_data.get("latitude", 0),
            gps_data.get("longitude", 0),
            int(datetime.now().timestamp())
        )
        GPS_DATA_STORE[gps_hash] = {
            "shipment_id": shipment_id,
            "data": gps_data,
            "timestamp": datetime.now().isoformat()
        }
        return gps_hash

    @staticmethod
    def log_tracking_event(
        shipment_id: str,
        event_type: str,  # "pickup", "in_transit", "delivery"
        location: str,
        gps_data: Optional[Dict] = None,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
    ) -> Dict:
        """
        Log a tracking event with hybrid storage:
        - Event reference stored on-chain
        - Detailed data stored off-chain
        - Hash stored on-chain for verification
        """
        timestamp = int(datetime.now().timestamp())
        
        # Create detailed event data (off-chain)
        event_details = {
            "shipment_id": shipment_id,
            "event_type": event_type,
            "location": location,
            "timestamp": timestamp,
            "gps": gps_data,
            "environmental": {
                "temperature": temperature,
                "humidity": humidity
            }
        }
        
        # Create hash of event details
        event_hash = hashlib.sha256(
            json.dumps(event_details, sort_keys=True).encode()
        ).hexdigest()
        
        # Store event reference (minimal on-chain footprint)
        event_record = {
            "event_hash": event_hash,
            "event_type": event_type,
            "location": location,
            "timestamp": timestamp,
            "full_data": event_details  # In production, stored off-chain with IPFS/Arweave
        }
        
        if shipment_id not in TRACKING_EVENTS_DB:
            TRACKING_EVENTS_DB[shipment_id] = []
        
        TRACKING_EVENTS_DB[shipment_id].append(event_record)
        
        return {
            "event_hash": event_hash,
            "event_type": event_type,
            "location": location,
            "timestamp": timestamp,
            "on_chain_data": {
                "event_hash": event_hash,
                "event_type": event_type,
                "location": location
            }
        }

    @staticmethod
    def verify_gps_data(shipment_id: str, latitude: float, longitude: float, timestamp: int) -> bool:
        """Verify GPS data integrity against stored hash"""
        computed_hash = TrackingService.create_gps_location_hash(latitude, longitude, timestamp)
        # In production, retrieve stored hash from blockchain
        if computed_hash in GPS_DATA_STORE:
            stored_data = GPS_DATA_STORE[computed_hash]
            return stored_data.get("shipment_id") == shipment_id
        return False

    @staticmethod
    def get_shipment_tracking_history(shipment_id: str) -> List[Dict]:
        """Get complete tracking history from events"""
        if shipment_id not in TRACKING_EVENTS_DB:
            return []
        
        history = []
        for event in TRACKING_EVENTS_DB[shipment_id]:
            history.append({
                "event_type": event["event_type"],
                "location": event["location"],
                "timestamp": event["timestamp"],
                "event_hash": event["event_hash"],
                "details": event["full_data"]
            })
        
        return sorted(history, key=lambda x: x["timestamp"])

    @staticmethod
    def create_delivery_proof(
        shipment_id: str,
        recipient_name: str,
        signature: str,
        photo_hash: Optional[str] = None
    ) -> Dict:
        """
        Create delivery confirmation with proof
        - Recipient signature (off-chain)
        - Photo hash (off-chain IPFS storage)
        - Confirmation hash stored on-chain
        """
        delivery_hash = TrackingService.create_delivery_confirmation_hash(
            shipment_id,
            recipient_name,
            signature
        )
        
        delivery_proof = {
            "shipment_id": shipment_id,
            "recipient_name": recipient_name,
            "signature": signature,
            "photo_hash": photo_hash,
            "timestamp": int(datetime.now().timestamp()),
            "delivery_hash": delivery_hash
        }
        
        return {
            "delivery_hash": delivery_hash,
            "proof_data": delivery_proof,
            "on_chain_data": {
                "delivery_hash": delivery_hash,
                "timestamp": delivery_proof["timestamp"]
            }
        }


class HybridStorageModel:
    """
    Hybrid storage implementation:
    1. Critical data on-chain (Solana blockchain)
    2. Large data off-chain (IPFS, Arweave) 
    3. Hashes on-chain for verification
    """

    @staticmethod
    def should_store_on_chain(data_type: str, data_size: int) -> bool:
        """
        Determine if data should be stored on-chain
        
        ON-CHAIN: Small, critical data
        - Shipment creation/status
        - Delivery confirmation
        - Event references
        - Hash values
        
        OFF-CHAIN: Large data
        - GPS coordinates sequences
        - Temperature/humidity readings
        - Photo/video proofs
        - Signature images
        """
        # Events and confirmation hashes go on-chain
        if data_type in ["event_hash", "delivery_hash", "status_change"]:
            return True
        
        # GPS and sensor data (large) go off-chain
        if data_type in ["gps_sequence", "temperature_log", "humidity_log"]:
            return False
        
        # Default: store large data off-chain, small on-chain
        return data_size < 1000  # Arbitrary threshold

    @staticmethod
    def prepare_blockchain_transaction(shipment_id: str, event_type: str) -> Dict:
        """Prepare minimal on-chain transaction"""
        return {
            "instruction": "log_tracking_event",
            "shipment_id": shipment_id,
            "event_type": event_type,
            "timestamp": int(datetime.now().timestamp())
        }

    @staticmethod
    def prepare_off_chain_storage(detailed_data: Dict) -> Dict:
        """Prepare off-chain data for IPFS/Arweave storage"""
        return {
            "data": detailed_data,
            "stored_at": datetime.now().isoformat(),
            "hash": hashlib.sha256(
                json.dumps(detailed_data, sort_keys=True).encode()
            ).hexdigest()
        }
