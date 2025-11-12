"""
Network Interface Management
Manages virtual and physical network interfaces.
"""

import socket
import platform
from typing import Dict, List, Optional
from datetime import datetime
import subprocess


class NetworkAdapter:
    """Represents a network adapter"""
    
    def __init__(self, name: str, adapter_type: str = "ethernet"):
        self.name = name
        self.adapter_type = adapter_type  # ethernet, wifi, loopback
        self.status = "down"
        self.ip_address = None
        self.mac_address = None
        self.netmask = None
        self.gateway = None
        self.dns_servers = []
        self.bytes_sent = 0
        self.bytes_received = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.last_updated = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.adapter_type,
            'status': self.status,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'netmask': self.netmask,
            'gateway': self.gateway,
            'dns_servers': self.dns_servers,
            'stats': {
                'bytes_sent': self.bytes_sent,
                'bytes_received': self.bytes_received,
                'packets_sent': self.packets_sent,
                'packets_received': self.packets_received
            },
            'last_updated': self.last_updated.isoformat()
        }


class NetworkInterface:
    """Network Interface Manager"""
    
    def __init__(self):
        self.adapters: Dict[str, NetworkAdapter] = {}
        self.active_connections = []
        self.connection_history = []
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """Initialize network adapters"""
        # Create loopback adapter
        loopback = NetworkAdapter("lo", "loopback")
        loopback.status = "up"
        loopback.ip_address = "127.0.0.1"
        self.adapters["lo"] = loopback
        
        # Try to detect real network interfaces
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Create primary adapter
            eth0 = NetworkAdapter("eth0", "ethernet")
            eth0.status = "up"
            eth0.ip_address = local_ip
            self.adapters["eth0"] = eth0
        except:
            # Create virtual adapter
            eth0 = NetworkAdapter("eth0", "ethernet")
            eth0.status = "down"
            self.adapters["eth0"] = eth0
    
    def get_adapter(self, name: str) -> Optional[NetworkAdapter]:
        """Get adapter by name"""
        return self.adapters.get(name)
    
    def list_adapters(self) -> List[NetworkAdapter]:
        """List all adapters"""
        return list(self.adapters.values())
    
    def get_active_adapters(self) -> List[NetworkAdapter]:
        """Get active (up) adapters"""
        return [a for a in self.adapters.values() if a.status == "up"]
    
    def set_adapter_status(self, name: str, status: str) -> bool:
        """Set adapter status (up/down)"""
        if name in self.adapters:
            self.adapters[name].status = status
            self.adapters[name].last_updated = datetime.now()
            return True
        return False
    
    def get_local_ip(self) -> Optional[str]:
        """Get local IP address"""
        try:
            # Try to get actual IP
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            # Return first active adapter IP
            for adapter in self.get_active_adapters():
                if adapter.ip_address and adapter.ip_address != "127.0.0.1":
                    return adapter.ip_address
            return "127.0.0.1"
    
    def get_hostname(self) -> str:
        """Get system hostname"""
        return socket.gethostname()
    
    def get_platform_info(self) -> dict:
        """Get platform network info"""
        return {
            'hostname': self.get_hostname(),
            'platform': platform.system(),
            'local_ip': self.get_local_ip(),
            'adapters': len(self.adapters),
            'active_adapters': len(self.get_active_adapters())
        }
    
    def update_adapter_stats(self, name: str, bytes_sent: int = 0, 
                           bytes_received: int = 0, packets_sent: int = 0, 
                           packets_received: int = 0):
        """Update adapter statistics"""
        if name in self.adapters:
            adapter = self.adapters[name]
            adapter.bytes_sent += bytes_sent
            adapter.bytes_received += bytes_received
            adapter.packets_sent += packets_sent
            adapter.packets_received += packets_received
            adapter.last_updated = datetime.now()
    
    def format_adapter_info(self, adapter: NetworkAdapter) -> str:
        """Format adapter information"""
        lines = [
            f"{adapter.name}: <{adapter.status.upper()}>",
            f"  Type: {adapter.adapter_type}",
        ]
        
        if adapter.ip_address:
            lines.append(f"  IP Address: {adapter.ip_address}")
        if adapter.netmask:
            lines.append(f"  Netmask: {adapter.netmask}")
        if adapter.gateway:
            lines.append(f"  Gateway: {adapter.gateway}")
        if adapter.mac_address:
            lines.append(f"  MAC Address: {adapter.mac_address}")
        
        lines.extend([
            f"  TX: {adapter.bytes_sent} bytes ({adapter.packets_sent} packets)",
            f"  RX: {adapter.bytes_received} bytes ({adapter.packets_received} packets)"
        ])
        
        return "\n".join(lines)
