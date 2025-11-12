"""
Process Router
API endpoints for process management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from backend.services.os_connector import os_connector

router = APIRouter(prefix="/process", tags=["process"])


class ProcessStartRequest(BaseModel):
    """Request model for starting a process"""
    name: str
    command: Optional[str] = None
    args: Optional[List[str]] = None


class ProcessStopRequest(BaseModel):
    """Request model for stopping a process"""
    pid: int


class ProcessSignalRequest(BaseModel):
    """Request model for sending signal to process"""
    pid: int
    signal: str


@router.get("/list")
async def list_processes() -> Dict[str, Any]:
    """
    List all running processes
    
    Returns:
        List of active processes
    """
    try:
        # Get process layer
        process_layer = os_connector.get_layer('process')
        
        if not process_layer:
            raise HTTPException(status_code=500, detail="Process layer not available")
        
        # Get process list
        if hasattr(process_layer, 'list_processes'):
            processes = process_layer.list_processes()
        elif hasattr(process_layer, 'get_all_processes'):
            processes = process_layer.get_all_processes()
        else:
            # Fallback: execute ps command
            output = os_connector.execute_command('ps', [])
            processes = {"raw_output": output}
        
        return {
            "processes": processes if isinstance(processes, (list, dict)) else [processes],
            "count": len(processes) if isinstance(processes, (list, dict)) else 1,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{pid}")
async def get_process_info(pid: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific process
    
    Args:
        pid: Process ID
    
    Returns:
        Process details
    """
    try:
        # Get process layer
        process_layer = os_connector.get_layer('process')
        
        if not process_layer:
            raise HTTPException(status_code=500, detail="Process layer not available")
        
        # Get process info
        if hasattr(process_layer, 'get_process_info'):
            info = process_layer.get_process_info(pid)
        elif hasattr(process_layer, 'get_process'):
            info = process_layer.get_process(pid)
        else:
            raise HTTPException(status_code=404, detail=f"Process {pid} not found")
        
        return {
            "pid": pid,
            "info": info if isinstance(info, dict) else {"details": str(info)},
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_process(request: ProcessStartRequest) -> Dict[str, Any]:
    """
    Start a new process
    
    Args:
        request: Process name and optional command/args
    
    Returns:
        Started process information
    """
    try:
        # Get process layer
        process_layer = os_connector.get_layer('process')
        
        if not process_layer:
            raise HTTPException(status_code=500, detail="Process layer not available")
        
        # Start process
        if hasattr(process_layer, 'start_process'):
            result = process_layer.start_process(
                name=request.name,
                command=request.command,
                args=request.args
            )
        elif hasattr(process_layer, 'create_process'):
            result = process_layer.create_process(
                name=request.name,
                command=request.command or request.name
            )
        else:
            raise HTTPException(status_code=500, detail="Process start not supported")
        
        return {
            "name": request.name,
            "result": result if isinstance(result, dict) else {"pid": result},
            "status": "success",
            "message": f"Process '{request.name}' started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_process(request: ProcessStopRequest) -> Dict[str, Any]:
    """
    Stop a running process
    
    Args:
        request: Process ID to stop
    
    Returns:
        Stop operation result
    """
    try:
        # Get process layer
        process_layer = os_connector.get_layer('process')
        
        if not process_layer:
            raise HTTPException(status_code=500, detail="Process layer not available")
        
        # Stop process
        if hasattr(process_layer, 'stop_process'):
            result = process_layer.stop_process(request.pid)
        elif hasattr(process_layer, 'kill_process'):
            result = process_layer.kill_process(request.pid)
        else:
            # Fallback: execute kill command
            result = os_connector.execute_command('kill', [str(request.pid)])
        
        return {
            "pid": request.pid,
            "status": "success",
            "message": f"Process {request.pid} stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signal")
async def send_signal(request: ProcessSignalRequest) -> Dict[str, Any]:
    """
    Send a signal to a process
    
    Args:
        request: Process ID and signal name
    
    Returns:
        Signal operation result
    """
    try:
        # Get process layer
        process_layer = os_connector.get_layer('process')
        
        if not process_layer:
            raise HTTPException(status_code=500, detail="Process layer not available")
        
        # Send signal
        if hasattr(process_layer, 'send_signal'):
            result = process_layer.send_signal(request.pid, request.signal)
        else:
            # Fallback: execute kill command with signal
            result = os_connector.execute_command('kill', [f'-{request.signal}', str(request.pid)])
        
        return {
            "pid": request.pid,
            "signal": request.signal,
            "status": "success",
            "message": f"Signal {request.signal} sent to process {request.pid}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_process_stats() -> Dict[str, Any]:
    """
    Get overall process statistics
    
    Returns:
        Process statistics and metrics
    """
    try:
        # Get process layer
        process_layer = os_connector.get_layer('process')
        
        if not process_layer:
            raise HTTPException(status_code=500, detail="Process layer not available")
        
        # Get stats
        if hasattr(process_layer, 'get_stats'):
            stats = process_layer.get_stats()
        elif hasattr(process_layer, 'get_statistics'):
            stats = process_layer.get_statistics()
        else:
            # Fallback: get basic info
            processes = process_layer.list_processes() if hasattr(process_layer, 'list_processes') else []
            stats = {
                "total_processes": len(processes) if isinstance(processes, list) else 0,
                "running": len(processes) if isinstance(processes, list) else 0
            }
        
        return {
            "stats": stats if isinstance(stats, dict) else {"info": str(stats)},
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
