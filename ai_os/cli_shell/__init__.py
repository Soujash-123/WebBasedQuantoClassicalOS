"""
Unified CLI Shell Layer
Integrates all OS layers into a cohesive interactive command-line interface.
"""

from .shell import CLIShell
from .command_parser import CommandParser
from .command_registry import CommandRegistry
from .command_history import CommandHistory
from .command_aliases import AliasManager
from .command_help import HelpSystem
from .os_session_manager import SessionManager
from .error_handler import ErrorHandler
from .logger import CLILogger

__all__ = [
    'CLIShell',
    'CommandParser',
    'CommandRegistry',
    'CommandHistory',
    'AliasManager',
    'HelpSystem',
    'SessionManager',
    'ErrorHandler',
    'CLILogger'
]
