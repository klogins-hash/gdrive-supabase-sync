#!/bin/bash

# Google Drive to Supabase S3 Sync (MCP Version)
# Simple launcher script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Google Drive to Supabase S3 Sync (MCP Version)${NC}"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check if MCP sync tool exists
if [ ! -f "mcp_sync_tool.py" ]; then
    echo -e "${RED}Error: mcp_sync_tool.py not found${NC}"
    exit 1
fi

# Check if config file exists
if [ ! -f "config_mcp.json" ]; then
    echo -e "${YELLOW}Warning: config_mcp.json not found${NC}"
    if [ -f "config_mcp.example.json" ]; then
        echo "Creating config_mcp.json from example..."
        cp config_mcp.example.json config_mcp.json
        echo -e "${YELLOW}Please edit config_mcp.json with your Supabase credentials${NC}"
        echo ""
        echo "Required settings:"
        echo "  - bucket_name: Your Supabase storage bucket name"
        echo "  - access_key_id: Your Supabase S3 access key"
        echo "  - secret_access_key: Your Supabase S3 secret key"
        echo ""
        echo "Then run this script again."
        exit 1
    else
        echo -e "${RED}Error: No configuration file found${NC}"
        exit 1
    fi
fi

# Install dependencies if needed
echo "Checking dependencies..."
python3 -c "import boto3" 2>/dev/null || {
    echo "Installing boto3..."
    python3 -m pip install boto3
}

# Show menu
echo ""
echo "Choose an option:"
echo "1) Dry run (preview what would be synced)"
echo "2) Run sync"
echo "3) Run sync with custom config"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${BLUE}Running dry run...${NC}"
        python3 mcp_sync_tool.py --dry-run
        ;;
    2)
        echo -e "${BLUE}Running sync...${NC}"
        python3 mcp_sync_tool.py
        ;;
    3)
        read -p "Enter config file path: " config_path
        if [ -f "$config_path" ]; then
            echo -e "${BLUE}Running sync with custom config...${NC}"
            python3 mcp_sync_tool.py --config "$config_path"
        else
            echo -e "${RED}Error: Config file not found: $config_path${NC}"
            exit 1
        fi
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Script completed!${NC}"
