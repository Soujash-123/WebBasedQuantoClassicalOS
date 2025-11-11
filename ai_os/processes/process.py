"""
Process Class
Represents a single process/task in the OS.
"""

import time
import threading
from enum import Enum
from typing import Callable, Optional, Any, Dict


class ProcessState(Enum):
    """Process execution states."""
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class Process:
    """Represents a process in the OS."""
    
    _next_pid = 1
    _pid_lock = threading.Lock()
    
    def __init__(
        self,
        name: str,
        runtime_function: Callable,
        priority: int = 5,
        args: tuple = (),
        kwargs: dict = None,
        owner: Optional[str] = None
    ):
        """
        Initialize a process.
        
        Args:
            name: Process name
            runtime_function: Function to execute
            priority: Priority level (1-10, higher = more important)
            args: Positional arguments for runtime function
            kwargs: Keyword arguments for runtime function
            owner: Username of process owner
        """
        with Process._pid_lock:
            self.pid = Process._next_pid
            Process._next_pid += 1
        
        self.name = name
        self.runtime_function = runtime_function
        self.priority = max(1, min(10, priority))  # Clamp between 1-10
        self.args = args
        self.kwargs = kwargs or {}
        self.owner = owner or "system"
        
        # State management
        self.state = ProcessState.READY
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.cpu_time = 0.0
        
        # Execution
        self.thread: Optional[threading.Thread] = None
        self.result: Any = None
        self.error: Optional[Exception] = None
        
        # Control flags
        self._suspend_flag = threading.Event()
        self._suspend_flag.set()  # Not suspended initially
        self._terminate_flag = threading.Event()
        
        # Output capture
        self.output_lines = []
        self.max_output_lines = 1000
    
    def start(self) -> bool:
        """
        Start the process execution.
        
        Returns:
            True if started successfully
        """
        if self.state != ProcessState.READY:
            print(f"[Process {self.pid}] Cannot start from state {self.state.value}")
            return False
        
        self.state = ProcessState.RUNNING
        self.started_at = time.time()
        
        # Create and start thread
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        print(f"[Process {self.pid}] Started: {self.name}")
        return True
    
    def _run(self) -> None:
        """Internal method to run the process."""
        try:
            start_time = time.time()
            
            # Execute the runtime function
            self.result = self.runtime_function(*self.args, **self.kwargs)
            
            # Update CPU time
            self.cpu_time += time.time() - start_time
            
            # Mark as terminated
            self.state = ProcessState.TERMINATED
            self.finished_at = time.time()
            
            print(f"[Process {self.pid}] Completed successfully")
            
        except Exception as e:
            self.error = e
            self.state = ProcessState.TERMINATED
            self.finished_at = time.time()
            print(f"[Process {self.pid}] Error: {e}")
    
    def terminate(self) -> bool:
        """
        Terminate the process.
        
        Returns:
            True if terminated successfully
        """
        if self.state == ProcessState.TERMINATED:
            print(f"[Process {self.pid}] Already terminated")
            return False
        
        self._terminate_flag.set()
        self.state = ProcessState.TERMINATED
        self.finished_at = time.time()
        
        print(f"[Process {self.pid}] Terminated")
        return True
    
    def suspend(self) -> bool:
        """
        Suspend the process execution.
        
        Returns:
            True if suspended successfully
        """
        if self.state != ProcessState.RUNNING:
            print(f"[Process {self.pid}] Cannot suspend from state {self.state.value}")
            return False
        
        self._suspend_flag.clear()
        self.state = ProcessState.SUSPENDED
        
        print(f"[Process {self.pid}] Suspended")
        return True
    
    def resume(self) -> bool:
        """
        Resume the process execution.
        
        Returns:
            True if resumed successfully
        """
        if self.state != ProcessState.SUSPENDED:
            print(f"[Process {self.pid}] Cannot resume from state {self.state.value}")
            return False
        
        self._suspend_flag.set()
        self.state = ProcessState.RUNNING
        
        print(f"[Process {self.pid}] Resumed")
        return True
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for process to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if process completed
        """
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout)
            return not self.thread.is_alive()
        return True
    
    def is_alive(self) -> bool:
        """Check if process is still running."""
        return self.state in [ProcessState.RUNNING, ProcessState.SUSPENDED, ProcessState.WAITING]
    
    def get_runtime(self) -> float:
        """Get total runtime in seconds."""
        if self.started_at is None:
            return 0.0
        
        if self.finished_at:
            return self.finished_at - self.started_at
        else:
            return time.time() - self.started_at
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get process information.
        
        Returns:
            Dictionary with process details
        """
        return {
            'pid': self.pid,
            'name': self.name,
            'state': self.state.value,
            'priority': self.priority,
            'owner': self.owner,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
            'runtime': self.get_runtime(),
            'cpu_time': self.cpu_time,
            'has_error': self.error is not None,
            'error': str(self.error) if self.error else None
        }
    
    def add_output(self, line: str) -> None:
        """Add output line from process."""
        self.output_lines.append(line)
        if len(self.output_lines) > self.max_output_lines:
            self.output_lines.pop(0)
    
    def get_output(self) -> str:
        """Get all process output."""
        return '\n'.join(self.output_lines)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Process(pid={self.pid}, name='{self.name}', state={self.state.value})"
