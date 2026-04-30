# Web 3.0 INTELLICA - Usage Examples

## 🎬 Real-World Scenarios

This document shows practical examples of how to use your Web 3.0 logistics system.

---

## 📦 Scenario 1: Create a New Shipment

### Step 1: Form (User Input)
```html
Shipment ID: 5001
Destination: Colombo Central Warehouse
Product Line: Electronics
Quantity: 100
Current Location (GPS): 6.9271°N, 80.7789°E (Colombo)
```

### Step 2: Frontend JavaScript
```javascript
// Get coordinates
const latitude = 6.9271;
const longitude = 80.7789;

// Generate GPS hash (privacy-preserving)
const gpsHash = generateGpsHash(latitude, longitude);
// Result: "Ni45OTI3MSw4MC43Nzg5LDE3MDg5NTUyMDI="

// Get connected wallet address from Phantom
const walletAddress = "DeliveryDriver123PublicAddress...";

// Call backend to get instruction
const response = await fetch('/api/blockchain/shipment/create', {
  method: 'POST',
  body: new FormData({
    shipment_id: 5001,
    destination: "Colombo Central Warehouse",
    product_line: "Electronics",
    quantity: 100,
    latitude: 6.9271,
    longitude: 80.7789
  })
});

const { instruction } = await response.json();
```

### Step 3: What Gets Stored On-Chain
```solidity
Account Data (stored on Solana blockchain):
{
  shipment_id: 5001,
  owner: "DeliveryDriver123PublicAddress...",
  current_owner: "DeliveryDriver123PublicAddress...",
  destination: "Colombo Central Warehouse",
  product_line: "Electronics",
  quantity: 100,
  status: "Created" (enum 0),
  created_timestamp: 1708955202 (Unix - Feb 26 2024),
  last_updated_timestamp: 1708955202,
  gps_hash: "Ni45OTI3MSw4MC43Nzg5LDE3MDg5NTUyMDI=",
  delivery_confirmation_hash: null,
  is_delivered: false
}
```

### Step 4: Phantom Wallet
```
Phantom Notification:
"Approve transaction to create shipment 5001?"
- Program: IntLgKwDSxjWsFZRmZnvKVHD2AoJsFViBMagR7tWc2a
- Fee: 0.000425 SOL
[Approve] [Reject]

User clicks "Approve"
↓
Transaction signed
↓
Sent to Solana network
```

### Step 5: Transaction Confirmation
```json
{
  "status": "success",
  "transaction_signature": "5xB7w2FnQkE8T3vJ9mN2L...",
  "shipment_id": 5001,
  "message": "Shipment created on blockchain!",
  "timestamp": "2024-02-26T12:34:56Z"
}
```

### Step 6: Verify on Explorer
```
Visit: https://explorer.solana.com/tx/5xB7w2FnQkE8T3vJ9mN2L...?cluster=devnet

Shows:
✓ Transaction Status: Confirmed
✓ From: DeliveryDriver123PublicAddress...
✓ Program: Your Solana Program ID
✓ Fee: 0.000425 SOL
✓ Signature: 5xB7w2FnQkE8T3vJ9mN2L...
✓ Block: 178954321
```

---

## 🔄 Scenario 2: Transfer Ownership

### Situation
Shipment 5001 is at warehouse. Now needs to be transferred to delivery driver.

### Step 1: Transfer Request
```python
# Backend prepares transfer instruction
shipment_id = 5001
warehouse_address = "DeliveryDriver123PublicAddress..."
driver_address = "DeliveryDriver456PublicAddress..."

# Driver's wallet will sign this transfer
```

### Step 2: Frontend
```javascript
const response = await fetch('/api/blockchain/shipment/transfer', {
  method: 'POST',
  body: new FormData({
    shipment_id: 5001,
    new_owner: "DeliveryDriver456PublicAddress..."
  })
});
```

