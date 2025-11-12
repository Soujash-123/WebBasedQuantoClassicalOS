"""
Process Manager
Manages process registration, execution, and control.
"""

from typing import Optional, List, Dict, Any, Callable
from .process import Process, ProcessState
from .scheduler import Scheduler


class ProcessManager:
    """Manages processes and provides CLI commands."""
    
    def __init__(self, scheduler: Scheduler):
        """
        Initialize process manager.
        
        Args:
            scheduler: Scheduler instance
        """
        self.scheduler = scheduler
        self.processes: Dict[int, Process] = {}
        
        print("[ProcessManager] Process Manager initialized")
    
    def run(
        self,
        name: str,
        runtime_function: Callable,
        priority: int = 5,
        args: tuple = (),
        kwargs: dict = None,
        owner: Optional[str] = None,
        background: bool = False
    ) -> Optional[Process]:
        """
        Run a new process.
        
        Args:
            name: Process name
            runtime_function: Function to execute
            priority: Priority level (1-10)
            args: Positional arguments
            kwargs: Keyword arguments
            owner: Process owner username
            background: Run in background (don't wait)
            
        Returns:
            Process instance
        """
        # Create process
        process = Process(
            name=name,
            runtime_function=runtime_function,
            priority=priority,
            args=args,
            kwargs=kwargs or {},
            owner=owner
        )
        
        # Register process
        self.processes[process.pid] = process
        
        # Add to scheduler
        self.scheduler.add_process(process)
        
        print(f"[ProcessManager] Created process {process.pid}: {name}")
        
        # Wait if foreground
        if not background:
            process.wait()
        
        return process
    
    def kill(self, pid: int, owner: Optional[str] = None) -> bool:
        """
        Terminate a process.
        
        Args:
            pid: Process ID
            owner: Username requesting termination (for permission check)
            
        Returns:
            True if terminated successfully
        """
        process = self.get_process(pid)
        if not process:
            print(f"[ProcessManager] Process {pid} not found")
            return False
        
        # Check permissions
        if owner and process.owner != owner and owner != "root":
            print(f"[ProcessManager] Permission denied: {owner} cannot kill process {pid}")
            return False
        
        return process.terminate()
    
    def suspend(self, pid: int, owner: Optional[str] = None) -> bool:
        """
        Suspend a process.
        
        Args:
            pid: Process ID
            owner: Username requesting suspension
            
        Returns:
            True if suspended successfully
        """
        process = self.get_process(pid)
        if not process:
            print(f"[ProcessManager] Process {pid} not found")
            return False
        
        # Check permissions
        if owner and process.owner != owner and owner != "root":
            print(f"[ProcessManager] Permission denied")
            return False
        
        return process.suspend()
    
    def resume(self, pid: int, owner: Optional[str] = None) -> bool:
        """
        Resume a suspended process.
        
        Args:
            pid: Process ID
            owner: Username requesting resume
            
        Returns:
            True if resumed successfully
        """
        process = self.get_process(pid)
        if not process:
            print(f"[ProcessManager] Process {pid} not found")
            return False
        
        # Check permissions
        if owner and process.owner != owner and owner != "root":
            print(f"[ProcessManager] Permission denied")
            return False
        
        return process.resume()
    
    def get_process(self, pid: int) -> Optional[Process]:
        """
        Get process by PID.
        
        Args:
            pid: Process ID
            
        Returns:
            Process instance or None
        """
        return self.processes.get(pid)
    
    def ps(self, owner: Optional[str] = None, show_all: bool = False) -> List[Dict[str, Any]]:
        """
        List processes (like Unix 'ps' command).
        
        Args:
            owner: Filter by owner (None = all)
            show_all: Show terminated processes
            
        Returns:
            List of process information dictionaries
        """
        result = []
        
        for process in self.processes.values():
            # Filter by owner
            if owner and process.owner != owner and owner != "root":
                continue
            
            # Filter terminated
            if not show_all and process.state == ProcessState.TERMINATED:
                continue
            
            result.append(process.get_info())
        
        # Sort by PID
        result.sort(key=lambda x: x['pid'])
        
        return result
    
    def top(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top processes by CPU time.
        
        Args:
            limit: Maximum number of processes to return
            
        Returns:
            List of process information dictionaries
        """
        all_processes = [p.get_info() for p in self.processes.values()]
        all_processes.sort(key=lambda x: x['cpu_time'], reverse=True)
        return all_processes[:limit]
    
    def get_process_count(self, state: Optional[ProcessState] = None) -> int:
        """
        Get count of processes.
        
        Args:
            state: Filter by state (None = all)
            
        Returns:
            Process count
        """
        if state is None:
            return len(self.processes)
        
        return sum(1 for p in self.processes.values() if p.state == state)
    
    def cleanup_terminated(self) -> int:
        """
        Remove terminated processes from memory.
        
        Returns:
            Number of processes removed
        """
        terminated_pids = [
            pid for pid, p in self.processes.items()
            if p.state == ProcessState.TERMINATED
        ]
        
        for pid in terminated_pids:
            del self.processes[pid]
        
        # Also clear from scheduler
        self.scheduler.clear_terminated()
        
        print(f"[ProcessManager] Cleaned up {len(terminated_pids)} terminated process(es)")
        return len(terminated_pids)
    
    def killall(self, owner: Optional[str] = None) -> int:
        """
        Terminate all processes.
        
        Args:
            owner: Only kill processes owned by this user
            
        Returns:
            Number of processes terminated
        """
        count = 0
        for process in list(self.processes.values()):
            if owner and process.owner != owner:
                continue
            
            if process.terminate():
                count += 1
        
        print(f"[ProcessManager] Terminated {count} process(es)")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get process manager statistics."""
        return {
            'total_processes': len(self.processes),
            'running': self.get_process_count(ProcessState.RUNNING),
            'ready': self.get_process_count(ProcessState.READY),
            'suspended': self.get_process_count(ProcessState.SUSPENDED),
            'waiting': self.get_process_count(ProcessState.WAITING),
            'terminated': self.get_process_count(ProcessState.TERMINATED),
            'scheduler_stats': self.scheduler.get_statistics()
        }
