"""
Scheduler
Handles process execution order and resource allocation.
"""

import time
import threading
from typing import List, Optional
from collections import deque
from .process import Process, ProcessState


class Scheduler:
    """Process scheduler with FIFO and round-robin support."""
    
    def __init__(self, algorithm: str = "fifo", time_quantum: float = 0.1):
        """
        Initialize scheduler.
        
        Args:
            algorithm: Scheduling algorithm ('fifo' or 'round_robin')
            time_quantum: Time slice for round-robin (seconds)
        """
        self.algorithm = algorithm.lower()
        self.time_quantum = time_quantum
        
        # Process queues
        self.ready_queue = deque()
        self.running_processes: List[Process] = []
        self.waiting_processes: List[Process] = []
        self.terminated_processes: List[Process] = []
        
        # Scheduler control
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Statistics
        self.total_processes = 0
        self.completed_processes = 0
        
        print(f"[Scheduler] Initialized with {algorithm} algorithm")
    
    def add_process(self, process: Process) -> None:
        """
        Add a process to the ready queue.
        
        Args:
            process: Process to add
        """
        with self._lock:
            if self.algorithm == "fifo":
                self.ready_queue.append(process)
            elif self.algorithm == "round_robin":
                # Priority-based insertion for round-robin
                inserted = False
                for i, p in enumerate(self.ready_queue):
                    if process.priority > p.priority:
                        self.ready_queue.insert(i, process)
                        inserted = True
                        break
                if not inserted:
                    self.ready_queue.append(process)
            
            self.total_processes += 1
            print(f"[Scheduler] Added process {process.pid} to ready queue")
    
    def start(self) -> None:
        """Start the scheduler."""
        if self.running:
            print("[Scheduler] Already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._schedule_loop, daemon=True)
        self.scheduler_thread.start()
        print("[Scheduler] Started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2.0)
        print("[Scheduler] Stopped")
    
    def _schedule_loop(self) -> None:
        """Main scheduling loop."""
        while self.running:
            try:
                if self.algorithm == "fifo":
                    self._schedule_fifo()
                elif self.algorithm == "round_robin":
                    self._schedule_round_robin()
                
                # Clean up terminated processes
                self._cleanup_terminated()
                
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                print(f"[Scheduler] Error in scheduling loop: {e}")
    
    def _schedule_fifo(self) -> None:
        """FIFO (First-In-First-Out) scheduling."""
        with self._lock:
            # Start processes from ready queue
            while self.ready_queue:
                process = self.ready_queue.popleft()
                if process.start():
                    self.running_processes.append(process)
    
    def _schedule_round_robin(self) -> None:
        """Round-robin scheduling with time quantum."""
        with self._lock:
            # Start new processes if slots available
            max_concurrent = 5  # Limit concurrent processes
            while self.ready_queue and len(self.running_processes) < max_concurrent:
                process = self.ready_queue.popleft()
                if process.start():
                    self.running_processes.append(process)
            
            # Check running processes for time quantum expiration
            # (Simplified - in real OS, would preempt and context switch)
            for process in self.running_processes[:]:
                if process.get_runtime() > self.time_quantum and len(self.ready_queue) > 0:
                    # Move to back of queue (simulated preemption)
                    if process.state == ProcessState.RUNNING:
                        process.suspend()
                        self.running_processes.remove(process)
                        self.ready_queue.append(process)
                        process.resume()
    
    def _cleanup_terminated(self) -> None:
        """Move terminated processes to terminated list."""
        with self._lock:
            for process in self.running_processes[:]:
                if process.state == ProcessState.TERMINATED:
                    self.running_processes.remove(process)
                    self.terminated_processes.append(process)
                    self.completed_processes += 1
    
    def get_process_by_pid(self, pid: int) -> Optional[Process]:
        """
        Find a process by PID.
        
        Args:
            pid: Process ID
            
        Returns:
            Process instance or None
        """
        with self._lock:
            # Check all queues
            all_processes = (
                list(self.ready_queue) +
                self.running_processes +
                self.waiting_processes +
                self.terminated_processes
            )
            
            for process in all_processes:
                if process.pid == pid:
                    return process
        
        return None
    
    def get_all_processes(self) -> List[Process]:
        """Get all processes in the system."""
        with self._lock:
            return (
                list(self.ready_queue) +
                self.running_processes +
                self.waiting_processes +
                self.terminated_processes
            )
    
    def get_running_processes(self) -> List[Process]:
        """Get currently running processes."""
        with self._lock:
            return self.running_processes.copy()
    
    def get_statistics(self) -> dict:
        """Get scheduler statistics."""
        with self._lock:
            return {
                'algorithm': self.algorithm,
                'total_processes': self.total_processes,
                'completed_processes': self.completed_processes,
                'ready_queue_size': len(self.ready_queue),
                'running_count': len(self.running_processes),
                'waiting_count': len(self.waiting_processes),
                'terminated_count': len(self.terminated_processes)
            }
    
    def clear_terminated(self) -> int:
        """
        Clear terminated processes from memory.
        
        Returns:
            Number of processes cleared
        """
        with self._lock:
            count = len(self.terminated_processes)
            self.terminated_processes.clear()
            return count
