// ============================================================================
// INTELLICA LOGISTICS - Blockchain Transaction Manager
// Handles Phantom wallet transactions and on-chain shipment management
// ============================================================================

import { Connection, PublicKey, Transaction } from "@solana/web3.js";

const RPC_ENDPOINT = "https://api.devnet.solana.com";
const PROGRAM_ID = new PublicKey("IntLgKwDSxjWsFZRmZnvKVHD2AoJsFViBMagR7tWc2a");

class BlockchainTransactionManager {
  constructor() {
    this.connection = new Connection(RPC_ENDPOINT, "processed");
    this.wallet = null;
    this.isConnected = false;
  }

  /**
   * Check if Phantom wallet is available
   */
  async checkWalletAvailability() {
    const phantomProvider = window.phantom?.solana || window.solana;
    
    if (!phantomProvider) {
      return {
        available: false,
        message: "Phantom wallet not detected. Install from phantom.app"
      };
    }

    return {
      available: true,
      isPhantom: phantomProvider.isPhantom,
      publicKey: phantomProvider.publicKey?.toString()
    };
  }

  /**
   * Get connected wallet
   */
  async getWalletStatus() {
    const phantomProvider = window.phantom?.solana || window.solana;
    
    if (!phantomProvider || !phantomProvider.publicKey) {
      return {
        connected: false,
        message: "Wallet not connected"
      };
    }

    const pubkey = phantomProvider.publicKey.toString();
    const balance = await this.connection.getBalance(
      new PublicKey(pubkey)
    );

    return {
      connected: true,
      publicKey: pubkey,
      balance: balance / 1e9, // Convert lamports to SOL
      network: "Devnet"
    };
  }

  /**
   * Create shipment transaction
   */
  async createShipmentTransaction(shipmentData) {
    try {
      const response = await fetch("/api/blockchain/shipments/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(shipmentData)
      });

      if (!response.ok) {
        throw new Error("Failed to create shipment transaction");
      }

      return await response.json();
    } catch (error) {
      console.error("Shipment creation failed:", error);
      throw error;
    }
  }

  /**
   * Log tracking event
   */
  async logTrackingEvent(shipmentId, eventData) {
    try {
      const response = await fetch(
        `/api/blockchain/shipments/${shipmentId}/track`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(eventData)
        }
      );

      if (!response.ok) {
        throw new Error("Failed to log tracking event");
      }

      return await response.json();
    } catch (error) {
      console.error("Tracking event failed:", error);
      throw error;
    }
  }

  /**
   * Confirm delivery on-chain
   */
  async confirmDelivery(shipmentId, deliveryData) {
    try {
      const response = await fetch(
        `/api/blockchain/shipments/${shipmentId}/confirm-delivery`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(deliveryData)
        }
      );

      if (!response.ok) {
        throw new Error("Failed to confirm delivery");
      }

      return await response.json();
    } catch (error) {
      console.error("Delivery confirmation failed:", error);
      throw error;
    }
  }

  /**
   * Get shipment tracking history
   */
  async getTrackingHistory(shipmentId) {
    try {
      const response = await fetch(
        `/api/blockchain/shipments/${shipmentId}/history`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch tracking history");
      }

      return await response.json();
    } catch (error) {
      console.error("Tracking history fetch failed:", error);
      throw error;
    }
  }

  /**
   * Verify GPS data integrity
   */
  async verifyGPSData(shipmentId, latitude, longitude, timestamp) {
    try {
      const response = await fetch("/api/blockchain/verify/gps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          shipment_id: shipmentId,
          latitude,
          longitude,
          timestamp
        })
      });

      if (!response.ok) {
        throw new Error("GPS verification failed");
      }

      return await response.json();
    } catch (error) {
      console.error("GPS verification failed:", error);
      throw error;
    }
  }

  /**
   * Sign and send transaction (requires Phantom)
   */
  async signAndSendTransaction(transaction) {
    const phantomProvider = window.phantom?.solana || window.solana;

    if (!phantomProvider || !phantomProvider.publicKey) {
      throw new Error("Phantom wallet not connected");
    }

    try {
      // Get recent blockhash
      const { blockhash } = await this.connection.getLatestBlockhash();
      transaction.recentBlockhash = blockhash;
      transaction.feePayer = phantomProvider.publicKey;

      // Sign transaction
      const signedTransaction = await phantomProvider.signTransaction(
        transaction
      );

      // Send transaction
      const signature = await this.connection.sendRawTransaction(
        signedTransaction.serialize()
      );

      // Wait for confirmation
      await this.connection.confirmTransaction(signature);

      return {
        success: true,
        signature,
        message: "Transaction confirmed on-chain"
      };
    } catch (error) {
      console.error("Transaction signing failed:", error);
      throw error;
    }
  }

  /**
   * Get current SOL balance
   */
  async getBalance() {
    const phantomProvider = window.phantom?.solana || window.solana;
    
    if (!phantomProvider || !phantomProvider.publicKey) {
      return 0;
    }

    const balance = await this.connection.getBalance(
      phantomProvider.publicKey
    );
    return balance / 1e9;
  }

  /**
   * Check if user has sufficient funds
   */
  async hasSufficientFunds(requiredSOL = 0.1) {
    const balance = await this.getBalance();
    return balance >= requiredSOL;
  }
}

