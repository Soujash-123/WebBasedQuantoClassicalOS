# Backend Layer - Web-Based Virtual OS

The **Backend Layer** is a FastAPI-based REST API that bridges the **Core OS Layer** and the **Web GUI Layer**. It provides a modular, RESTful interface to interact with all OS functionalities including system management, shell commands, file operations, and process control.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web GUI Layer                        │
│                  (React Frontend)                       │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   Backend Layer (FastAPI)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routers    │  │   Services   │  │  Hot Reload  │  │
│  │              │  │              │  │              │  │
│  │ • System     │  │ • OS Conn.   │  │ • Watchdog   │  │
│  │ • Shell      │  │ • Hot Reload │  │ • Auto Sync  │  │
│  │ • Files      │  │              │  │              │  │
│  │ • Process    │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ Python API
┌─────────────────────────────────────────────────────────┐
│                    Core OS Layer                        │
│  (All OS Layers: VFS, Memory, Network, Security, etc.) │
└─────────────────────────────────────────────────────────┘
```

## 📁 Folder Structure

```
backend/
│
├── main.py                 # FastAPI entry point
├── requirements.txt        # Python dependencies
├── example_usage.py        # API testing script
│
├── routers/
│   ├── __init__.py
│   ├── system_router.py    # System info & control endpoints
│   ├── shell_router.py     # Shell command execution
│   ├── file_router.py      # File system operations
│   └── process_router.py   # Process management
│
└── services/
    ├── __init__.py
    ├── os_connector.py     # Interface to Core OS Layer
    └── hot_reload.py       # Dynamic module reloading
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Or if using the main environment
pip install -r ai_os/requirements.txt
```

### 2. Start the Backend Server

```bash
# From project root
python backend/main.py

# Or using uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### System Endpoints (`/system`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/system/info` | Get comprehensive system information |
| GET | `/system/status` | Get current system status |
| GET | `/system/layers` | Get all OS layers information |
| GET | `/system/commands` | Get all available commands |
| GET | `/system/uptime` | Get system uptime |
| GET | `/system/config` | Get system configuration |
| POST | `/system/reload` | Trigger hot reload of OS |

### Shell Endpoints (`/shell`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shell/execute` | Execute a shell command |
| GET | `/shell/commands` | List all shell commands |
| GET | `/shell/command/{name}` | Get command details |
| POST | `/shell/batch` | Execute multiple commands |

### File Endpoints (`/files`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/files/list` | List files in directory |
| POST | `/files/read` | Read file contents |
| POST | `/files/write` | Write to file |
| POST | `/files/delete` | Delete file |
| POST | `/files/mkdir` | Create directory |
| GET | `/files/info` | Get file/directory info |
| GET | `/files/tree` | Get directory tree |

### Process Endpoints (`/process`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/process/list` | List all processes |
| GET | `/process/info/{pid}` | Get process details |
| POST | `/process/start` | Start a new process |
| POST | `/process/stop` | Stop a process |
| POST | `/process/signal` | Send signal to process |
| GET | `/process/stats` | Get process statistics |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root information |
| GET | `/health` | Health check |
| GET | `/hot-reload/status` | Hot reload status |
| POST | `/hot-reload/trigger` | Manually trigger reload |

## 🔥 Hot Reload Feature

The backend includes a **hot reload** mechanism that watches the `ai_os/` directory for changes and automatically reloads the OS without restarting the server.

### How It Works

1. **Watchdog** monitors `ai_os/` directory for Python file changes
2. When changes are detected, the OS is gracefully reloaded
3. All API endpoints continue to work without interruption
4. No need to restart the backend server

### Manual Reload

```bash
# Trigger reload via API
curl -X POST http://localhost:8000/system/reload

# Or
curl -X POST http://localhost:8000/hot-reload/trigger
```

### Check Reload Status

```bash
curl http://localhost:8000/hot-reload/status
```

## 📝 Example Usage

### Using Python Requests

```python
import requests

# Get system info
response = requests.get("http://localhost:8000/system/info")
print(response.json())

# Execute a command
response = requests.post(
    "http://localhost:8000/shell/execute",
    json={"command": "help", "args": []}
)
print(response.json())

# List files
response = requests.get(
    "http://localhost:8000/files/list",
    params={"path": "/"}
)
print(response.json())
```

### Using the Example Script

```bash
# Run the example usage script
python backend/example_usage.py
```

This script demonstrates all major API endpoints.

### Using cURL

```bash
# System info
curl http://localhost:8000/system/info

# Execute command
curl -X POST http://localhost:8000/shell/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "help"}'

# List files
curl "http://localhost:8000/files/list?path=/"

# Health check
curl http://localhost:8000/health
```

## 🔧 Configuration

The backend connects to the Core OS Layer using the `OSConnector` service, which initializes the `AIOSMaster` with default configuration. You can customize the OS configuration by modifying the config in `ai_os/system_config.json`.

## 🛠️ Development

### Adding New Endpoints

1. Create a new router in `backend/routers/`
2. Define your endpoints using FastAPI decorators
3. Import and include the router in `main.py`

Example:

```python
# backend/routers/my_router.py
from fastapi import APIRouter

router = APIRouter(prefix="/my-feature", tags=["my-feature"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello!"}
```

```python
# backend/main.py
from backend.routers import my_router

app.include_router(my_router.router)
```

### Testing

```bash
# Run the example script
python backend/example_usage.py

# Or use pytest (if tests are added)
pytest backend/tests/
```

## 🐛 Troubleshooting

### Backend won't start

- Ensure all dependencies are installed: `pip install -r backend/requirements.txt`
- Check if port 8000 is already in use
- Verify the Core OS Layer can be imported

### Hot reload not working

- Check if `watchdog` is installed
- Verify the `ai_os/` directory path is correct
- Check hot reload status: `curl http://localhost:8000/hot-reload/status`

### Commands not executing

- Verify the OS is initialized: `curl http://localhost:8000/system/status`
- Check available commands: `curl http://localhost:8000/system/commands`
- Review server logs for errors

## 📚 Next Steps

1. **Web GUI Layer**: Build a React frontend that consumes these APIs
2. **Authentication**: Add user authentication and session management
3. **WebSockets**: Implement real-time updates for system events
4. **Logging**: Enhanced logging and monitoring
5. **Testing**: Add comprehensive unit and integration tests

## 🔗 Related Documentation

- Core OS Layer: `ai_os/README.md`
- API Documentation: http://localhost:8000/docs (when running)
- Architecture: `documentation/ARCHITECTURE.md`

---

**Backend Layer v1.0.0** - Part of the Modular Web-Based Virtual OS
