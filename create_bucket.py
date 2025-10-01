#!/usr/bin/env python3
"""
Create a valid S3 bucket in Supabase for the Google Drive sync tool.

This script attempts to create a bucket with a valid S3 name using various methods.
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def create_supabase_bucket():
    """Create a valid S3 bucket in Supabase."""
    
    # Load configuration
    try:
        with open('config_mcp.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config_mcp.json not found. Please run this from the project directory.")
        return False
    
    supabase_config = config['supabase']
    
    print("🪣 Creating valid S3 bucket for Google Drive sync...")
    print(f"📍 Endpoint: {supabase_config['endpoint_url']}")
    print(f"🌍 Region: {supabase_config['region']}")
    
    # Try different valid bucket names
    bucket_names = [
        "gdrive-sync",
        "google-drive-backup", 
        "my-drive-files",
        "drive-backup",
        "sync-files"
    ]
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=supabase_config['endpoint_url'],
            region_name=supabase_config['region'],
            aws_access_key_id=supabase_config['access_key_id'],
            aws_secret_access_key=supabase_config['secret_access_key']
        )
        
        print("✅ S3 client created successfully")
        
        # Try to create buckets
        for bucket_name in bucket_names:
            print(f"\n🧪 Trying to create bucket: '{bucket_name}'")
            
            try:
                # Check if bucket already exists
                try:
                    s3_client.head_bucket(Bucket=bucket_name)
                    print(f"✅ Bucket '{bucket_name}' already exists and is accessible!")
                    
                    # Update config with this bucket
                    config['supabase']['bucket_name'] = bucket_name
                    with open('config_mcp.json', 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    print(f"✅ Updated config_mcp.json with bucket: '{bucket_name}'")
                    return True
                    
                except ClientError:
                    # Bucket doesn't exist, try to create it
                    pass
                
                # Try to create the bucket
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ Successfully created bucket: '{bucket_name}'")
                
                # Test upload
                test_key = "test-connection.txt"
                test_content = "Google Drive MCP Sync - Bucket Test"
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content.encode('utf-8'),
                    ContentType='text/plain'
                )
                
                print(f"✅ Upload test successful")
                
                # Clean up test file
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
                
                # Update config
                config['supabase']['bucket_name'] = bucket_name
                with open('config_mcp.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"✅ Updated config_mcp.json with bucket: '{bucket_name}'")
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                print(f"❌ Failed to create '{bucket_name}': {error_code}")
                continue
            except Exception as e:
                print(f"❌ Failed to create '{bucket_name}': {e}")
                continue
        
        print(f"\n❌ Could not create any bucket automatically")
        return False
        
    except Exception as e:
        print(f"❌ S3 client error: {e}")
        return False

def print_manual_instructions():
    """Print manual bucket creation instructions."""
    print(f"\n" + "="*60)
    print("📋 MANUAL BUCKET CREATION INSTRUCTIONS")
    print("="*60)
    print("Since automatic bucket creation didn't work, please create manually:")
    print("")
    print("1. 🌐 Go to your Supabase dashboard:")
    print("   https://supabase.com/dashboard/projects")
    print("")
    print("2. 📁 Select your project: TTS Master")
    print("")
    print("3. 🗂️  Navigate to Storage in the left sidebar")
    print("")
    print("4. ➕ Click 'New bucket' or 'Create bucket'")
    print("")
    print("5. 📝 Enter bucket name: gdrive-sync")
    print("   ⚠️  Important: Use exactly 'gdrive-sync' (no spaces)")
    print("")
    print("6. 🔒 Set bucket as Private (not public)")
    print("")
    print("7. ✅ Click Create")
    print("")
    print("8. 🧪 Then test with: python3 mcp_sync_tool.py --dry-run")
    print("")
    print("Valid bucket names must contain only:")
    print("  ✅ Letters (a-z, A-Z)")
    print("  ✅ Numbers (0-9)")
    print("  ✅ Hyphens (-)")
    print("  ✅ Underscores (_)")
    print("  ✅ Dots (.)")
    print("  ❌ NO SPACES")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Supabase Bucket Creation Tool")
    print("="*40)
    
    success = create_supabase_bucket()
    
    if success:
        print(f"\n🎉 SUCCESS! Your sync tool is ready to use!")
        print(f"\nNext steps:")
        print(f"1. Test: python3 mcp_sync_tool.py --dry-run")
        print(f"2. Sync: python3 mcp_sync_tool.py")
    else:
        print_manual_instructions()
    
    print(f"\n" + "="*40)
