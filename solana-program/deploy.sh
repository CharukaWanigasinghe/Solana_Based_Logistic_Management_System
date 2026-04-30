#!/bin/bash
# Deployment script for Solana program
# Deploy the compiled program to Solana network

set -e

echo "=========================================="
echo "Deploying Solana Logistics Program"
echo "=========================================="

# Check required tools
if ! command -v solana &> /dev/null; then
    echo "ERROR: Solana CLI is not installed"
    echo "Install Solana CLI: https://docs.solana.com/cli/install-solana-cli-tools"
    exit 1
fi

if ! command -v anchor &> /dev/null; then
    echo "ERROR: Anchor is not installed"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if program is built
if [ ! -f "$SCRIPT_DIR/target/deploy/intellica_logistics_program.so" ]; then
    echo "ERROR: Program not built. Run ./build.sh first"
    exit 1
fi

# Get network from argument
NETWORK=${1:-devnet}

echo "Deploying to: $NETWORK"
echo "Checking balance..."

# Check wallet balance
BALANCE=$(solana balance --url "$NETWORK")
echo "Wallet balance: $BALANCE"

if [ "$NETWORK" == "devnet" ]; then
    echo "Requesting airdrop for devnet..."
    solana airdrop 2 --url devnet || true
elif [ "$NETWORK" == "testnet" ]; then
    echo "Requesting airdrop for testnet..."
    solana airdrop 2 --url testnet || true
fi

echo ""
echo "Deploying program to $NETWORK..."

# Deploy program
PROGRAM_ID=$(solana deploy target/deploy/intellica_logistics_program.so --url "$NETWORK" 2>&1 | grep "Program Id:" | awk '{print $3}')

echo ""
echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo "Program ID: $PROGRAM_ID"
echo "Network: $NETWORK"
echo ""
echo "Next steps:"
echo "1. Update SOLANA_PROGRAM_ID in .env with: $PROGRAM_ID"
echo "2. Update Anchor.toml with the program ID"
echo ""
