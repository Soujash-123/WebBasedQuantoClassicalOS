"""
Network Monitor
Monitors network connections and activity.
"""

import socket
from typing import List, Dict, Optional
from datetime import datetime
import threading
import time


class Connection:
    """Represents a network connection"""
    
    def __init__(self, local_addr: str, local_port: int, remote_addr: str = None, 
                 remote_port: int = None, state: str = "ESTABLISHED", protocol: str = "TCP"):
        self.local_addr = local_addr
        self.local_port = local_port
        self.remote_addr = remote_addr
        self.remote_port = remote_port
        self.state = state
        self.protocol = protocol
        self.established_time = datetime.now()
        self.bytes_sent = 0
        self.bytes_received = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'local': f"{self.local_addr}:{self.local_port}",
            'remote': f"{self.remote_addr}:{self.remote_port}" if self.remote_addr else "N/A",
            'state': self.state,
            'protocol': self.protocol,
            'established': self.established_time.isoformat(),
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received
        }


class NetworkMonitor:
    """Monitors network connections and activity"""
    
    def __init__(self):
        self.connections: List[Connection] = []
        self.connection_history = []
        self.max_history = 500
        self.monitoring = False
        self.monitor_thread = None
        self.open_ports = set()
    
    def start_monitoring(self):
        """Start network monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def add_connection(self, local_addr: str, local_port: int, remote_addr: str = None,
                      remote_port: int = None, state: str = "ESTABLISHED", 
                      protocol: str = "TCP") -> Connection:
        """Add a connection"""
        conn = Connection(local_addr, local_port, remote_addr, remote_port, state, protocol)
        self.connections.append(conn)
        
        # Add to history
        self.connection_history.append({
            'timestamp': datetime.now().isoformat(),
            'connection': conn.to_dict(),
            'action': 'opened'
        })
        
        if len(self.connection_history) > self.max_history:
            self.connection_history = self.connection_history[-self.max_history:]
        
        return conn
    
    def remove_connection(self, conn: Connection):
        """Remove a connection"""
        if conn in self.connections:
            self.connections.remove(conn)
            
            self.connection_history.append({
                'timestamp': datetime.now().isoformat(),
                'connection': conn.to_dict(),
                'action': 'closed'
            })
    
    def get_connections(self, state: Optional[str] = None, protocol: Optional[str] = None) -> List[Connection]:
        """Get connections with optional filtering"""
        conns = self.connections
        
        if state:
            conns = [c for c in conns if c.state == state]
        if protocol:
            conns = [c for c in conns if c.protocol == protocol]
        
        return conns
    
    def get_listening_ports(self) -> List[int]:
        """Get list of listening ports"""
        return sorted(list(self.open_ports))
    
    def add_listening_port(self, port: int):
        """Add a listening port"""
        self.open_ports.add(port)
    
    def remove_listening_port(self, port: int):
        """Remove a listening port"""
        self.open_ports.discard(port)
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        total = len(self.connections)
        by_state = {}
        by_protocol = {}
        
        for conn in self.connections:
            by_state[conn.state] = by_state.get(conn.state, 0) + 1
            by_protocol[conn.protocol] = by_protocol.get(conn.protocol, 0) + 1
        
        return {
            'total_connections': total,
            'by_state': by_state,
            'by_protocol': by_protocol,
            'listening_ports': len(self.open_ports),
            'history_entries': len(self.connection_history)
        }
    
    def format_connections(self) -> str:
        """Format connections for display"""
        if not self.connections:
            return "No active connections"
        
        lines = [
            "=" * 100,
            f"{'Protocol':<10} {'Local Address':<25} {'Remote Address':<25} {'State':<15} {'Bytes TX/RX'}",
            "=" * 100
        ]
        
        for conn in self.connections:
            local = f"{conn.local_addr}:{conn.local_port}"
            remote = f"{conn.remote_addr}:{conn.remote_port}" if conn.remote_addr else "N/A"
            bytes_info = f"{conn.bytes_sent}/{conn.bytes_received}"
            
            lines.append(
                f"{conn.protocol:<10} {local:<25} {remote:<25} {conn.state:<15} {bytes_info}"
            )
        
        lines.append("=" * 100)
        lines.append(f"Total connections: {len(self.connections)}")
        
        return "\n".join(lines)
    
    def format_listening_ports(self) -> str:
        """Format listening ports for display"""
        if not self.open_ports:
            return "No listening ports"
        
        lines = ["Listening Ports:", "-" * 40]
        
        for port in sorted(self.open_ports):
            lines.append(f"  Port {port}")
        
        return "\n".join(lines)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Simulate monitoring - in real implementation, would scan actual connections
                time.sleep(5)
            except Exception as e:
                print(f"Network monitor error: {e}")
                time.sleep(5)
