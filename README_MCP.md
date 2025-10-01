# Google Drive to Supabase S3 Sync Tool (MCP Version)

A Python tool that syncs files from Google Drive to Supabase S3 storage using the **MCP (Model Context Protocol)** connection. This version eliminates the need for manual Google Drive API setup and credentials by leveraging the active MCP connection.

## 🌟 Key Advantages of MCP Version

- **No Google Drive API Setup Required**: Uses the existing MCP connection
- **No OAuth Flow**: No need to handle Google authentication
- **No Credentials Management**: No `credentials.json` or `token.json` files needed
- **Simplified Configuration**: Only Supabase credentials required
- **Real-time Testing**: Can be tested directly in the MCP environment

## 🚀 Quick Start

### 1. Test the Connection (Dry Run)

First, test that the MCP connection is working:

```bash
python mcp_sync_tool.py --dry-run
```

This will:
- List files from your Google Drive via MCP
- Show what would be synced
- Not download or upload anything

### 2. Configure Supabase Credentials

Copy the example config and update with your credentials:

```bash
cp config_mcp.example.json config_mcp.json
```

Edit `config_mcp.json`:

```json
{
  "supabase": {
    "endpoint_url": "https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3",
    "region": "ca-central-1",
    "bucket_name": "your-actual-bucket-name",
    "access_key_id": "your-actual-access-key",
    "secret_access_key": "your-actual-secret-key"
  }
}
```

### 3. Run the Sync

```bash
python mcp_sync_tool.py
```

## 📁 Files Overview

### MCP-Specific Files

- **`mcp_sync_tool.py`** - Main MCP-based sync tool
- **`config_mcp.example.json`** - MCP configuration template
- **`README_MCP.md`** - This documentation

### Original Files (for reference)

- **`gdrive_to_supabase_sync.py`** - Original version requiring Google API setup
- **`config.example.json`** - Original configuration template
- **`README.md`** - Original documentation

## ⚙️ Configuration Options

### Supabase Settings (Required)
```json
{
  "supabase": {
    "endpoint_url": "https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3",
    "region": "ca-central-1",
    "bucket_name": "your-bucket-name",
    "access_key_id": "your-access-key",
    "secret_access_key": "your-secret-key"
  }
}
```

### Google Drive Settings (Optional)
```json
{
  "google_drive": {
    "folder_id": null,           // Specific folder ID to sync (null = entire drive)
    "query": null,               // Custom Google Drive query filter
    "max_file_size_mb": 100,     // Maximum file size to sync
    "page_size": 100             // Files per page when listing
  }
}
```

### Sync Settings (Optional)
```json
{
  "sync": {
    "batch_size": 10,            // Files per batch
    "delay_between_batches": 1,  // Seconds between batches
    "skip_existing": true,       // Skip files that already exist
    "preserve_folder_structure": false  // Maintain folder structure
  }
}
```

## 🎯 Usage Examples

### Basic Sync
```bash
python mcp_sync_tool.py
```

### Dry Run (Preview)
```bash
python mcp_sync_tool.py --dry-run
```

### Custom Configuration
```bash
python mcp_sync_tool.py --config my_config.json
```

### Sync Specific Folder
Update your config:
```json
{
  "google_drive": {
    "folder_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  }
}
```

### Filter Files by Query
```json
{
  "google_drive": {
    "query": "name contains 'backup' and modifiedTime > '2023-01-01T00:00:00'"
  }
}
```

## 🔍 How It Works

### 1. MCP Connection
The tool uses the active MCP connection to Google Drive, which means:
- No authentication setup required
- Uses your existing Google Drive permissions
- Leverages the MCP session for API calls

### 2. File Discovery
```python
# MCP call to list files
result, error = run_composio_tool("GOOGLEDRIVE_LIST_FILES", {
    "pageSize": 100,
    "q": "trashed=false and mimeType != 'application/vnd.google-apps.folder'"
})
```

### 3. File Download
```python
# MCP call to download file
result, error = run_composio_tool("GOOGLEDRIVE_DOWNLOAD_FILE", {
    "file_id": file_id
})
```

### 4. Upload to Supabase
Uses boto3 to upload to your Supabase S3 storage:
```python
s3_client.upload_fileobj(file, bucket_name, s3_key)
```

## 📊 Output Example

```
🚀 Starting Google Drive to Supabase sync (MCP version)
📋 Fetching file list from Google Drive via MCP...
📄 Page 1: Found 25 files (Total: 25)
📊 Found 25 total files to process

🔄 Processing batch 1/3 (10 files)
  [1/10] Processing: document.pdf
    ⬇️  Downloading via MCP...
    ✅ Downloaded document.pdf
    ⬆️  Uploading to Supabase S3...
    ✅ Successfully uploaded: document.pdf (2.5 MB)

✅ Batch 1/3 completed: 10 synced, 0 skipped, 0 failed
⏳ Waiting 1 seconds before next batch...

============================================================
📊 SYNC SUMMARY (MCP VERSION)
============================================================
📁 Total files found: 25
✅ Successfully synced: 23
⏭️  Skipped files: 2
❌ Failed files: 0
📦 Batches processed: 3
💾 Total data synced: 45.67 MB
============================================================
```

## 🛠️ Troubleshooting

### Common Issues

1. **"No files found in Google Drive"**
   - Check if your Google Drive has files
   - Verify the MCP connection is active
   - Try adjusting the query filter

2. **"Failed to connect to Supabase S3"**
   - Verify your Supabase credentials
   - Check bucket name and region
   - Ensure your Supabase project has S3 storage enabled

3. **"MCP download error"**
   - Some file types may not be downloadable
   - Large files might timeout
   - Check file permissions in Google Drive

### File Type Handling

**Supported Files:**
- Documents (PDF, DOC, TXT, etc.)
- Images (JPG, PNG, GIF, etc.)
- Videos (MP4, AVI, etc.)
- Archives (ZIP, RAR, etc.)
- Code files (PY, JS, etc.)

**Skipped Files:**
- Google Workspace files (Docs, Sheets, Slides) - require export
- Folders
- Files exceeding size limit
- Files already uploaded (when skip_existing=true)

## 🔒 Security Notes

- The MCP connection handles Google Drive authentication securely
- Only Supabase credentials need to be managed locally
- Keep your `config_mcp.json` file secure
- Add `config_mcp.json` to `.gitignore`

## 🆚 MCP vs Original Version

| Feature | MCP Version | Original Version |
|---------|-------------|------------------|
| Google Drive Setup | ✅ None required | ❌ Complex OAuth setup |
| Credentials | 🟡 Supabase only | 🔴 Google + Supabase |
| Dependencies | 🟢 Minimal | 🟡 Google API libraries |
| Testing | ✅ Immediate | ❌ Requires setup |
| Maintenance | ✅ Low | 🟡 Token refresh needed |

## 📝 Next Steps

1. **Test with dry run**: `python mcp_sync_tool.py --dry-run`
2. **Configure Supabase credentials** in `config_mcp.json`
3. **Run small batch**: Set `batch_size: 5` for initial testing
4. **Scale up**: Increase batch size and remove file limits
5. **Schedule**: Set up cron job for regular syncing

## 🤝 Support

For issues:
1. Check the troubleshooting section
2. Review log files (`mcp_sync.log`)
3. Test with `--dry-run` first
4. Verify MCP connection is active

The MCP version provides a much simpler and more reliable way to sync your Google Drive files to Supabase S3 storage!
