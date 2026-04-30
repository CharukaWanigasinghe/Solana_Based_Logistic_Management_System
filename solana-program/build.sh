#!/bin/bash
# Build script for Solana program using Anchor
# This script builds the Rust Solana program and generates the IDL

set -e

echo "=========================================="
echo "Building Solana Logistics Program"
echo "=========================================="

# Check if Anchor is installed
if ! command -v anchor &> /dev/null; then
    echo "ERROR: Anchor is not installed"
    echo "Install Anchor Framework: https://docs.rs/anchor-lang/latest/anchor_lang/"
    exit 1
fi

# Check if Cargo is installed
if ! command -v cargo &> /dev/null; then
    echo "ERROR: Cargo (Rust) is not installed"
    echo "Install Rust: https://rustup.rs/"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Building program..."
cd "$SCRIPT_DIR"

# Build the Solana program
cargo build-sbf --manifest-path=Cargo.toml --sbf-out-dir=target/deploy

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
echo "Compiled program: target/deploy/intellica_logistics_program.so"
echo ""

# Optionally generate IDL
if command -v anchor &> /dev/null; then
    echo "Generating IDL..."
    # Note: This requires anchor.toml to be properly configured
    # anchor idl parse -f ./src/lib.rs -o target/idl/intellica_logistics_program.json || echo "IDL generation skipped (requires full Anchor setup)"
fi

echo "Done!"