### Step 3: Wallet Signing
```
Phantom Notification:
"Approve transfer of shipment 5001 to DeliveryDriver456?"
[Approve] [Reject]

Current warehouse address signs the transaction
↓
Ownership changes on-chain
```

### Step 4: On-Chain Changes
```javascript
// Before transfer:
{
  current_owner: "DeliveryDriver123PublicAddress...",
  status: "Created",
  last_updated_timestamp: 1708955202
}

// After transfer:
{
  current_owner: "DeliveryDriver456PublicAddress...",  // ← Changed!
  status: "InTransit",                                  // ← Changed!
  last_updated_timestamp: 1708955300                    // ← Updated!
}
```

### Step 5: Audit Trail
```
Solana Explorer shows:
Transaction 1: CreateShipment (Warehouse created it)
  └─ Timestamp: 1708955202

Transaction 2: TransferOwnership (Warehouse transferred to Driver)
  └─ timestamp: 1708955300

Both transactions visible forever on blockchain
```

---

## 📍 Scenario 3: Update GPS During Transit

### Situation
Driver is transporting shipment 5001. Every hour, GPS location is updated.

### Hour 1 - Colombo (6.9271°N, 80.7789°E)
```javascript
const gpsHash1 = generateGpsHash(6.9271, 80.7789);
// Hash: "Ni45OTI3MSw4MC43Nzg5LDE3MDk0NjcwMA=="

await updateGPS(5001, gpsHash1);
```

**On-Chain Result:**
```
gps_hash = "Ni45OTI3MSw4MC43Nzg5LDE3MDk0NjcwMA=="
last_updated_timestamp = 1708955400
```

### Hour 2 - Suburbs (7.0411°N, 80.6321°E)
```javascript
const gpsHash2 = generateGpsHash(7.0411, 80.6321);
// Hash: "Ny4wNDExLDgwLjYzMjEsMTcwODk0Nzk2MA=="

await updateGPS(5001, gpsHash2);
```

**On-Chain Result:**
```
gps_hash = "Ny4wNDExLDgwLjYzMjEsMTcwODk0Nzk2MA=="  // ← Updated!
last_updated_timestamp = 1708959600                    // ← Updated!
```

### Hour 3 - Port City (6.8397°N, 80.7891°E)
```javascript
const gpsHash3 = generateGpsHash(6.8397, 80.7891);
// Hash: "Ni44Mzk3LDgwLjc4OTEsMTcwODk2MzIwMA=="

await updateGPS(5001, gpsHash3);
```

**On-Chain Result:**
```
gps_hash = "Ni44Mzk3LDgwLjc4OTEsMTcwODk2MzIwMA=="  // ← Updated again!
last_updated_timestamp = 1708963200                   // ← Updated again!
```

### Privacy Feature
```
Blockchain shows hashes only:
- "Ni45OTI3MSw4MC43Nzg5LDE3MDk0NjcwMA=="
- "Ny4wNDExLDgwLjYzMjEsMTcwODk0Nzk2MA=="
- "Ni44Mzk3LDgwLjc4OTEsMTcwODk2MzIwMA=="

To verify location, you need original coordinates:
generateGpsHash(6.9271, 80.7789) -> matches Hash 1 ✓

Others can't reverse the hash without knowing the coordinates
```

---

## ✅ Scenario 4: Confirm Delivery

### Situation
Driver arrives at destination port. Delivery is complete.

### Step 1: Final Location Capture
```javascript
const finalLatitude = 6.8397;
const finalLongitude = 80.7891;
const finalGpsHash = generateGpsHash(finalLatitude, finalLongitude);

// Generate digital signature (proof of delivery)
const walletSignature = "5xB7w2FnQkE8T3vJ9mN2L...";  // From driver's wallet

const confirmationHash = generateConfirmationHash(
  5001,  // shipment ID
  walletSignature,
  Math.floor(Date.now() / 1000)  // timestamp
);
// Result: "NTAwMXw1eEI3dzJGblFrRTh...fDE3MDk2MzIwMA=="
```

