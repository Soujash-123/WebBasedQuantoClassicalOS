"""
Shell Router
API endpoints for executing shell commands in the virtual OS
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from backend.services.os_connector import os_connector

router = APIRouter(prefix="/shell", tags=["shell"])


class CommandRequest(BaseModel):
    """Request model for command execution"""
    command: str  # The complete command string including arguments


class CommandResponse(BaseModel):
    """Response model for command execution"""
    command: str
    output: str
    status: str
    timestamp: str


@router.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest) -> CommandResponse:
    """
    Execute a shell command in the virtual OS
    
    Args:
        request: Complete command string including all arguments
    
    Returns:
        Command execution result
    """
    try:
        from datetime import datetime
        import shlex
        
        # Parse the command string into command and arguments
        parts = shlex.split(request.command)
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute the command with the parsed arguments
        output = os_connector.execute_command(command, args)
        
        return CommandResponse(
            command=request.command,
            output=output,
            status="success",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commands")
async def list_available_commands() -> Dict[str, Any]:
    """
    List all available shell commands
    
    Returns:
        Dictionary of available commands
    """
    try:
        commands = os_connector.get_all_commands()
        
        # Filter and format shell commands
        shell_commands = {}
        for cmd_name, cmd_info in commands.items():
            shell_commands[cmd_name] = {
                "name": cmd_name,
                "description": cmd_info.get('description', ''),
                "usage": cmd_info.get('usage', ''),
                "layer": cmd_info.get('layer', 'unknown')
            }
        
        return {
            "total": len(shell_commands),
            "commands": shell_commands
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/command/{command_name}")
async def get_command_info(command_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific command
    
    Args:
        command_name: Name of the command
    
    Returns:
        Command details
    """
    try:
        commands = os_connector.get_all_commands()
        
        if command_name not in commands:
            raise HTTPException(status_code=404, detail=f"Command not found: {command_name}")
        
        cmd_info = commands[command_name]
        
        return {
            "name": command_name,
            "description": cmd_info.get('description', ''),
            "usage": cmd_info.get('usage', ''),
            "layer": cmd_info.get('layer', 'unknown')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def execute_batch_commands(commands: List[CommandRequest]) -> Dict[str, Any]:
    """
    Execute multiple commands in sequence
    
    Args:
        commands: List of commands to execute
    
    Returns:
        Results of all command executions
    """
    try:
        from datetime import datetime
        
        results = []
        
        for cmd_req in commands:
            try:
                output = os_connector.execute_command(cmd_req.command, cmd_req.args)
                results.append({
                    "command": cmd_req.command,
                    "output": output,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "command": cmd_req.command,
                    "output": str(e),
                    "status": "error"
                })
        
        return {
            "total": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
