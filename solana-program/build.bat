@echo off
REM Build script for Solana program on Windows
REM This script builds the Rust Solana program

echo.
echo ==========================================
echo Building Solana Logistics Program
echo ==========================================
echo.

REM Check if Cargo is installed
where cargo >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Cargo (Rust) is not installed
    echo Install Rust: https://rustup.rs/
    exit /b 1
)

REM Check if Anchor is installed
where anchor >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Anchor is not installed or not in PATH
    echo Install Anchor: https://book.anchor-lang.com/getting_started/installation.html
)

echo Building program...

REM Navigate to script directory
cd /d "%~dp0"

REM Build the program
cargo build-sbf --manifest-path=Cargo.toml --sbf-out-dir=target/deploy

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo Build completed successfully!
    echo ==========================================
    echo.
    echo Compiled program: target\deploy\intellica_logistics_program.so
    echo.
) else (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)