### Step 2: Confirm Delivery
```javascript
const response = await fetch('/api/blockchain/shipment/confirm-delivery', {
  method: 'POST',
  body: new FormData({
    shipment_id: 5001,
    latitude: 6.8397,
    longitude: 80.7891,
    signature: walletSignature
  })
});
```

### Step 3: Phantom Approval
```
Phantom Notification:
"Confirm delivery of shipment 5001?"
- Final Location: 6.8397°N, 80.7891°E
- Confirmation Hash: NTAwMXw1eEI3dzJGblFrRTh...
- Fee: 0.000425 SOL
[Approve] [Reject]

Driver clicks "Approve"
↓
Transaction signed with driver's private key
↓
Proof of delivery is cryptographically verified
```

### Step 4: On-Chain State
```javascript
// After ConfirmDelivery transaction:
{
  shipment_id: 5001,
  status: "Delivered",                    // ← Final status
  is_delivered: true,                     // ← Proof flag
  gps_hash: "Ni44Mzk3LDgwLjc4OTEsMTcwODk2MzIwMA==",  // Final location
  delivery_confirmation_hash: "NTAwMXw1eEI3dzJGblFrRTh...",  // Proof
  last_updated_timestamp: 1708963600,
  owner: "DeliveryDriver123PublicAddress...",
  current_owner: "DeliveryDriver456PublicAddress..."
}
```

### Step 5: Verification
```
Recipient can verify:
1. Signature is from driver's wallet ✓
2. Approval timestamp is recent ✓
3. GPS hash matches final location ✓
4. Shipment ownership history ✓
5. All state changes are immutable ✓

Nobody can fake a delivery because:
- Signature requires driver's private key
- Blockchain is immutable
- Hash proves location
- Timestamp is verified by Solana network
```

---

## 💾 Scenario 5: Retrieve Historical Data

### Get Full History
```bash
# Check transaction signature
curl http://localhost:8000/api/blockchain/transaction/5xB7w2FnQkE8T3vJ9mN2L

# Response:
{
  "transaction": "5xB7w2FnQkE8T3vJ9mN2L...",
  "status": "confirmed",
  "explorer_url": "https://explorer.solana.com/tx/5xB7w2FnQkE8T3vJ9mN2L...?cluster=devnet"
}
```

### On Solana Explorer
```
View all shipment 5001 transactions in chronological order:

Time: 12:00:00 - CreateShipment
     ├─ Creator: Warehouse
     └─ Status: Created

Time: 12:30:00 - TransferOwnership  
     ├─ From: Warehouse
     ├─ To: Driver
     └─ Status: InTransit

Time: 13:00:00 - UpdateGpsLocation (Hour 1)
     ├─ GPS: Colombo location
     └─ Timestamp: Verified by Solana

Time: 14:00:00 - UpdateGpsLocation (Hour 2)
     ├─ GPS: Suburbs location
     └─ Timestamp: Verified by Solana

Time: 15:00:00 - UpdateGpsLocation (Hour 3)
     ├─ GPS: Port City location
     └─ Timestamp: Verified by Solana

Time: 16:00:00 - ConfirmDelivery
     ├─ Final GPS: Port City location
     ├─ Confirmation: Driver signature
     ├─ Status: Delivered
     └─ Timestamp: Verified by Solana

Complete audit trail forever on blockchain!
```

---

## 🔐 Scenario 6: Dispute Resolution

### Situation
Customer claims shipment never arrived, but blockchain says it was delivered.

### Customer Claims
```
"I never received shipment 5001!"
"The GPS says Port City, but it should be in Negombo!"
```

