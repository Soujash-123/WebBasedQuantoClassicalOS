"""
Backend Services
Core services for OS connection, file metadata, and hot reload functionality
"""

# Import file metadata database
from .file_metadata_db import file_metadata_db as file_metadata_db

# Import OS connector
from .os_connector import os_connector, OSConnector

# Initialize services
__all__ = ['os_connector', 'file_metadata_db', 'OSConnector']

# Make os_connector methods available at the package level
from .os_connector import (
    get_os,
    get_layer,
    execute_command,
    get_all_commands,
    get_system_info,
    reload_os,
    shutdown
)

# Add to __all__
__all__.extend([
    'get_os',
    'get_layer',
    'execute_command',
    'get_all_commands',
    'get_system_info',
    'reload_os',
    'shutdown'
])
