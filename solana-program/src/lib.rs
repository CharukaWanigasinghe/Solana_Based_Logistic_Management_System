use anchor_lang::prelude::*;
use std::mem::size_of;

declare_id!("IntLgKwDSxjWsFZRmZnvKVHD2AoJsFViBMagR7tWc2a");

// ============================================================================
// INTELLICA LOGISTICS - Solana On-Chain Shipment Tracking Program
// Implements hybrid storage: critical events on-chain, GPS data off-chain
// On-Chain: Shipment state, status changes, event references
// Off-Chain: GPS coordinates, temperature data, detailed delivery proofs
// Hashes: Verify integrity of off-chain data
// ============================================================================

#[program]
pub mod intellica_logistics {
    use super::*;

    // ===== SHIPMENT MANAGEMENT =====

    /// Initialize a new shipment on-chain
    pub fn create_shipment(
        ctx: Context<CreateShipment>,
        shipment_id: u64,
        destination: String,
        product_line: String,
        quantity: u32,
        gps_data_hash: String,
    ) -> Result<()> {
        let shipment = &mut ctx.accounts.shipment;
        shipment.shipment_id = shipment_id;
        shipment.owner = ctx.accounts.owner.key();
        shipment.current_owner = ctx.accounts.owner.key();
        shipment.destination = destination;
        shipment.product_line = product_line;
        shipment.quantity = quantity;
        shipment.status = ShipmentStatus::Created as u8;
        shipment.gps_data_hash = gps_data_hash;
        shipment.delivery_confirmation_hash = None;
        shipment.is_delivered = false;
        shipment.created_timestamp = Clock::get()?.unix_timestamp as u64;
        shipment.last_updated_timestamp = Clock::get()?.unix_timestamp as u64;
        shipment.event_count = 0;
        shipment.bump = *ctx.bumps.get("shipment").unwrap();

        msg!(
            "✓ Shipment {} created | Status: Created | Product: {} | Qty: {}",
            shipment_id, shipment.product_line, quantity
        );

        Ok(())
    }

    /// Update shipment status and store hash of off-chain GPS data
    pub fn update_shipment_status(
        ctx: Context<UpdateShipment>,
        new_status: u8,
        gps_data_hash: Option<String>,
    ) -> Result<()> {
        let shipment = &mut ctx.accounts.shipment;
        
        let current_status = shipment.status;
        
        // Only allow forward transitions
        match current_status {
            0 => { // Created
                require_eq!(new_status, 1, CustomErrorCode::InvalidStatusTransition); // InTransit
            }
            1 => { // InTransit
                require!(new_status == 2 || new_status == 3, CustomErrorCode::InvalidStatusTransition);
            }
            _ => return Err(CustomErrorCode::InvalidStatusTransition.into()),
        }

        shipment.status = new_status;
        if let Some(hash) = gps_data_hash {
            shipment.gps_data_hash = hash;
        }
        shipment.last_updated_timestamp = Clock::get()?.unix_timestamp as u64;

        msg!(
            "✓ Shipment {} status updated to {} | Timestamp: {}",
            shipment.shipment_id, new_status, shipment.last_updated_timestamp
        );

        Ok(())
    }

    /// Mark shipment as delivered and store delivery confirmation hash
    pub fn confirm_delivery(
        ctx: Context<ConfirmDelivery>,
        delivery_confirmation_hash: String,
    ) -> Result<()> {
        let shipment = &mut ctx.accounts.shipment;
        require!(!shipment.is_delivered, CustomErrorCode::AlreadyDelivered);
        require_eq!(shipment.status, 1, CustomErrorCode::InvalidStatus); // Must be InTransit

        shipment.is_delivered = true;
        shipment.status = 2; // Delivered
        shipment.delivery_confirmation_hash = Some(delivery_confirmation_hash);
        shipment.last_updated_timestamp = Clock::get()?.unix_timestamp as u64;

        msg!(
            "✓ Shipment {} DELIVERED | Confirmation Hash stored | Timestamp: {}",
            shipment.shipment_id, shipment.last_updated_timestamp
        );

        Ok(())
    }

    // ===== TRACKING EVENT LOG =====

    /// Log a tracking event on-chain (critical events only)
    pub fn log_tracking_event(
        ctx: Context<LogTrackingEvent>,
        event_type: u8,
        location: String,
        event_hash: String, // Hash of off-chain event data
    ) -> Result<()> {
        let event = &mut ctx.accounts.event;
        event.shipment_id = ctx.accounts.shipment.shipment_id;
        event.event_type = event_type;
        event.location = location;
        event.event_hash = event_hash;
        event.timestamp = Clock::get()?.unix_timestamp as u64;
        event.event_index = ctx.accounts.shipment.event_count;

        // Update shipment event counter
        ctx.accounts.shipment.event_count += 1;
        ctx.accounts.shipment.last_updated_timestamp = Clock::get()?.unix_timestamp as u64;

        msg!(
            "✓ Event logged for Shipment {} | Type: {} | Location: {} | Event #{}",
            ctx.accounts.shipment.shipment_id, event_type, event.location, event.event_index
        );

        Ok(())
    }

    // ===== HANDOFF & TRANSFER =====

