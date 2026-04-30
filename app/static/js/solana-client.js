// Use explicit imports for clarity (requested by frontend)
import { Connection, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction, TransactionInstruction, Keypair } from '@solana/web3.js';
import * as borsh from 'borsh';

// Example wallet/public key to use in frontend interactions
export const SOLANA_ADDRESS = new PublicKey('FUmpfcaHxc6w8e2WJZrGMaWdBoDJF1NshTT7GesQAQft');


// ============================================================================
// INTELLICA LOGISTICS - Web3.js Client Library
// Handles all blockchain interactions for shipment management
// ============================================================================

// Program ID (this would be deployed from your Solana program)
export const PROGRAM_ID = new PublicKey(
  'IntLgKwDSxjWsFZRmZnvKVHD2AoJsFViBMagR7tWc2a' // REPLACE WITH YOUR DEPLOYED PROGRAM ID
);

// Connection to Solana network
let connection: Connection;

// ============================================================================
// Account Structure Definitions (Rust to TypeScript mapping)
// ============================================================================

export interface Shipment {
  shipmentId: bigint;
  owner: web3.PublicKey;
  currentOwner: web3.PublicKey;
  destination: string;
  productLine: string;
  quantity: number;
  status: ShipmentStatus;
  createdTimestamp: bigint;
  lastUpdatedTimestamp: bigint;
  gpsHash: string;
  deliveryConfirmationHash: string | null;
  isDelivered: boolean;
  bump: number;
}

export enum ShipmentStatus {
  Created = 0,
  InTransit = 1,
  Delivered = 2,
  Cancelled = 3,
}

// Borsh schema for deserialization
const shipmentSchema = new Map([
  [
    Shipment,
    {
      kind: 'struct',
      fields: [
        ['shipmentId', 'u64'],
        ['owner', [32]],
        ['currentOwner', [32]],
        ['destination', 'string'],
        ['productLine', 'string'],
        ['quantity', 'u32'],
        ['status', 'u8'],
        ['createdTimestamp', 'i64'],
        ['lastUpdatedTimestamp', 'i64'],
        ['gpsHash', 'string'],
        ['deliveryConfirmationHash', { kind: 'option', type: 'string' }],
        ['isDelivered', 'bool'],
        ['bump', 'u8'],
      ],
    },
  ],
]);

// ============================================================================
// Initialize Connection
// ============================================================================

export function initializeConnection(rpcUrl: string = 'https://api.devnet.solana.com'): void {
  connection = new Connection(rpcUrl, 'processed');
  console.log('✓ Connected to Solana network:', rpcUrl);
}

// ============================================================================
// Instruction Builders
// ============================================================================

export class IntelligaLogisticsClient {
  private programId: web3.PublicKey;
  private connection: web3.Connection;

  constructor(programId: web3.PublicKey, connection: web3.Connection) {
    this.programId = programId;
    this.connection = connection;
  }

