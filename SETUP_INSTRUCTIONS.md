# 🚀 Quick Setup Instructions

Your MCP-based Google Drive to Supabase S3 sync tool is **almost ready**! 

## ✅ What's Already Configured

- ✅ **MCP Connection**: Active Google Drive connection (dp@thekollektiv.xyz)
- ✅ **Supabase Credentials**: Your S3 credentials are configured
- ✅ **Sync Tool**: MCP-based sync tool is ready
- ✅ **Configuration**: `config_mcp.json` is set up

## 🔧 One Final Step Required

You need to create a bucket named `gdrive-sync` in your Supabase dashboard:

### Create Bucket in Supabase:

1. **Go to your Supabase dashboard**
2. **Navigate to Storage** 
3. **Create a new bucket** named: `gdrive-sync`
   - ⚠️ **Important**: Use exactly `gdrive-sync` (no spaces, lowercase with hyphen)
   - This matches your configuration file

### Alternative: Use Different Bucket Name

If you prefer a different name, update `config_mcp.json`:

```json
{
  "supabase": {
    "bucket_name": "your-preferred-name"
  }
}
```

**Valid bucket names:**
- ✅ `gdrive-sync`
- ✅ `my-files` 
- ✅ `backup-storage`
- ✅ `drive_backup`
- ❌ `test bucket` (no spaces)
- ❌ `My Files` (no spaces or capitals)

## 🧪 Test the Setup

Once you've created the bucket, test the connection:

```bash
cd /Users/franksimpson/CascadeProjects/gdrive-supabase-sync

# Test with dry run (safe - no actual sync)
python3 mcp_sync_tool.py --dry-run
```

## 🚀 Run the Sync

If the dry run looks good:

```bash
# Run the actual sync
python3 mcp_sync_tool.py

# Or use the interactive launcher
./sync_mcp.sh
```

## 📊 What Will Happen

The tool will:

1. **Connect to Google Drive** via MCP (no auth needed)
2. **List your files** (excluding Google Workspace files and folders)
3. **Download files in batches** of 5 files at a time
4. **Upload to Supabase S3** in your `gdrive-sync` bucket
5. **Skip existing files** (resume capability)
6. **Provide detailed progress** and final statistics

## 🔍 Current Google Drive Files Detected

From our test, your drive contains:
- `Mem0 Quickstart` (Colab notebook - will be skipped)
- `filtered_activity.csv` (0.01 MB - will sync)
- `northflank-deployment-progress-summary.md` (0.01 MB - will sync)
- `Sloan's Bday Zoom.mp4` (149 MB - will sync)
- `bookmarks_5_28_25.html` (0.36 MB - will sync)
- `github-permanent-setup.md` (0.00 MB - will sync)

## 🛠️ Configuration Summary

**Your current settings:**
- **Batch size**: 5 files at a time
- **Delay between batches**: 2 seconds
- **Max file size**: 100 MB
- **Skip existing**: Yes (resume capability)
- **Preserve folders**: No (flat structure)

## 🆘 Need Help?

If you encounter issues:

1. **Check the logs**: `mcp_sync.log`
2. **Run dry run first**: `python3 mcp_sync_tool.py --dry-run`
3. **Verify bucket exists**: Check your Supabase dashboard

---

**You're just one bucket creation away from syncing your Google Drive to Supabase! 🎉**
