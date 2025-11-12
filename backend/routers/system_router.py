"""
System Router
API endpoints for system information, status, and control
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from backend.services.os_connector import os_connector

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information
    
    Returns:
        System version, uptime, layers, commands, and configuration
    """
    try:
        return os_connector.get_system_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get current system status
    
    Returns:
        Quick status check of the OS
    """
    try:
        os_master = os_connector.get_os()
        
        return {
            "status": "running" if os_master.initialized else "stopped",
            "timestamp": datetime.now().isoformat(),
            "layers_active": len(os_master.layers),
            "commands_available": len(os_master.command_registry)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers")
async def get_layers() -> Dict[str, Any]:
    """
    Get information about all OS layers
    
    Returns:
        List of active layers and their status
    """
    try:
        os_master = os_connector.get_os()
        
        layers_info = {}
        for layer_name, layer in os_master.layers.items():
            layers_info[layer_name] = {
                "name": layer_name,
                "type": type(layer).__name__,
                "initialized": hasattr(layer, 'initialized') and layer.initialized if hasattr(layer, 'initialized') else True
            }
        
        return {
            "total_layers": len(layers_info),
            "layers": layers_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commands")
async def get_all_commands() -> Dict[str, Any]:
    """
    Get all available commands
    
    Returns:
        Dictionary of all registered commands with their metadata
    """
    try:
        commands = os_connector.get_all_commands()
        
        # Format commands for API response
        formatted_commands = {}
        for cmd_name, cmd_info in commands.items():
            formatted_commands[cmd_name] = {
                "name": cmd_name,
                "layer": cmd_info.get('layer', 'unknown'),
                "description": cmd_info.get('description', ''),
                "usage": cmd_info.get('usage', '')
            }
        
        return {
            "total_commands": len(formatted_commands),
            "commands": formatted_commands
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uptime")
async def get_uptime() -> Dict[str, Any]:
    """
    Get system uptime
    
    Returns:
        Uptime in various formats
    """
    try:
        info = os_connector.get_system_info()
        uptime_seconds = info.get('uptime_seconds', 0)
        
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        return {
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": f"{hours}h {minutes}m {seconds}s",
            "start_time": info.get('start_time')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_system() -> Dict[str, Any]:
    """
    Reload the OS system (hot reload)
    
    Returns:
        Reload status and message
    """
    try:
        result = os_connector.reload_os()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """
    Get system configuration
    
    Returns:
        Current OS configuration
    """
    try:
        info = os_connector.get_system_info()
        return {
            "config": info.get('config', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
