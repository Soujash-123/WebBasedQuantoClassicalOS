# Backend Layer - Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### Step 2: Start the Backend

**Option A - Using Python:**
```bash
python backend/start_backend.py
```

**Option B - Using the batch file (Windows):**
```bash
backend\start_backend.bat
```

**Option C - Direct uvicorn:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Test the API

**Open in browser:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Or run the example script:**
```bash
python backend/example_usage.py
```

## 📋 What You Get

✅ **RESTful API** for the entire OS  
✅ **Hot Reload** - changes to `ai_os/` auto-reload  
✅ **Interactive Docs** - Swagger UI at `/docs`  
✅ **Modular Routers** - System, Shell, Files, Process  
✅ **Example Client** - Ready-to-use Python client  

## 🔗 Key Endpoints

```bash
# System Info
curl http://localhost:8000/system/info

# Execute Command
curl -X POST http://localhost:8000/shell/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "help"}'

# List Files
curl "http://localhost:8000/files/list?path=/"

# List Processes
curl http://localhost:8000/process/list
```

## 🔥 Hot Reload

The backend automatically reloads when you modify files in `ai_os/`:

1. Edit any file in `ai_os/`
2. Save the file
3. Backend detects change and reloads
4. No restart needed!

**Manual reload:**
```bash
curl -X POST http://localhost:8000/system/reload
```

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change port in start_backend.py or use:
uvicorn backend.main:app --port 8001
```

**Import errors?**
```bash
# Make sure you're in the project root
cd WebBasedOS-college
python backend/start_backend.py
```

**Dependencies missing?**
```bash
pip install fastapi uvicorn watchdog requests pydantic
```

---

**Ready to build the Web GUI?** The backend is now ready to serve your frontend! 🎉
