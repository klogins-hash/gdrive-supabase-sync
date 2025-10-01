# Google Drive to Supabase S3 Sync Project

This project provides **two versions** of a Google Drive to Supabase S3 sync tool: an **MCP-based version** (recommended) and an **original version** with direct API access.

## 🌟 Recommended: MCP Version

**Files:**
- `mcp_sync_tool.py` - Main MCP-based sync tool
- `config_mcp.example.json` - MCP configuration template  
- `README_MCP.md` - MCP version documentation
- `sync_mcp.sh` - Interactive launcher script

**Advantages:**
- ✅ **No Google Drive API setup required**
- ✅ **Uses existing MCP connection** 
- ✅ **Simplified configuration** (only Supabase credentials needed)
- ✅ **Immediate testing capability**
- ✅ **No OAuth flow or token management**

**Quick Start:**
```bash
# Test the connection
python3 mcp_sync_tool.py --dry-run

# Or use the interactive launcher
./sync_mcp.sh
```

## 📚 Original Version (Reference)

**Files:**
- `gdrive_to_supabase_sync.py` - Original sync tool
- `config.example.json` - Original configuration template
- `README.md` - Original documentation
- `setup.py` - Setup script
- `sync.sh` - Launcher script

**Features:**
- Full Google Drive API integration
- OAuth authentication flow
- Comprehensive error handling
- Advanced filtering options

## 🗂️ Project Structure

```
gdrive-supabase-sync/
├── 🌟 MCP VERSION (RECOMMENDED)
│   ├── mcp_sync_tool.py           # Main MCP sync tool
│   ├── config_mcp.example.json    # MCP config template
│   ├── README_MCP.md              # MCP documentation
│   └── sync_mcp.sh                # MCP launcher
│
├── 📚 ORIGINAL VERSION
│   ├── gdrive_to_supabase_sync.py # Original sync tool
│   ├── config.example.json        # Original config template
│   ├── README.md                  # Original documentation
│   ├── setup.py                   # Setup script
│   └── sync.sh                    # Original launcher
│
├── 📋 SHARED FILES
│   ├── requirements.txt           # Python dependencies
│   ├── .gitignore                 # Security exclusions
│   └── PROJECT_OVERVIEW.md        # This file
```

## 🚀 Getting Started (MCP Version)

### 1. Test Connection
```bash
cd /Users/franksimpson/CascadeProjects/gdrive-supabase-sync
python3 mcp_sync_tool.py --dry-run
```

### 2. Configure Supabase
```bash
cp config_mcp.example.json config_mcp.json
# Edit config_mcp.json with your Supabase credentials
```

### 3. Run Sync
```bash
python3 mcp_sync_tool.py
```

## ⚙️ Your Supabase Configuration

**Endpoint:** `https://xmngdcugklkgboeblmbf.storage.supabase.co/storage/v1/s3`  
**Region:** `ca-central-1`

You need to add:
- `bucket_name` - Your Supabase storage bucket name
- `access_key_id` - Your Supabase S3 access key  
- `secret_access_key` - Your Supabase S3 secret key

## 🔍 Testing Results

The MCP connection has been tested and successfully:
- ✅ Connected to Google Drive via MCP
- ✅ Listed 6 files from your Google Drive
- ✅ Filtered out Google Workspace files appropriately
- ✅ Identified downloadable files (PDFs, videos, CSVs, etc.)

**Sample files detected:**
- `Mem0 Quickstart` (Colab notebook)
- `filtered_activity.csv` (CSV file)
- `Sloan's Bday Zoom.mp4` (149 MB video)
- `bookmarks_5_28_25.html` (HTML file)
- Various markdown files

## 📊 Sync Capabilities

**Supported File Types:**
- Documents (PDF, DOC, TXT, MD, HTML)
- Images (JPG, PNG, GIF, etc.)
- Videos (MP4, AVI, MOV, etc.)
- Data files (CSV, JSON, XML)
- Archives (ZIP, RAR, TAR)
- Code files (PY, JS, etc.)

**Batch Processing:**
- Configurable batch sizes
- Rate limiting between batches
- Progress tracking
- Error handling and retry logic

**Smart Filtering:**
- Skip Google Workspace files (requires export)
- File size limits
- Custom query filters
- Skip existing files option

## 🛠️ Maintenance

**MCP Version:**
- Minimal maintenance required
- No token refresh needed
- Only Supabase credentials to manage

**Original Version:**
- Requires Google API token refresh
- More complex credential management
- Additional dependencies

## 🎯 Recommendation

**Use the MCP version** (`mcp_sync_tool.py`) as it provides:
- Simpler setup and maintenance
- Leverages your existing MCP connection
- Faster time to deployment
- Reduced complexity

The original version remains available for reference or if you need specific features not available in the MCP version.

## 📞 Next Steps

1. **Test the MCP version**: `python3 mcp_sync_tool.py --dry-run`
2. **Configure your Supabase credentials** in `config_mcp.json`
3. **Run a small test sync** with limited batch size
4. **Scale up** once confirmed working
5. **Set up scheduling** if needed for regular syncs

The MCP-based sync tool is ready to use with your active Google Drive connection!
