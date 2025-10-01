#!/usr/bin/env python3
"""
Google Drive to Supabase S3 Sync Tool

This script syncs files from Google Drive to Supabase S3 storage in batches.
It uses the Google Drive API to list and download files, then uploads them
to Supabase S3-compatible storage.
"""

import os
import sys
import json
import logging
import tempfile
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import argparse

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GDriveSupabaseSync:
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the sync tool with configuration."""
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.drive_service = None
        self.s3_client = None
        self.sync_stats = {
            'total_files': 0,
            'synced_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'total_size': 0
        }
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Creating default config...")
            default_config = {
                "supabase": {
                    "endpoint_url": "https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3",
                    "region": "ca-central-1",
                    "bucket_name": "your-bucket-name",
                    "access_key_id": "your-access-key",
                    "secret_access_key": "your-secret-key"
                },
                "google_drive": {
                    "credentials_file": "credentials.json",
                    "token_file": "token.json",
                    "folder_id": null,
                    "query": null,
                    "max_file_size_mb": 100
                },
                "sync": {
                    "batch_size": 10,
                    "delay_between_batches": 1,
                    "skip_existing": true,
                    "preserve_folder_structure": true
                }
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Default config created at {config_file}. Please update with your credentials.")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_file = self.config.get('logging', {}).get('file', 'sync.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def authenticate_google_drive(self):
        """Authenticate with Google Drive API."""
        creds = None
        token_file = self.config['google_drive']['token_file']
        credentials_file = self.config['google_drive']['credentials_file']
        
        # Load existing token
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    self.logger.error(f"Google Drive credentials file not found: {credentials_file}")
                    self.logger.error("Please download credentials.json from Google Cloud Console")
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.logger.info("Google Drive authentication successful")
    
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
            self.s3_client.head_bucket(Bucket=self.config['supabase']['bucket_name'])
            self.logger.info("Supabase S3 connection successful")
            
        except NoCredentialsError:
            self.logger.error("AWS credentials not found")
            sys.exit(1)
        except ClientError as e:
            self.logger.error(f"Failed to connect to Supabase S3: {e}")
            sys.exit(1)
    
    def list_drive_files(self, page_token: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
        """List files from Google Drive."""
        try:
            query_parts = []
            
            # Add folder filter if specified
            if self.config['google_drive'].get('folder_id'):
                query_parts.append(f"'{self.config['google_drive']['folder_id']}' in parents")
            
            # Add custom query if specified
            if self.config['google_drive'].get('query'):
                query_parts.append(self.config['google_drive']['query'])
            
            # Exclude trashed files
            query_parts.append("trashed=false")
            
            query = " and ".join(query_parts) if query_parts else "trashed=false"
            
            results = self.drive_service.files().list(
                q=query,
                pageSize=1000,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, size, mimeType, parents, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            next_page_token = results.get('nextPageToken')
            
            return files, next_page_token
            
        except HttpError as e:
            self.logger.error(f"Failed to list Google Drive files: {e}")
            return [], None
    
    def get_file_path_in_drive(self, file_info: Dict) -> str:
        """Get the full path of a file in Google Drive."""
        if not self.config['sync']['preserve_folder_structure']:
            return file_info['name']
        
        # For now, just return the filename
        # In a full implementation, you'd traverse the parent folders
        return file_info['name']
    
    def download_drive_file(self, file_id: str, file_name: str) -> Optional[str]:
        """Download a file from Google Drive to temporary storage."""
        try:
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"gdrive_sync_{file_id}_{file_name}")
            
            # Download file
            request = self.drive_service.files().get_media(fileId=file_id)
            fh = io.FileIO(temp_file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    self.logger.debug(f"Download progress: {int(status.progress() * 100)}%")
            
            fh.close()
            return temp_file_path
            
        except HttpError as e:
            self.logger.error(f"Failed to download file {file_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {file_name}: {e}")
            return None
    
    def upload_to_supabase(self, local_file_path: str, s3_key: str) -> bool:
        """Upload a file to Supabase S3."""
        try:
            bucket_name = self.config['supabase']['bucket_name']
            
            # Check if file already exists and skip_existing is enabled
            if self.config['sync']['skip_existing']:
                try:
                    self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                    self.logger.info(f"File already exists, skipping: {s3_key}")
                    return True
                except ClientError:
                    pass  # File doesn't exist, continue with upload
            
            # Upload file
            with open(local_file_path, 'rb') as f:
                self.s3_client.upload_fileobj(f, bucket_name, s3_key)
            
            self.logger.info(f"Successfully uploaded: {s3_key}")
            return True
            
        except ClientError as e:
            self.logger.error(f"Failed to upload {s3_key}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error uploading {s3_key}: {e}")
            return False
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    def process_file_batch(self, files: List[Dict]) -> Dict:
        """Process a batch of files."""
        batch_stats = {'synced': 0, 'skipped': 0, 'failed': 0}
        
        for file_info in files:
            file_name = file_info['name']
            file_id = file_info['id']
            file_size = int(file_info.get('size', 0))
            
            # Skip files that are too large
            max_size_mb = self.config['google_drive']['max_file_size_mb']
            if max_size_mb and file_size > max_size_mb * 1024 * 1024:
                self.logger.warning(f"Skipping large file: {file_name} ({file_size / 1024 / 1024:.1f} MB)")
                batch_stats['skipped'] += 1
                continue
            
            # Skip Google Workspace files (they need special handling)
            mime_type = file_info.get('mimeType', '')
            if mime_type.startswith('application/vnd.google-apps'):
                self.logger.warning(f"Skipping Google Workspace file: {file_name}")
                batch_stats['skipped'] += 1
                continue
            
            self.logger.info(f"Processing file: {file_name}")
            
            # Download from Google Drive
            temp_file_path = self.download_drive_file(file_id, file_name)
            if not temp_file_path:
                batch_stats['failed'] += 1
                continue
            
            try:
                # Generate S3 key
                s3_key = self.get_file_path_in_drive(file_info)
                
                # Upload to Supabase
                if self.upload_to_supabase(temp_file_path, s3_key):
                    batch_stats['synced'] += 1
                    self.sync_stats['total_size'] += file_size
                else:
                    batch_stats['failed'] += 1
                    
            finally:
                # Clean up temporary file
                self.cleanup_temp_file(temp_file_path)
        
        return batch_stats
    
    def run_sync(self):
        """Run the complete sync process."""
        self.logger.info("Starting Google Drive to Supabase sync")
        
        # Setup connections
        self.authenticate_google_drive()
        self.setup_s3_client()
        
        # Get all files to sync
        all_files = []
        page_token = None
        
        self.logger.info("Fetching file list from Google Drive...")
        while True:
            files, page_token = self.list_drive_files(page_token)
            all_files.extend(files)
            
            if not page_token:
                break
        
        self.sync_stats['total_files'] = len(all_files)
        self.logger.info(f"Found {len(all_files)} files to process")
        
        if not all_files:
            self.logger.info("No files to sync")
            return
        
        # Process files in batches
        batch_size = self.config['sync']['batch_size']
        delay_between_batches = self.config['sync']['delay_between_batches']
        
        for i in range(0, len(all_files), batch_size):
            batch = all_files[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(all_files) + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            batch_stats = self.process_file_batch(batch)
            
            # Update overall stats
            self.sync_stats['synced_files'] += batch_stats['synced']
            self.sync_stats['skipped_files'] += batch_stats['skipped']
            self.sync_stats['failed_files'] += batch_stats['failed']
            
            self.logger.info(f"Batch {batch_num} completed: {batch_stats['synced']} synced, "
                           f"{batch_stats['skipped']} skipped, {batch_stats['failed']} failed")
            
            # Delay between batches to avoid rate limiting
            if i + batch_size < len(all_files) and delay_between_batches > 0:
                self.logger.info(f"Waiting {delay_between_batches} seconds before next batch...")
                time.sleep(delay_between_batches)
        
        # Print final statistics
        self.print_sync_summary()
    
    def print_sync_summary(self):
        """Print sync summary statistics."""
        stats = self.sync_stats
        total_size_mb = stats['total_size'] / (1024 * 1024)
        
        self.logger.info("=" * 50)
        self.logger.info("SYNC SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total files found: {stats['total_files']}")
        self.logger.info(f"Successfully synced: {stats['synced_files']}")
        self.logger.info(f"Skipped files: {stats['skipped_files']}")
        self.logger.info(f"Failed files: {stats['failed_files']}")
        self.logger.info(f"Total data synced: {total_size_mb:.2f} MB")
        self.logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='Sync files from Google Drive to Supabase S3')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be synced without actually syncing')
    
    args = parser.parse_args()
    
    try:
        sync_tool = GDriveSupabaseSync(args.config)
        
        if args.dry_run:
            print("DRY RUN MODE - No files will be actually synced")
            # TODO: Implement dry run functionality
        
        sync_tool.run_sync()
        
    except KeyboardInterrupt:
        print("\nSync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Sync failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
