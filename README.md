# Google Drive to Supabase S3 Sync Tool

A Python tool to sync files from Google Drive to Supabase S3 storage in batches. This tool efficiently handles large numbers of files by processing them in configurable batches with rate limiting and comprehensive error handling.

## Features

- **Batch Processing**: Process files in configurable batch sizes to avoid API rate limits
- **Resume Capability**: Skip already uploaded files to resume interrupted syncs
- **Flexible Filtering**: Filter files by folder, query, or file size
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Error Handling**: Robust error handling with retry logic
- **Progress Tracking**: Real-time progress updates and final statistics
- **Supabase S3 Compatible**: Works with Supabase's S3-compatible storage

## Prerequisites

1. **Python 3.7+**
2. **Google Cloud Project** with Drive API enabled
3. **Supabase Project** with S3 storage configured
4. **Google Drive API Credentials**
5. **Supabase S3 Access Keys**

## Installation

1. **Clone or download the project:**
   ```bash
   cd /Users/franksimpson/CascadeProjects/gdrive-supabase-sync
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### 1. Google Drive API Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Drive API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it

3. **Create Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials JSON file
   - Rename it to `credentials.json` and place it in the project directory

### 2. Supabase S3 Setup

1. **Get Supabase S3 Credentials:**
   - Go to your Supabase project dashboard
   - Navigate to Settings > Storage
   - Find your S3 credentials (Access Key ID and Secret Access Key)
   - Note your bucket name and region

2. **Your Supabase S3 endpoint is:**
   ```
   https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3
   ```

### 3. Configuration

1. **Copy the example configuration:**
   ```bash
   cp config.example.json config.json
   ```

2. **Edit `config.json` with your credentials:**
   ```json
   {
     "supabase": {
       "endpoint_url": "https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3",
       "region": "ca-central-1",
       "bucket_name": "your-actual-bucket-name",
       "access_key_id": "your-actual-access-key",
       "secret_access_key": "your-actual-secret-key"
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
     },
     "logging": {
       "level": "INFO",
       "file": "sync.log"
     }
   }
   ```

## Configuration Options

### Supabase Settings
- `endpoint_url`: Your Supabase S3 endpoint URL
- `region`: Your Supabase region (ca-central-1)
- `bucket_name`: Your Supabase storage bucket name
- `access_key_id`: Your Supabase S3 access key
- `secret_access_key`: Your Supabase S3 secret key

### Google Drive Settings
- `credentials_file`: Path to Google Drive API credentials JSON
- `token_file`: Path to store OAuth token (auto-generated)
- `folder_id`: Specific folder ID to sync (null for entire drive)
- `query`: Custom Google Drive query filter (null for all files)
- `max_file_size_mb`: Maximum file size to sync in MB (null for no limit)

### Sync Settings
- `batch_size`: Number of files to process in each batch
- `delay_between_batches`: Seconds to wait between batches
- `skip_existing`: Skip files that already exist in Supabase
- `preserve_folder_structure`: Maintain folder structure in S3

### Logging Settings
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path

## Usage

### Basic Sync
```bash
python gdrive_to_supabase_sync.py
```

### Custom Configuration File
```bash
python gdrive_to_supabase_sync.py --config my_config.json
```

### Dry Run (Preview what would be synced)
```bash
python gdrive_to_supabase_sync.py --dry-run
```

## Advanced Usage

### Sync Specific Folder
Set the `folder_id` in your config to sync only a specific Google Drive folder:
```json
{
  "google_drive": {
    "folder_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  }
}
```

### Custom File Filtering
Use Google Drive query syntax to filter files:
```json
{
  "google_drive": {
    "query": "name contains 'backup' and modifiedTime > '2023-01-01T00:00:00'"
  }
}
```

### Batch Size Optimization
- **Small files, fast connection**: Increase batch_size to 50-100
- **Large files, slow connection**: Decrease batch_size to 5-10
- **Rate limiting issues**: Increase delay_between_batches

## File Handling

### Supported Files
- All binary files (images, videos, documents, etc.)
- Text files and documents
- Archives and compressed files

### Skipped Files
- Google Workspace files (Docs, Sheets, Slides) - require special export handling
- Files exceeding the configured size limit
- Files that already exist (when skip_existing is true)

### File Naming
- Files are uploaded with their original Google Drive names
- Folder structure is preserved if `preserve_folder_structure` is enabled
- Duplicate names are handled by S3's natural overwrite behavior

## Monitoring and Logs

### Log Files
The tool creates detailed logs in the specified log file (default: `sync.log`):
- File processing progress
- Upload success/failure status
- Error messages and stack traces
- Final sync statistics

### Console Output
Real-time progress updates including:
- Current batch being processed
- Files synced/skipped/failed per batch
- Overall progress statistics

### Final Statistics
After completion, you'll see a summary:
```
==================================================
SYNC SUMMARY
==================================================
Total files found: 1,234
Successfully synced: 1,200
Skipped files: 20
Failed files: 14
Total data synced: 2,456.78 MB
==================================================
```

## Troubleshooting

### Common Issues

1. **"Credentials not found" error:**
   - Ensure `credentials.json` is in the project directory
   - Verify the file is valid JSON from Google Cloud Console

2. **"Failed to connect to Supabase S3" error:**
   - Check your Supabase credentials in config.json
   - Verify your bucket name and region
   - Ensure your Supabase project has S3 storage enabled

3. **Rate limiting errors:**
   - Increase `delay_between_batches` in config
   - Decrease `batch_size` in config
   - Check Google Drive API quotas in Google Cloud Console

4. **Large file upload failures:**
   - Reduce `max_file_size_mb` in config
   - Check Supabase storage limits
   - Ensure stable internet connection

### Authentication Issues

1. **First run authentication:**
   - The tool will open a browser for Google OAuth
   - Grant necessary permissions
   - Token will be saved for future runs

2. **Token expiration:**
   - Delete `token.json` to re-authenticate
   - Run the sync tool again

### Performance Optimization

1. **For many small files:**
   ```json
   {
     "sync": {
       "batch_size": 50,
       "delay_between_batches": 0.5
     }
   }
   ```

2. **For large files:**
   ```json
   {
     "sync": {
       "batch_size": 5,
       "delay_between_batches": 2
     }
   }
   ```

## Security Notes

- Keep your `config.json` file secure and never commit it to version control
- Use environment variables for sensitive credentials in production
- Regularly rotate your Supabase S3 access keys
- Monitor your Google Drive API usage quotas

## License

This tool is provided as-is for educational and personal use. Please ensure compliance with Google Drive API terms of service and Supabase usage policies.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the log files for detailed error messages
3. Verify your configuration settings
4. Ensure all prerequisites are properly set up