// Export singleton instance
export const blockchainManager = new BlockchainTransactionManager();

/**
 * UI Helper Functions
 */

export async function displayWalletStatus() {
  const status = await blockchainManager.getWalletStatus();
  const statusElement = document.getElementById("wallet-status");

  if (statusElement) {
    if (status.connected) {
      statusElement.innerHTML = `
        <div class="bg-green-900 text-green-100 p-4 rounded-lg">
          <p><strong>Wallet Connected</strong></p>
          <p>Address: ${status.publicKey.substring(0, 8)}...${status.publicKey.substring(
        -8
      )}</p>
          <p>Balance: ${status.balance.toFixed(4)} SOL</p>
          <p>Network: ${status.network}</p>
        </div>
      `;
    } else {
      statusElement.innerHTML = `
        <div class="bg-red-900 text-red-100 p-4 rounded-lg">
          <p><strong>Wallet Not Connected</strong></p>
          <p>Please connect your Phantom wallet to continue.</p>
        </div>
      `;
    }
  }
}

export async function createShipmentUI(shipmentData) {
  try {
    const result = await blockchainManager.createShipmentTransaction(
      shipmentData
    );

    return {
      success: true,
      data: result,
      message: "Shipment prepared for blockchain deployment"
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: "Failed to prepare shipment"
    };
  }
}

export async function trackShipmentUI(shipmentId, eventData) {
  try {
    const result = await blockchainManager.logTrackingEvent(shipmentId, eventData);

    return {
      success: true,
      data: result,
      message: "Tracking event logged on-chain"
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: "Failed to log tracking event"
    };
  }
}

export async function displayShipmentHistory(shipmentId) {
  try {
    const history = await blockchainManager.getTrackingHistory(shipmentId);

    let historyHTML = `<h3>Tracking History for Shipment ${shipmentId}</h3>`;
    historyHTML += '<table class="w-full border">';
    historyHTML +=
      "<thead><tr><th>Event Type</th><th>Location</th><th>Timestamp</th><th>Hash</th></tr></thead>";
    historyHTML += "<tbody>";

    history.events.forEach((event) => {
      const date = new Date(event.timestamp * 1000).toLocaleString();
      historyHTML += `
        <tr>
          <td>${event.event_type}</td>
          <td>${event.location}</td>
          <td>${date}</td>
          <td>${event.event_hash.substring(0, 16)}...</td>
        </tr>
      `;
    });

    historyHTML += "</tbody></table>";

    return historyHTML;
  } catch (error) {
    console.error("Failed to display history:", error);
    return `<p class="text-red-600">Failed to load tracking history: ${error.message}</p>`;
  }
}

export function formatSOL(lamports) {
  return (lamports / 1e9).toFixed(9);
}

export function formatAddress(address) {
  return `${address.substring(0, 6)}...${address.substring(-6)}`;
}
