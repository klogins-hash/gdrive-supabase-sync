#!/bin/bash

# Google Drive to Supabase S3 Sync Script
# Simple wrapper for the Python sync tool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Google Drive to Supabase S3 Sync${NC}"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check if config file exists
if [ ! -f "config.json" ]; then
    echo -e "${YELLOW}Warning: config.json not found${NC}"
    if [ -f "config.example.json" ]; then
        echo "Creating config.json from example..."
        cp config.example.json config.json
        echo -e "${YELLOW}Please edit config.json with your credentials before running sync${NC}"
        exit 1
    else
        echo -e "${RED}Error: No configuration file found${NC}"
        exit 1
    fi
fi

# Check if credentials file exists
if [ ! -f "credentials.json" ]; then
    echo -e "${YELLOW}Warning: credentials.json not found${NC}"
    echo "Please download Google Drive API credentials and save as credentials.json"
    echo "See README.md for instructions"
    exit 1
fi

# Run the sync
echo "Starting sync..."
python3 gdrive_to_supabase_sync.py "$@"

echo -e "${GREEN}Sync completed!${NC}"
