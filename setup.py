#!/usr/bin/env python3
"""
Setup script for Google Drive to Supabase S3 Sync Tool
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)

def create_config_file():
    """Create configuration file if it doesn't exist."""
    config_file = "config.json"
    if os.path.exists(config_file):
        print(f"✓ Configuration file {config_file} already exists")
        return
    
    if os.path.exists("config.example.json"):
        print(f"Creating {config_file} from example...")
        with open("config.example.json", "r") as src:
            config = json.load(src)
        
        with open(config_file, "w") as dst:
            json.dump(config, dst, indent=2)
        
        print(f"✓ Created {config_file}")
        print(f"⚠️  Please edit {config_file} with your actual credentials")
    else:
        print("Warning: config.example.json not found")

def check_credentials():
    """Check if Google Drive credentials file exists."""
    credentials_file = "credentials.json"
    if os.path.exists(credentials_file):
        print(f"✓ Google Drive credentials file found")
    else:
        print(f"⚠️  Google Drive credentials file not found: {credentials_file}")
        print("   Please download credentials.json from Google Cloud Console")
        print("   See README.md for detailed instructions")

def main():
    """Main setup function."""
    print("=" * 50)
    print("Google Drive to Supabase S3 Sync - Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create config file
    create_config_file()
    
    # Check credentials
    check_credentials()
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Download Google Drive API credentials (credentials.json)")
    print("2. Edit config.json with your Supabase credentials")
    print("3. Run: python gdrive_to_supabase_sync.py")
    print("\nSee README.md for detailed instructions")

if __name__ == "__main__":
    main()
