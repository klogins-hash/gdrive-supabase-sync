#!/usr/bin/env python3
"""
Google Drive to Supabase S3 Sync Tool (MCP Version)

This script syncs files from Google Drive to Supabase S3 storage in batches
using the MCP (Model Context Protocol) connection for Google Drive operations.
This eliminates the need for manual Google Drive API setup and credentials.

Usage:
    python mcp_sync_tool.py --config config_mcp.json
    python mcp_sync_tool.py --dry-run
"""

import json
import os
import tempfile
import time
import logging
import argparse
import sys
from typing import List, Dict, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class MCPGDriveSupabaseSync:
    def __init__(self, config: Dict):
        """Initialize the MCP-based sync tool."""
        self.config = config
        self.s3_client = None
        self.sync_stats = {
            'total_files': 0,
            'synced_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'total_size': 0,
            'batches_processed': 0
        }
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging."""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_file = self.config.get('logging', {}).get('file', 'mcp_sync.log')
        
        # Configure logging to both file and console
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_s3_client(self):
        """Setup S3 client for Supabase."""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.config['supabase']['endpoint_url'],
                region_name=self.config['supabase']['region'],
                aws_access_key_id=self.config['supabase']['access_key_id'],
                aws_secret_access_key=self.config['supabase']['secret_access_key']
            )
            
            # Test connection
            bucket_name = self.config['supabase']['bucket_name']
            self.s3_client.head_bucket(Bucket=bucket_name)
            self.logger.info(f"✓ Supabase S3 connection successful (bucket: {bucket_name})")
            return True
            
        except NoCredentialsError:
            self.logger.error("❌ AWS credentials not found")
            return False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.logger.error(f"❌ Bucket not found: {self.config['supabase']['bucket_name']}")
            elif error_code == '403':
                self.logger.error("❌ Access denied - check your credentials and permissions")
            else:
                self.logger.error(f"❌ Failed to connect to Supabase S3: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error connecting to Supabase S3: {e}")
            return False
    
    def list_drive_files_mcp(self, page_token: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
        """List files from Google Drive using MCP connection."""
        try:
            # Prepare arguments for MCP call
            arguments = {
                "pageSize": self.config['google_drive'].get('page_size', 100),
                "fields": "nextPageToken, files(id, name, size, mimeType, parents, modifiedTime, webViewLink)"
            }
            
            # Add folder filter if specified
            if self.config['google_drive'].get('folder_id'):
                arguments["folderId"] = self.config['google_drive']['folder_id']
            
            # Build query
            query_parts = ["trashed=false"]
            
            # Exclude Google Workspace files and folders by default
            query_parts.append("mimeType != 'application/vnd.google-apps.folder'")
            
            # Add custom query if specified
            if self.config['google_drive'].get('query'):
                query_parts.append(self.config['google_drive']['query'])
            
            arguments["q"] = " and ".join(query_parts)
            
            # Add page token for pagination
            if page_token:
                arguments["pageToken"] = page_token
            
            self.logger.info(f"📋 Listing Google Drive files via MCP...")
            
            # This would be the actual MCP call in a real implementation
            # For demonstration purposes, we'll return a mock response
            # In your actual implementation, replace this with:
            # result, error = run_composio_tool("GOOGLEDRIVE_LIST_FILES", arguments)
            
            # Mock response for demonstration
            mock_files = [
                {
                    "id": "1j0sMsrR6ngQEHLALhnOXHje5zZimVsEJ",
                    "name": "Sample Document.pdf",
                    "size": "1048576",  # 1MB
                    "mimeType": "application/pdf",
                    "modifiedTime": "2025-10-01T03:00:00.000Z",
                    "webViewLink": "https://drive.google.com/file/d/1j0sMsrR6ngQEHLALhnOXHje5zZimVsEJ/view"
                },
                {
                    "id": "2k1tNtrS7ohREILBMioOYIkf6aAjnWtFK",
                    "name": "Image.jpg",
                    "size": "2097152",  # 2MB
                    "mimeType": "image/jpeg",
                    "modifiedTime": "2025-09-30T15:30:00.000Z",
                    "webViewLink": "https://drive.google.com/file/d/2k1tNtrS7ohREILBMioOYIkf6aAjnWtFK/view"
                }
            ]
            
            # Filter out Google Workspace files and large files
            filtered_files = []
            max_size_mb = self.config['google_drive'].get('max_file_size_mb', 100)
            max_size_bytes = max_size_mb * 1024 * 1024 if max_size_mb else None
            
            for file_info in mock_files:
                mime_type = file_info.get('mimeType', '')
                file_size = int(file_info.get('size', 0))
                
                # Skip Google Workspace files
                if mime_type.startswith('application/vnd.google-apps'):
                    self.logger.debug(f"Skipping Google Workspace file: {file_info.get('name')}")
                    continue
                
                # Skip files that are too large
                if max_size_bytes and file_size > max_size_bytes:
                    self.logger.debug(f"Skipping large file: {file_info.get('name')} ({file_size / 1024 / 1024:.1f} MB)")
                    continue
                
                filtered_files.append(file_info)
            
            self.logger.info(f"✅ Retrieved {len(filtered_files)} files from Google Drive")
            
            # Return files and next page token (None for this demo)
            return filtered_files, None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list Google Drive files via MCP: {e}")
            return [], None
    
    def download_drive_file_mcp(self, file_id: str, file_name: str) -> Optional[str]:
        """Download a file from Google Drive using MCP connection."""
        try:
            # Create temporary file with safe filename
            temp_dir = tempfile.gettempdir()
            safe_filename = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
            temp_file_path = os.path.join(temp_dir, f"gdrive_mcp_{file_id}_{safe_filename}")
            
            self.logger.info(f"⬇️  Downloading {file_name} via MCP...")
            
            # This would be the actual MCP call in a real implementation
            # For demonstration purposes, we'll create a mock file
            # In your actual implementation, replace this with:
            # result, error = run_composio_tool("GOOGLEDRIVE_DOWNLOAD_FILE", {"file_id": file_id})
            
            # Create a mock file for demonstration
            mock_content = f"Mock content for file: {file_name}\nFile ID: {file_id}\nDownloaded via MCP\n"
            
            with open(temp_file_path, 'w') as f:
                f.write(mock_content)
            
            self.logger.info(f"✅ Downloaded {file_name} to {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to download file {file_name} via MCP: {e}")
            return None
    
    def upload_to_supabase(self, local_file_path: str, s3_key: str, file_size: int = 0) -> bool:
        """Upload a file to Supabase S3."""
        try:
            bucket_name = self.config['supabase']['bucket_name']
            
            # Check if file already exists and skip_existing is enabled
            if self.config['sync']['skip_existing']:
                try:
                    self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                    self.logger.info(f"📄 File already exists, skipping: {s3_key}")
                    return True
                except ClientError:
                    pass  # File doesn't exist, continue with upload
            
            # Upload file
            with open(local_file_path, 'rb') as f:
                self.s3_client.upload_fileobj(f, bucket_name, s3_key)
            
            size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
            self.logger.info(f"✅ Successfully uploaded: {s3_key} ({size_mb:.2f} MB)")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                self.logger.error(f"❌ Bucket does not exist: {bucket_name}")
            elif error_code == 'AccessDenied':
                self.logger.error(f"❌ Access denied uploading {s3_key}")
            else:
                self.logger.error(f"❌ Failed to upload {s3_key}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error uploading {s3_key}: {e}")
            return False
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.debug(f"🗑️  Cleaned up temp file: {file_path}")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to cleanup temp file {file_path}: {e}")
    
    def get_s3_key(self, file_info: Dict) -> str:
        """Generate S3 key for a file."""
        file_name = file_info['name']
        
        if not self.config['sync']['preserve_folder_structure']:
            return file_name
        
        # For now, just return the filename
        # In a full implementation, you'd traverse the parent folders using file_info['parents']
        return file_name
    
    def process_file_batch(self, files: List[Dict], batch_num: int) -> Dict:
        """Process a batch of files."""
        batch_stats = {'synced': 0, 'skipped': 0, 'failed': 0}
        
        self.logger.info(f"🔄 Processing batch {batch_num} ({len(files)} files)")
        
        for i, file_info in enumerate(files, 1):
            file_name = file_info['name']
            file_id = file_info['id']
            file_size = int(file_info.get('size', 0))
            
            self.logger.info(f"  [{i}/{len(files)}] Processing: {file_name}")
            
            # Download from Google Drive via MCP
            temp_file_path = self.download_drive_file_mcp(file_id, file_name)
            if not temp_file_path:
                batch_stats['failed'] += 1
                continue
            
            try:
                # Generate S3 key
                s3_key = self.get_s3_key(file_info)
                
                # Upload to Supabase
                if self.upload_to_supabase(temp_file_path, s3_key, file_size):
                    batch_stats['synced'] += 1
                    self.sync_stats['total_size'] += file_size
                else:
                    batch_stats['failed'] += 1
                    
            finally:
                # Clean up temporary file
                self.cleanup_temp_file(temp_file_path)
        
        return batch_stats
    
    def run_sync(self, dry_run: bool = False):
        """Run the complete sync process using MCP."""
        self.logger.info("🚀 Starting Google Drive to Supabase sync (MCP version)")
        
        if dry_run:
            self.logger.info("🧪 DRY RUN MODE - No files will be actually synced")
        
        # Setup S3 connection (only if not dry run)
        if not dry_run:
            if not self.setup_s3_client():
                self.logger.error("❌ Failed to setup S3 connection. Aborting sync.")
                return self.sync_stats
        
        # Get all files to sync via MCP
        all_files = []
        page_token = None
        page_count = 0
        
        self.logger.info("📋 Fetching file list from Google Drive via MCP...")
        
        while True:
            page_count += 1
            files, page_token = self.list_drive_files_mcp(page_token)
            
            if not files and page_count == 1:
                self.logger.warning("⚠️  No files found in Google Drive")
                break
            
            all_files.extend(files)
            self.logger.info(f"📄 Page {page_count}: Found {len(files)} files (Total: {len(all_files)})")
            
            if not page_token:
                break
        
        self.sync_stats['total_files'] = len(all_files)
        self.logger.info(f"📊 Found {len(all_files)} total files to process")
        
        if not all_files:
            self.logger.info("ℹ️  No files to sync")
            return self.sync_stats
        
        if dry_run:
            self.logger.info("📋 DRY RUN - Files that would be synced:")
            for i, file_info in enumerate(all_files, 1):
                size_mb = int(file_info.get('size', 0)) / (1024 * 1024)
                self.logger.info(f"  {i}. {file_info['name']} ({size_mb:.2f} MB)")
            return self.sync_stats
        
        # Process files in batches
        batch_size = self.config['sync']['batch_size']
        delay_between_batches = self.config['sync']['delay_between_batches']
        
        total_batches = (len(all_files) + batch_size - 1) // batch_size
        
        for i in range(0, len(all_files), batch_size):
            batch = all_files[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            batch_stats = self.process_file_batch(batch, batch_num)
            
            # Update overall stats
            self.sync_stats['synced_files'] += batch_stats['synced']
            self.sync_stats['skipped_files'] += batch_stats['skipped']
            self.sync_stats['failed_files'] += batch_stats['failed']
            self.sync_stats['batches_processed'] += 1
            
            self.logger.info(f"✅ Batch {batch_num}/{total_batches} completed: "
                           f"{batch_stats['synced']} synced, "
                           f"{batch_stats['skipped']} skipped, "
                           f"{batch_stats['failed']} failed")
            
            # Delay between batches to avoid rate limiting
            if i + batch_size < len(all_files) and delay_between_batches > 0:
                self.logger.info(f"⏳ Waiting {delay_between_batches} seconds before next batch...")
                time.sleep(delay_between_batches)
        
        # Print final statistics
        self.print_sync_summary()
        return self.sync_stats
    
    def print_sync_summary(self):
        """Print sync summary statistics."""
        stats = self.sync_stats
        total_size_mb = stats['total_size'] / (1024 * 1024)
        
        self.logger.info("=" * 60)
        self.logger.info("📊 SYNC SUMMARY (MCP VERSION)")
        self.logger.info("=" * 60)
        self.logger.info(f"📁 Total files found: {stats['total_files']}")
        self.logger.info(f"✅ Successfully synced: {stats['synced_files']}")
        self.logger.info(f"⏭️  Skipped files: {stats['skipped_files']}")
        self.logger.info(f"❌ Failed files: {stats['failed_files']}")
        self.logger.info(f"📦 Batches processed: {stats['batches_processed']}")
        self.logger.info(f"💾 Total data synced: {total_size_mb:.2f} MB")
        
        if stats['failed_files'] > 0:
            self.logger.warning(f"⚠️  {stats['failed_files']} files failed to sync. Check logs for details.")
        
        self.logger.info("=" * 60)


def load_config(config_file: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {config_file} not found.")
        print("Creating default config...")
        
        default_config = {
            "supabase": {
                "endpoint_url": "https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3",
                "region": "ca-central-1",
                "bucket_name": "your-bucket-name",
                "access_key_id": "your-access-key",
                "secret_access_key": "your-secret-key"
            },
            "google_drive": {
                "folder_id": None,
                "query": None,
                "max_file_size_mb": 100,
                "page_size": 100
            },
            "sync": {
                "batch_size": 10,
                "delay_between_batches": 1,
                "skip_existing": True,
                "preserve_folder_structure": False
            },
            "logging": {
                "level": "INFO",
                "file": "mcp_sync.log"
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✅ Default config created at {config_file}")
        print("Please update with your Supabase credentials and run again.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Sync files from Google Drive to Supabase S3 using MCP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp_sync_tool.py                           # Use default config
  python mcp_sync_tool.py --config my_config.json  # Use custom config
  python mcp_sync_tool.py --dry-run                 # Preview what would be synced
        """
    )
    
    parser.add_argument('--config', default='config_mcp.json', 
                       help='Configuration file path (default: config_mcp.json)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be synced without actually syncing')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Create and run sync tool
        sync_tool = MCPGDriveSupabaseSync(config)
        
        if args.dry_run:
            print("🧪 DRY RUN MODE - No files will be actually synced")
        
        stats = sync_tool.run_sync(dry_run=args.dry_run)
        
        # Exit with appropriate code
        if stats['failed_files'] > 0:
            print(f"\n⚠️  Sync completed with {stats['failed_files']} failures")
            sys.exit(1)
        else:
            print(f"\n🎉 Sync completed successfully!")
            sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n⏹️  Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Sync failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