    /// Transfer shipment ownership to another party (handoff)
    pub fn transfer_shipment(
        ctx: Context<TransferShipment>,
        new_owner: Pubkey,
    ) -> Result<()> {
        let shipment = &mut ctx.accounts.shipment;
        shipment.current_owner = new_owner;
        shipment.status = 1; // InTransit
        shipment.last_updated_timestamp = Clock::get()?.unix_timestamp as u64;

        msg!(
            "✓ Shipment {} transferred to new owner | Status: InTransit",
            shipment.shipment_id
        );

        Ok(())
    }

    // ===== VERIFICATION =====

    /// Verify integrity of off-chain GPS data against stored hash
    pub fn verify_gps_data(
        _ctx: Context<VerifyData>,
        computed_hash: String,
    ) -> Result<()> {
        let shipment = &_ctx.accounts.shipment;
        require_eq!(
            shipment.gps_data_hash, computed_hash,
            CustomErrorCode::HashMismatch
        );

        msg!(
            "✓ GPS data verified for Shipment {} | Hash match confirmed",
            shipment.shipment_id
        );

        Ok(())
    }

    /// Verify integrity of delivery confirmation
    pub fn verify_delivery_confirmation(
        _ctx: Context<VerifyData>,
        computed_hash: String,
    ) -> Result<()> {
        let shipment = &_ctx.accounts.shipment;
        require!(shipment.is_delivered, CustomErrorCode::NotDelivered);
        require_eq!(
            shipment.delivery_confirmation_hash.as_ref().unwrap(), 
            &computed_hash,
            CustomErrorCode::HashMismatch
        );

        msg!(
            "✓ Delivery confirmation verified for Shipment {}",
            shipment.shipment_id
        );

        Ok(())
    }
}

// ============================================================================
// ACCOUNTS & DATA STRUCTURES
// ============================================================================

#[derive(Accounts)]
#[instruction(shipment_id: u64)]
pub struct CreateShipment<'info> {
    #[account(
        init,
        payer = owner,
        space = 8 + size_of::<ShipmentAccount>(),
        seeds = [b"shipment", owner.key().as_ref(), shipment_id.to_le_bytes().as_ref()],
        bump
    )]
    pub shipment: Account<'info, ShipmentAccount>,
    
    #[account(mut)]
    pub owner: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateShipment<'info> {
    #[account(mut, has_one = current_owner)]
    pub shipment: Account<'info, ShipmentAccount>,
    
    pub current_owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct ConfirmDelivery<'info> {
    #[account(mut)]
    pub shipment: Account<'info, ShipmentAccount>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct LogTrackingEvent<'info> {
    #[account(mut)]
    pub shipment: Account<'info, ShipmentAccount>,
    
    #[account(
        init,
        payer = payer,
        space = 8 + size_of::<TrackingEvent>(),
        seeds = [b"event", shipment.key().as_ref(), shipment.event_count.to_le_bytes().as_ref()],
        bump
    )]
    pub event: Account<'info, TrackingEvent>,
    
    pub authority: Signer<'info>,
    
    #[account(mut)]
    pub payer: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct TransferShipment<'info> {
    #[account(mut, has_one = current_owner)]
    pub shipment: Account<'info, ShipmentAccount>,
    
    pub current_owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct VerifyData<'info> {
    pub shipment: Account<'info, ShipmentAccount>,
}

// ============================================================================
// SHIPMENT ACCOUNT - STORES CRITICAL ON-CHAIN DATA
// ============================================================================

#[account]
pub struct ShipmentAccount {
    pub shipment_id: u64,                              // Unique ID
    pub owner: Pubkey,                                 // Original owner
    pub current_owner: Pubkey,                         // Current custody holder
    pub destination: String,                           // Destination address
    pub product_line: String,                          // Product category
    pub quantity: u32,                                 // Quantity
    pub status: u8,                                    // Status (0=Created, 1=InTransit, 2=Delivered, 3=Cancelled)
    pub gps_data_hash: String,                         // Hash of off-chain GPS data
    pub delivery_confirmation_hash: Option<String>,    // Hash of delivery proof
    pub is_delivered: bool,                            // Delivery flag
    pub created_timestamp: u64,                        // Creation timestamp
    pub last_updated_timestamp: u64,                   // Last update timestamp
    pub event_count: u32,                              // Number of events logged
    pub bump: u8,                                      // PDA bump seed
}

// ============================================================================
// TRACKING EVENT ACCOUNT - STORES CRITICAL EVENTS ON-CHAIN
// Events are immutable records of shipment state changes
// ============================================================================

#[account]
pub struct TrackingEvent {
    pub shipment_id: u64,                  // Reference to shipment
    pub event_type: u8,                    // Event type (0=Pickup, 1=InTransit, 2=Delivery)
    pub location: String,                  // Location info
    pub event_hash: String,                // Hash of detailed off-chain event data
    pub timestamp: u64,                    // Event timestamp
    pub event_index: u32,                  // Event sequence number
}

// ============================================================================
// ENUMS & ERROR CODES
// ============================================================================

pub enum ShipmentStatus {
    Created = 0,
    InTransit = 1,
    Delivered = 2,
    Cancelled = 3,
}

#[error_code]
pub enum CustomErrorCode {
    #[msg("Invalid status transition")]
    InvalidStatusTransition,
    
    #[msg("Shipment already delivered")]
    AlreadyDelivered,
    
    #[msg("Invalid shipment status")]
    InvalidStatus,
    
    #[msg("Hash mismatch - data integrity violated")]
    HashMismatch,
    
    #[msg("Shipment not yet delivered")]
    NotDelivered,
}
