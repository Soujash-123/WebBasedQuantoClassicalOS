# Web-Based Virtual Operating System

A modular, web-based virtual operating system with a modern architecture that separates concerns between frontend, backend, and core OS layers.

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Key Components](#-key-components)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [License](#-license)

## 🌟 Project Overview

This project implements a web-based virtual operating system with the following key features:

- **Modular Architecture**: Separates concerns between UI, API, and core OS functionality
- **AI-Powered Control**: Currently features a prompt-based controller for system interactions
- **Hot Reloading**: Supports live code updates without restarting the system
- **RESTful API**: FastAPI-based backend with comprehensive API documentation
- **Modern Frontend**: Built with React for a responsive user interface
- **Virtual File System**: Implements a virtual file system with metadata support
- **Process Management**: Manages system processes and services
- **Device Abstraction**: Abstracted device layer for hardware interaction

### 🚧 Current AI Implementation

The current version includes a prompt-based AI controller that allows users to interact with the system using natural language commands. This serves as the foundation for more advanced AI capabilities.

### 🔜 Upcoming: CoPilot Integration

In the next phase of development, we plan to enhance the system with a comprehensive CoPilot feature that will provide:
- Intelligent command suggestions
- Context-aware assistance
- Automated task execution
- Learning from user behavior
- Proactive system management

This will transform the system from a command-based interface to an intelligent assistant that can understand and execute complex workflows.

## 🏗️ System Architecture

The system follows a three-layer architecture:

1. **Frontend Layer**
   - React-based web interface
   - Communicates with backend via REST API
   - Implements terminal emulator and file explorer

2. **Backend Layer (FastAPI)**
   - RESTful API endpoints
   - Handles authentication and authorization
   - Manages communication with core OS layer
   - Implements hot reload functionality

3. **Core OS Layer**
   - AIOSMaster: Main controller managing all OS components
   - Layered architecture with independent modules:
     - Core Layer: Basic OS functionality
     - System Layer: System services and utilities
     - Device Layer: Hardware abstraction
     - File System Layer: Virtual file system management
     - Memory Layer: Memory management
     - Network Layer: Network services
     - Security Layer: Authentication and permissions
     - Process Layer: Process management
     - User Layer: User management
     - Diagnostics Layer: System monitoring

## 🧩 Key Components

### Backend Components

#### `backend/main.py`
- FastAPI application entry point
- Configures CORS and includes all API routers
- Implements lifespan management for startup/shutdown

#### `backend/services/os_connector.py`
- Singleton pattern for OS instance management
- Provides thread-safe access to OS functionality
- Handles OS initialization and shutdown

#### `backend/services/hot_reload.py`
- Monitors file system changes in the OS layer
- Implements hot reloading of OS modules
- Uses watchdog for efficient file system monitoring

#### API Routers

##### `system_router.py` - System Information and Control
- `GET /system/info` - Get comprehensive system information
- `GET /system/status` - Get current system status
- `GET /system/layers` - List all active OS layers
- `GET /system/commands` - List all available commands
- `GET /system/uptime` - Get system uptime information
- `POST /system/reload` - Reload the OS system (hot reload)
- `GET /system/config` - Get system configuration

##### `file_router.py` - File System Operations
- `GET /files/list` - List files in a directory
- `POST /files/read` - Read file contents
- `POST /files/write` - Write content to a file
- `DELETE /files/delete` - Delete a file or directory
- `POST /files/mkdir` - Create a new directory
- `GET /files/info` - Get file/directory information
- `GET /files/tree` - Get directory tree structure

##### `shell_router.py` - Command Execution
- `POST /shell/execute` - Execute a shell command
- `GET /shell/commands` - List available shell commands
- `GET /shell/commands/{command_name}` - Get command information
- `POST /shell/batch` - Execute multiple commands in sequence

##### `process_router.py` - Process Management
- `GET /processes` - List all running processes
- `POST /processes/start` - Start a new process
- `GET /processes/{pid}` - Get process details
- `DELETE /processes/{pid}` - Terminate a process
- `GET /processes/{pid}/output` - Get process output

### Frontend Components

#### `frontend/src/App.jsx`
- Main application component
- Implements routing and layout
- Manages application state

#### `frontend/src/api/client.js`
- API client for backend communication
- Handles requests and responses
- Implements error handling

#### `frontend/src/components/`
- `AppContent.jsx`: Main application content
- `TextEditor.jsx`: File editing component

### Core OS Components

#### `ai_os/os_master.py`
- Main OS controller
- Manages all OS layers and services
- Handles command registration and execution

#### `ai_os/core/`
- Core OS functionality
- System initialization and configuration
- Service management

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WebBasedOS-college
   ```

2. **Set up the Python environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the System

1. **Start the backend server**
   ```bash
   # From project root
   python -m backend.start_backend
   ```

2. **Start the frontend development server**
   ```bash
   # From frontend directory
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
WebBasedOS-college/
├── ai_os/                  # Core OS implementation
│   ├── core/               # Core OS functionality
│   ├── devices/            # Device drivers and abstractions
│   └── os_master.py        # Main OS controller
│
├── backend/                # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── services/           # Backend services
│   ├── main.py             # FastAPI app entry point
│   └── start_backend.py    # Backend startup script
│
├── frontend/               # React frontend
│   ├── public/             # Static files
│   ├── src/                # Source code
│   │   ├── api/            # API client
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   └── package.json        # Frontend dependencies
│
├── vfs_storage/            # Virtual file system storage
├── config.json             # Main configuration
└── README.md               # This file
```

## 📚 API Documentation

The API is documented using OpenAPI and Swagger UI. After starting the backend server, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

## 🛠 Development

### Hot Reloading

The system supports hot reloading of the OS layer during development. When you modify any Python files in the `ai_os` directory, the changes will be automatically detected and the OS will be reloaded.

### Testing

Run the test suite with:

```bash
# Run Python tests
pytest

# Run frontend tests
cd frontend
npm test
```

### Code Style

- Python: Follows PEP 8
- JavaScript: Follows Airbnb style guide
- Use pre-commit hooks for automatic formatting and linting

# ⚡ Quick Start - Web-Based Virtual OS

## 🚀 Start Everything (2 Commands)

### Terminal 1: Backend
```bash
cd WebBasedOS-college
uvicorn backend.main:app --reload
```

### Terminal 2: Frontend
```bash
cd frontend
npm install  # First time only
npm run dev
```

### Open Browser
```
http://localhost:5173
```

---

## ✅ What You'll See

### Desktop
- **Files** icon - Real file browser
- **Terminal** icon - Execute OS commands
- **Settings** - System configuration
- **Monitor** - Live system stats

### Features
- ✨ Drag windows around
- 🔄 Minimize/Maximize windows
- 📁 Browse real files from backend
- 💻 Execute real shell commands
- 📊 Live system monitoring
- ⚙️ System settings and info

---

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Web OS Interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | Backend status |

---

## 🧪 Test Commands (Terminal App)

```bash
help        # List all commands
ls          # List files
whoami      # Current user
syscheck    # System diagnostics
uptime      # System uptime
ps          # List processes
clear       # Clear terminal
```

---

## 📦 Dependencies

### Backend
```bash
pip install fastapi uvicorn pydantic requests watchdog
```

### Frontend
```bash
cd frontend
npm install
```

---

## 🐛 Common Issues

### Backend won't start?
```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Try different port
uvicorn backend.main:app --reload --port 8001
```

### Frontend shows errors?
```bash
# Check backend is running
curl http://localhost:8000/health

# Update API URL in frontend/.env
VITE_API_URL=http://localhost:8000
```

### Port already in use?
```bash
# Backend: Change port
uvicorn backend.main:app --reload --port 8001

# Frontend: Change port
npm run dev -- --port 5174
```

---

## 📚 Full Documentation

- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Backend Docs**: `backend/README.md`
- **Backend Quick Start**: `backend/QUICKSTART.md`
- **Core OS Docs**: `ai_os/README.md`

---

## 🎯 Architecture

```
┌─────────────────────────────────────┐
│     Web GUI (React + Vite)          │  ← You interact here
│     http://localhost:5173            │
└─────────────────────────────────────┘
              ↕ REST API
┌─────────────────────────────────────┐
│   Backend Layer (FastAPI)           │  ← API endpoints
│   http://localhost:8000              │
└─────────────────────────────────────┘
              ↕ Python
┌─────────────────────────────────────┐
│   Core OS Layer (Python)            │  ← OS functionality
│   10 Layers, 48 Commands             │
└─────────────────────────────────────┘
```

---

## ✨ Features

### Files App
- Browse real filesystem
- Navigate folders
- View file list
- Auto-refresh

### Terminal App
- Execute real commands
- Command history
- Real-time output
- 48+ commands available

### Settings App
- System information
- OS version
- Active layers
- Command count

### Monitor App
- Live system stats
- Process list (auto-refresh)
- System uptime
- Resource usage

---

## 🎉 You're Ready!

Everything is set up and connected. Enjoy your Web-Based OS!

**Need help?** Check `INTEGRATION_GUIDE.md` for detailed instructions.

---

*Built with FastAPI + React + Python* 🚀