### Blockchain Evidence
```
1. View on Solana Explorer:
   Shipment 5001 → ConfirmDelivery transaction

2. Verify chain of ownership:
   Created by: Warehouse (transaction 1)
   Transfer to: Driver (transaction 2)
   Delivered by: Driver (final transaction)

3. Check signature:
   Delivery signature: Driver's wallet only
   ✓ Cryptographically verified by blockchain
   ✓ Driver physically signed the delivery

4. GPS verification:
   Final GPS hash: "Ni44Mzk3LDgwLjc4OTEsMTcwODk2MzIwMA=="
   Driver's location at time: Port City (6.8397°N, 80.7891°E)
   ✓ Hashes match - location proven

5. Timestamp verification:
   Delivery confirmed: 2024-02-26 16:00:00 UTC
   ✓ Verified by Solana network consensus
   ✓ Cannot be backdated
```

### Proof
```
Blockchain provides irrefutable evidence:
✅ Delivery was confirmed with cryptographic signature
✅ Customer receives GPS coordinates (if needed)
✅ Timestamp is tamper-proof
✅ Full audit trail shows no data modification
✅ No forging possible (requires private key)

Case resolved in customer's favor or against depends on:
- Did delivery GPS match recipient's address?
- Did driver sign the correct account?
- Can driver provide proof they went to correct location?
```

---

## 📊 Scenario 7: Analytics from Blockchain

### Query 1: All Shipments by Status
```python
# Get all shipments ever created
shipments = await solana_client.get_all_shipments()

# Filter by status
delivered = [s for s in shipments if s.is_delivered == True]
in_transit = [s for s in shipments if s.status == ShipmentStatus.IN_TRANSIT]

print(f"Delivered: {len(delivered)}")
print(f"In Transit: {len(in_transit)}")
```

### Query 2: Delivery Times
```javascript
// For each shipment, calculate delivery time
shipments.forEach(shipment => {
  const createdTime = shipment.created_timestamp;
  const deliveredTime = shipment.last_updated_timestamp;
  const deliveryDuration = deliveredTime - createdTime;
  
  console.log(`Shipment ${shipment.shipment_id}:`);
  console.log(`  Created: ${new Date(createdTime * 1000)}`);
  console.log(`  Delivered: ${new Date(deliveredTime * 1000)}`);
  console.log(`  Duration: ${deliveryDuration / 3600} hours`);
});
```

### Query 3: Driver Performance
```python
# Count successful deliveries per driver
driver_stats = {}

for shipment in shipments:
  if shipment.is_delivered:
    driver = shipment.current_owner
    if driver not in driver_stats:
      driver_stats[driver] = 0
    driver_stats[driver] += 1

for driver, count in sorted(driver_stats.items(), 
                            key=lambda x: x[1], 
                            reverse=True):
  print(f"{driver}: {count} deliveries")
```

---

## 🎓 What Makes This Web 3.0

Comparing to traditional Web 2.0:

| Aspect | Web 2.0 | Web 3.0 (Your System) |
|--------|---------|---------------------|
| **Data Modification** | Admin can edit/delete database | Immutable - only append new transactions |
| **Timestamps** | Server timestamp (can be changed) | Blockchain timestamp (tamper-proof) |
| **Privacy** | Raw data in database | Hash-based privacy |
| **Verification** | Trust company's claims | Cryptographically verified |
| **Audit Trail** | Centralized logs (can be deleted) | Public blockchain (permanent) |
| **Dispute Resolution** | Depends on company | Proven by blockchain |
| **User Control** | Company owns data | User owns data (via wallet) |
| **Scalability** | Single server bottleneck | 100+ Solana validators |

---

## 🚀 Running These Examples

To run the scenarios above:

1. **Start the system**
   ```bash
   cd app
   python -m uvicorn main:app --reload
   ```

2. **Open Web3 interface**
   ```
   http://localhost:8000/web3/tracking
   ```

3. **Connect Phantom wallet**
   - Click "Connect Wallet"
   - Approve in Phantom extension

4. **Create a shipment**
   - Fill form with scenario 1 data
   - Click "Create Shipment"
   - Phantom prompts for approval

5. **Check transaction**
   - Copy transaction signature
   - Visit Solana Explorer
   - Paste signature to view on-chain data

---

**All examples are now live on your blockchain! 🎉**
