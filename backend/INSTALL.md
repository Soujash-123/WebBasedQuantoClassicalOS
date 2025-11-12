# Backend Installation Guide

## Quick Install

### Option 1: Install All Dependencies (Recommended)

```bash
pip install -r backend/requirements.txt
```

This installs:
- FastAPI
- Uvicorn
- Pydantic
- Watchdog (for hot reload)
- Requests (for testing)

### Option 2: Minimal Install (Without Hot Reload)

```bash
pip install fastapi uvicorn pydantic requests
```

Hot reload will be disabled, but all other features work.

## Start the Backend

```bash
# Simple start with auto-reload
uvicorn backend.main:app --reload

# Or use the startup script
python backend/start_backend.py

# Or on Windows
backend\start_backend.bat
```

## Verify Installation

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or run:
```bash
curl http://localhost:8000/health
```

## Common Issues

### "ModuleNotFoundError: No module named 'watchdog'"

**Solution 1** (Recommended):
```bash
pip install watchdog
```

**Solution 2** (Skip hot reload):
The backend will work without it, hot reload will just be disabled.

### "UserLayer object has no attribute 'initialize'"

This is a warning, not an error. The backend will still work. The UserLayer doesn't have an initialize method, but it's optional.

### Port 8000 already in use

```bash
# Use a different port
uvicorn backend.main:app --reload --port 8001
```

## What's Working

✅ **Core OS Layer**: All 10 layers initialized  
✅ **48 Commands**: Available through the API  
✅ **REST API**: All endpoints functional  
✅ **Auto Documentation**: Swagger UI and ReDoc  
✅ **CORS**: Enabled for frontend integration  

## Optional: Hot Reload

If you want the hot reload feature:

```bash
pip install watchdog
```

Then restart the backend. You'll see:
```
✓ Hot reload service started
🔍 Hot reload watching: /path/to/ai_os
```

## Next Steps

1. ✅ Backend is running
2. Test the API: `python backend/example_usage.py`
3. Build the frontend to consume these APIs
4. Integrate with the Web GUI layer

---

**Need help?** Check [README.md](README.md) for full documentation.
