"""
File Router
API endpoints for file system operations
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import OS connector and metadata DB
from backend.services import os_connector
from backend.services.file_metadata_db import file_metadata_db

router = APIRouter(prefix="/files", tags=["files"])


class FileReadRequest(BaseModel):
    """Request model for reading a file"""
    path: str


class FileWriteRequest(BaseModel):
    """Request model for writing a file"""
    path: str
    content: str
    mode: Optional[str] = "w"  # w for write, a for append


class FileDeleteRequest(BaseModel):
    """Request model for deleting a file"""
    path: str


class DirectoryRequest(BaseModel):
    """Request model for directory operations"""
    path: str


@router.get("/list")
async def list_files(path: str = "/") -> Dict[str, Any]:
    """
    List files in a directory
    
    Args:
        path: Directory path (default: root)
    
    Returns:
        List of files and directories with metadata
    """
    try:
        # First try to get files from the filesystem layer
        fs_layer = None
        try:
            fs_layer = os_connector.get_os().layers.get('filesystem')
        except Exception as e:
            print(f"Warning: Could not get filesystem layer: {e}")
        
        # If filesystem layer is available, use it
        if fs_layer:
            try:
                # Get files from filesystem layer
                if hasattr(fs_layer, 'ls'):
                    fs_files = fs_layer.ls(path)
                    
                    # Convert to our metadata format
                    files = []
                    for item in fs_files if isinstance(fs_files, list) else [fs_files]:
                        if isinstance(item, dict):
                            file_info = {
                                'path': item.get('path', ''),
                                'name': item.get('name', ''),
                                'type': item.get('type', 'file'),
                                'size': item.get('size', 0),
                                'parent_path': path.rstrip('/'),
                                'modified_at': item.get('modified_at', datetime.now().timestamp()),
                                'is_encrypted': item.get('is_encrypted', False),
                                'encryption_status': 'encrypted' if item.get('is_encrypted') else 'not_encrypted'
                            }
                            files.append(file_info)
                            
                            # Save to metadata DB for future use
                            file_metadata_db.save_file_metadata(file_info)
                else:
                    # Fallback to metadata DB if filesystem layer doesn't support ls
                    files = file_metadata_db.list_directory(path)
            except Exception as e:
                print(f"Error getting files from filesystem layer: {e}")
                files = file_metadata_db.list_directory(path)
        else:
            # Fallback to metadata DB if filesystem layer is not available
            files = file_metadata_db.list_directory(path)
                
            # Use filesystem to get the list and update metadata
            if hasattr(fs_layer, 'list_directory'):
                fs_files = fs_layer.list_directory(path)
            elif hasattr(fs_layer, 'ls'):
                fs_files = fs_layer.ls(path)
                # Fallback: execute ls command with proper path handling
                try:
                    # Ensure path is properly quoted if it contains spaces
                    if ' ' in path and not (path.startswith('"') and path.endswith('"')):
                        path = f'"{path}"'
                    
                    # Execute the command with the path as a single argument
                    output = os_connector.execute_command('ls', [path])
                    fs_files = output.split('\n') if output else []
                except Exception as e:
                    print(f"Error executing ls command: {e}")
                    fs_files = []
            
            # Convert filesystem format to our metadata format
            files = []
            for item in fs_files if isinstance(fs_files, list) else [fs_files]:
                if isinstance(item, dict):
                    # Already in the right format
                    file_info = item
                else:
                    # Convert string to metadata format
                    file_info = {
                        'name': os.path.basename(item),
                        'path': os.path.join(path, item).replace('\\', '/'),
                        'type': 'directory' if os.path.isdir(item) else 'file',
                        'size': 0,
                        'parent_path': path.rstrip('/'),
                        'modified_at': datetime.now().timestamp(),
                        'is_encrypted': False,
                        'encryption_status': 'not_encrypted'
                    }
                
                # Save to metadata DB
                file_metadata_db.save_file_metadata(file_info)
                files.append(file_info)
        
        return {
            "path": path,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read")
async def read_file(request: FileReadRequest) -> Dict[str, Any]:
    """
    Read file contents
    
    Args:
        request: File path to read
    
    Returns:
        File contents with metadata
    """
    try:
        # First try to get from metadata DB
        metadata = file_metadata_db.get_file_metadata(request.path)
        
        # If not in DB or content preview is not enough, try to read from filesystem
        if not metadata or not metadata.get('content_preview'):
            # Get filesystem layer
            fs_layer = None
            try:
                fs_layer = os_connector.get_os().layers.get('filesystem')
            except Exception as e:
                print(f"Warning: Could not get filesystem layer: {e}")
            
            if not fs_layer:
                if metadata:
                    # Return what we have from metadata
                    return {
                        "path": request.path,
                        "content": "",
                        "metadata": dict(metadata),
                        "status": "success"
                    }
                else:
                    raise HTTPException(status_code=404, detail="File not found and filesystem layer not available")
            
            # Read file content
            try:
                try:
                    if hasattr(fs_layer, 'read'):
                        content = fs_layer.read(request.path)
                    elif hasattr(fs_layer, 'cat'):
                        content = fs_layer.cat(request.path)
                    else:
                        # Ensure path is properly quoted if it contains spaces
                        file_path = request.path
                        if ' ' in file_path and not (file_path.startswith('"') and file_path.endswith('"')):
                            file_path = f'"{file_path}"'
                        
                        output = os_connector.execute_command('cat', [file_path])
                        content = output if output else ""
                except Exception as e:
                    print(f"Error reading file: {e}")
                    content = ""
                
                # Update metadata in DB
                if content:
                    file_info = {
                        'path': request.path,
                        'name': os.path.basename(request.path),
                        'type': 'file',
                        'size': len(content),
                        'parent_path': os.path.dirname(request.path).rstrip('/') or '/',
                        'modified_at': datetime.now().timestamp(),
                        'content_preview': (content[:500] + '...') if len(content) > 500 else content,
                        'is_encrypted': False,
                        'encryption_status': 'not_encrypted'
                    }
                    file_metadata_db.save_file_metadata(file_info)
                
                return {
                    "path": request.path,
                    "content": content,
                    "metadata": metadata or {},
                    "status": "success"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
        else:
            # Return content from metadata
            return {
                "path": request.path,
                "content": metadata.get('content_preview', ''),
                "metadata": dict(metadata),
                "status": "success"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/write")
async def write_file(request: FileWriteRequest) -> Dict[str, Any]:
    """
    Write content to a file
    
    Args:
        request: File path, content, and write mode
    
    Returns:
        Write operation result with updated metadata
    """
    try:
        # Get filesystem layer if available
        fs_layer = None
        try:
            fs_layer = os_connector.get_os().layers.get('filesystem')
        except Exception as e:
            print(f"Warning: Could not get filesystem layer: {e}")
        
        if fs_layer:
            try:
                # Determine the write mode
                write_mode = getattr(request, 'mode', 'w')
                
                # Handle different write modes
                if write_mode == 'a' and hasattr(fs_layer, 'append'):
                    # Append to existing content
                    fs_layer.append(request.path, request.content)
                elif hasattr(fs_layer, 'write'):
                    # Write new content
                    fs_layer.write(request.path, request.content)
                elif hasattr(fs_layer, 'write_file'):
                    fs_layer.write_file(request.path, request.content, write_mode)
                elif hasattr(fs_layer, 'create_file'):
                    fs_layer.create_file(request.path, request.content)
                else:
                    # Fallback: use echo command
                    os_connector.execute_command('echo', [request.content, '>', request.path])
            except Exception as e:
                print(f"Error writing to filesystem: {e}")
                # Continue to update metadata even if filesystem write fails
        
        # Update metadata in database
        file_info = {
            'path': request.path,
            'name': os.path.basename(request.path),
            'type': 'file',
            'size': len(request.content),
            'parent_path': os.path.dirname(request.path).rstrip('/') or '/',
            'modified_at': datetime.now().timestamp(),
            'content_preview': (request.content[:500] + '...') if len(request.content) > 500 else request.content,
            'is_encrypted': False,
            'encryption_status': 'not_encrypted'
        }
        
        if not file_metadata_db.save_file_metadata(file_info):
            print(f"Warning: Failed to update metadata for {request.path}")
        
        return {
            "path": request.path,
            "status": "success",
            "message": "File written successfully",
            "metadata": file_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_file(path: str) -> Dict[str, Any]:
    """
    Delete a file or directory
    
    Args:
        path: Path to file or directory
    
    Returns:
        Delete operation result
    """
    try:
        # Get filesystem layer
        fs_layer = os_connector.get_layer('filesystem')
        if not fs_layer:
            raise HTTPException(status_code=500, detail="Filesystem layer not available")
        
        # First, check if it's a directory and get all child paths
        is_dir = False
        child_paths = []
        
        try:
            if hasattr(fs_layer, 'ls'):
                try:
                    contents = fs_layer.ls(path)
                    if contents:
                        is_dir = True
                        # Recursively get all child paths
                        for item in contents:
                            item_path = os.path.join(path, item['name'] if isinstance(item, dict) else item)
                            child_paths.append(item_path)
                except:
                    # If ls fails, it's probably a file
                    pass
        except:
            # If any error occurs, just proceed with the original path
            pass
        
        # Delete file or directory from filesystem
        if hasattr(fs_layer, 'rm'):
            fs_layer.rm(path)
        elif hasattr(fs_layer, 'delete_file'):
            fs_layer.delete_file(path)
        else:
            # Fallback: use rm command
            os_connector.execute_command('rm', ['-rf', path])
        
        # Delete metadata from database
        # First delete children if it's a directory
        if is_dir:
            for child_path in child_paths:
                file_metadata_db.delete_file_metadata(child_path)
        
        # Then delete the path itself
        file_metadata_db.delete_file_metadata(path)
        
        return {
            "path": path,
            "status": "success",
            "message": "File/directory deleted successfully",
            "is_directory": is_dir,
            "deleted_items": len(child_paths) + 1  # +1 for the path itself
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mkdir")
async def create_directory(request: DirectoryRequest) -> Dict[str, Any]:
    """
    Create a new directory
    
    Args:
        request: Directory path to create
    
    Returns:
        Directory creation result
    """
    try:
        # Execute mkdir command
        output = os_connector.execute_command('mkdir', [request.path])
        
        return {
            "path": request.path,
            "status": "success",
            "message": "Directory created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_file_info(path: str) -> Dict[str, Any]:
    """
    Get file or directory information
    
    Args:
        path: File or directory path
    
    Returns:
        File/directory metadata
    """
    try:
        # Get filesystem layer
        fs_layer = os_connector.get_layer('filesystem')
        
        if not fs_layer:
            raise HTTPException(status_code=500, detail="Filesystem layer not available")
        
        # Get file info
        # This will depend on your VFS implementation
        if hasattr(fs_layer, 'get_file_info'):
            info = fs_layer.get_file_info(path)
        elif hasattr(fs_layer, 'stat'):
            info = fs_layer.stat(path)
        else:
            # Fallback: execute stat or ls command
            output = os_connector.execute_command('ls', ['-l', path])
            info = {"raw_output": output}
        
        return {
            "path": path,
            "info": info if isinstance(info, dict) else {"details": str(info)},
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree")
async def get_directory_tree(path: str = "/", max_depth: int = 3) -> Dict[str, Any]:
    """
    Get directory tree structure
    
    Args:
        path: Root path for tree (default: root)
        max_depth: Maximum depth to traverse
    
    Returns:
        Directory tree structure
    """
    try:
        # Execute tree command if available
        output = os_connector.execute_command('tree', [path])
        
        return {
            "path": path,
            "tree": output,
            "status": "success"
        }
    except Exception as e:
        # If tree command not available, use ls -R
        try:
            output = os_connector.execute_command('ls', ['-R', path])
            return {
                "path": path,
                "tree": output,
                "status": "success"
            }
        except:
            raise HTTPException(status_code=500, detail=str(e))