  /**
   * Create a new shipment account on-chain
   */
  async createShipment(
    payer: web3.Keypair,
    shipmentId: bigint,
    destination: string,
    productLine: string,
    quantity: number,
    gpsHash: string
  ): Promise<web3.TransactionSignature> {
    // Derive shipment account PDA
    const [shipmentAccount, bump] = await web3.PublicKey.findProgramAddress(
      [Buffer.from('shipment'), Buffer.from(shipmentId.toString())],
      this.programId
    );

    const instruction = new web3.TransactionInstruction({
      keys: [
        { pubkey: shipmentAccount, isSigner: false, isWritable: true },
        { pubkey: payer.publicKey, isSigner: true, isWritable: false },
        { pubkey: web3.SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      programId: this.programId,
      data: Buffer.from(
        borsh.serialize(
          new Map([[Object, { kind: 'struct', fields: [
            ['variant', 'u8'],
            ['shipmentId', 'u64'],
            ['destination', 'string'],
            ['productLine', 'string'],
            ['quantity', 'u32'],
            ['gpsHash', 'string'],
          ]}]]),
          {
            variant: 0, // CreateShipment variant
            shipmentId,
            destination,
            productLine,
            quantity,
            gpsHash,
          }
        )
      ),
    });

    const transaction = new web3.Transaction().add(instruction);
    const signature = await web3.sendAndConfirmTransaction(
      this.connection,
      transaction,
      [payer]
    );

    console.log(
      `✓ Shipment ${shipmentId} created | Tx: ${signature}`
    );
    return signature;
  }

  /**
   * Transfer shipment ownership to new carrier
   */
  async transferOwnership(
    currentOwner: web3.Keypair,
    shipmentId: bigint,
    newOwner: web3.PublicKey
  ): Promise<web3.TransactionSignature> {
    const [shipmentAccount] = await web3.PublicKey.findProgramAddress(
      [Buffer.from('shipment'), Buffer.from(shipmentId.toString())],
      this.programId
    );

    const instruction = new web3.TransactionInstruction({
      keys: [
        { pubkey: shipmentAccount, isSigner: false, isWritable: true },
        { pubkey: currentOwner.publicKey, isSigner: true, isWritable: false },
      ],
      programId: this.programId,
      data: Buffer.from(
        borsh.serialize(
          new Map([[Object, { kind: 'struct', fields: [
            ['variant', 'u8'],
            ['shipmentId', 'u64'],
            ['newOwner', [32]],
          ]}]]),
          {
            variant: 1, // TransferOwnership variant
            shipmentId,
            newOwner: newOwner.toBuffer(),
          }
        )
      ),
    });

    const transaction = new web3.Transaction().add(instruction);
    const signature = await web3.sendAndConfirmTransaction(
      this.connection,
      transaction,
      [currentOwner]
    );

    console.log(
      `✓ Shipment ${shipmentId} transferred to ${newOwner.toBase58()} | Tx: ${signature}`
    );
    return signature;
  }

  /**
   * Confirm delivery with GPS and confirmation hash
   */
  async confirmDelivery(
    currentOwner: web3.Keypair,
    shipmentId: bigint,
    deliveryConfirmationHash: string,
    finalGpsHash: string
  ): Promise<web3.TransactionSignature> {
    const [shipmentAccount] = await web3.PublicKey.findProgramAddress(
      [Buffer.from('shipment'), Buffer.from(shipmentId.toString())],
      this.programId
    );

    const instruction = new web3.TransactionInstruction({
      keys: [
        { pubkey: shipmentAccount, isSigner: false, isWritable: true },
        { pubkey: currentOwner.publicKey, isSigner: true, isWritable: false },
      ],
      programId: this.programId,
      data: Buffer.from(
        borsh.serialize(
          new Map([[Object, { kind: 'struct', fields: [
            ['variant', 'u8'],
            ['shipmentId', 'u64'],
            ['deliveryConfirmationHash', 'string'],
            ['finalGpsHash', 'string'],
          ]}]]),
          {
            variant: 2, // ConfirmDelivery variant
            shipmentId,
            deliveryConfirmationHash,
            finalGpsHash,
          }
        )
      ),
    });

    const transaction = new web3.Transaction().add(instruction);
    const signature = await web3.sendAndConfirmTransaction(
      this.connection,
      transaction,
      [currentOwner]
    );

    console.log(
      `✓ Shipment ${shipmentId} DELIVERED | GPS: ${finalGpsHash} | Tx: ${signature}`
    );
    return signature;
  }

  /**
   * Update GPS location hash during transit
   */
  async updateGpsLocation(
    currentOwner: web3.Keypair,
    shipmentId: bigint,
    newGpsHash: string
  ): Promise<web3.TransactionSignature> {
    const [shipmentAccount] = await web3.PublicKey.findProgramAddress(
      [Buffer.from('shipment'), Buffer.from(shipmentId.toString())],
      this.programId
    );

    const instruction = new web3.TransactionInstruction({
      keys: [
        { pubkey: shipmentAccount, isSigner: false, isWritable: true },
        { pubkey: currentOwner.publicKey, isSigner: true, isWritable: false },
      ],
      programId: this.programId,
      data: Buffer.from(
        borsh.serialize(
          new Map([[Object, { kind: 'struct', fields: [
            ['variant', 'u8'],
            ['shipmentId', 'u64'],
            ['newGpsHash', 'string'],
          ]}]]),
          {
            variant: 3, // UpdateGpsLocation variant
            shipmentId,
            newGpsHash,
          }
        )
      ),
    });

    const transaction = new web3.Transaction().add(instruction);
    const signature = await web3.sendAndConfirmTransaction(
      this.connection,
      transaction,
      [currentOwner]
    );

    console.log(
      `✓ Shipment ${shipmentId} GPS updated to ${newGpsHash} | Tx: ${signature}`
    );
    return signature;
  }

  /**
   * Fetch shipment account data
   */
  async getShipment(shipmentId: bigint): Promise<Shipment | null> {
    const [shipmentAccount] = await web3.PublicKey.findProgramAddress(
      [Buffer.from('shipment'), Buffer.from(shipmentId.toString())],
      this.programId
    );

    const accountInfo = await this.connection.getAccountInfo(shipmentAccount);
    if (!accountInfo) {
      console.error(`Shipment ${shipmentId} not found`);
      return null;
    }

    try {
      const shipmentData = borsh.deserialize(
        shipmentSchema,
        Shipment,
        accountInfo.data
      );
      return shipmentData as any;
    } catch (error) {
      console.error('Error deserializing shipment:', error);
      return null;
    }
  }

  /**
   * Get all shipment accounts
   */
  async getAllShipments(): Promise<Array<{ address: web3.PublicKey; data: Shipment }>> {
    const accounts = await this.connection.getProgramAccounts(this.programId);
    const shipments: Array<{ address: web3.PublicKey; data: Shipment }> = [];

    for (const { pubkey, account } of accounts) {
      try {
        const data = borsh.deserialize(
          shipmentSchema,
          Shipment,
          account.data
        );
        shipments.push({ address: pubkey, data: data as any });
      } catch (error) {
        console.error('Error deserializing account:', error);
      }
    }

    return shipments;
  }
}

// ============================================================================
// Phantom Wallet Integration
// ============================================================================

export async function connectPhantomWallet(): Promise<web3.PublicKey | null> {
  const provider = (window as any).solana;

  if (!provider || !provider.isPhantom) {
    alert('Phantom wallet not found! Install it from https://phantom.app');
    return null;
  }

  try {
    const response = await provider.connect();
    console.log('✓ Connected to Phantom wallet:', response.publicKey.toBase58());
    return response.publicKey;
  } catch (error) {
    console.error('Failed to connect Phantom wallet:', error);
    return null;
  }
}

export function getPhantomProvider(): any {
  return (window as any).solana;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Generate GPS hash from coordinates
 */
export function generateGpsHash(latitude: number, longitude: number, timestamp: number): string {
  const input = `${latitude},${longitude},${timestamp}`;
  return Buffer.from(input).toString('base64');
}

/**
 * Generate delivery confirmation hash from data
 */
export function generateConfirmationHash(
  shipmentId: bigint,
  signature: string,
  timestamp: number
): string {
  const input = `${shipmentId}|${signature}|${timestamp}`;
  return Buffer.from(input).toString('base64');
}

/**
 * Format shipment status for display
 */
export function formatShipmentStatus(status: ShipmentStatus): string {
  switch (status) {
    case ShipmentStatus.Created:
      return '📦 Created';
    case ShipmentStatus.InTransit:
      return '🚚 In Transit';
    case ShipmentStatus.Delivered:
      return '✅ Delivered';
    case ShipmentStatus.Cancelled:
      return '❌ Cancelled';
    default:
      return 'Unknown';
  }
}
