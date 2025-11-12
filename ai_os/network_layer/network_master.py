"""
Network Layer Master
Unified interface for the network layer.
"""

from typing import Optional
from .network_interface import NetworkInterface
from .network_monitor import NetworkMonitor
from .network_tools import NetworkTools


class NetworkLayer:
    """Master controller for network layer"""
    
    def __init__(self, enable_monitoring: bool = True):
        self.network_interface = NetworkInterface()
        self.network_monitor = NetworkMonitor()
        self.network_tools = NetworkTools()
        self.initialized = False
        self.enable_monitoring = enable_monitoring
    
    def initialize(self):
        """Initialize network layer"""
        if self.initialized:
            return
        
        if self.enable_monitoring:
            self.network_monitor.start_monitoring()
        
        self.initialized = True
        print(f"[Network Layer] Initialized - Hostname: {self.network_interface.get_hostname()}")
    
    def shutdown(self):
        """Shutdown network layer"""
        if not self.initialized:
            return
        
        self.network_monitor.stop_monitoring()
        self.initialized = False
        print("[Network Layer] Shutdown complete")
    
    # Network Commands
    
    def cmd_ping(self, args: list = None) -> str:
        """Ping a host"""
        if not args:
            return "Usage: ping <host> [count] [timeout]"
        
        host = args[0]
        count = int(args[1]) if len(args) > 1 else 4
        timeout = int(args[2]) if len(args) > 2 else 5
        
        result = self.network_tools.ping(host, count, timeout)
        return self.network_tools.format_ping_result(result)
    
    def cmd_netstat(self, args: list = None) -> str:
        """Show network connections"""
        return self.network_monitor.format_connections()
    
    def cmd_ifconfig(self, args: list = None) -> str:
        """Show network interface configuration"""
        lines = ["=" * 60, "NETWORK INTERFACES", "=" * 60]
        
        for adapter in self.network_interface.list_adapters():
            lines.append("")
            lines.append(self.network_interface.format_adapter_info(adapter))
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def cmd_ipconfig(self, args: list = None) -> str:
        """Alias for ifconfig (Windows-style)"""
        return self.cmd_ifconfig(args)
    
    def cmd_hostname(self, args: list = None) -> str:
        """Show system hostname"""
        return self.network_interface.get_hostname()
    
    def cmd_netinfo(self, args: list = None) -> str:
        """Show network information"""
        info = self.network_interface.get_platform_info()
        
        lines = [
            "=" * 60,
            "NETWORK INFORMATION",
            "=" * 60,
            f"Hostname: {info['hostname']}",
            f"Platform: {info['platform']}",
            f"Local IP: {info['local_ip']}",
            f"Total Adapters: {info['adapters']}",
            f"Active Adapters: {info['active_adapters']}",
            "=" * 60
        ]
        
        return "\n".join(lines)
    
    def cmd_ports(self, args: list = None) -> str:
        """Show listening ports"""
        return self.network_monitor.format_listening_ports()
    
    def cmd_netstats(self, args: list = None) -> str:
        """Show network statistics"""
        stats = self.network_monitor.get_connection_stats()
        
        lines = [
            "=" * 60,
            "NETWORK STATISTICS",
            "=" * 60,
            f"Total Connections: {stats['total_connections']}",
            f"Listening Ports: {stats['listening_ports']}",
            ""
        ]
        
        if stats['by_state']:
            lines.append("Connections by State:")
            for state, count in stats['by_state'].items():
                lines.append(f"  {state}: {count}")
            lines.append("")
        
        if stats['by_protocol']:
            lines.append("Connections by Protocol:")
            for protocol, count in stats['by_protocol'].items():
                lines.append(f"  {protocol}: {count}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def cmd_checkport(self, args: list = None) -> str:
        """Check if a port is open"""
        if not args or len(args) < 2:
            return "Usage: checkport <host> <port>"
        
        host = args[0]
        try:
            port = int(args[1])
        except ValueError:
            return f"Error: Invalid port number: {args[1]}"
        
        result = self.network_tools.check_port(host, port)
        service = self.network_tools.get_service_name(port)
        
        status = "OPEN" if result['open'] else "CLOSED"
        return f"Port {port} ({service}) on {host}: {status}"
    
    # API Methods for other layers
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        return self.network_interface.get_local_ip()
    
    def get_hostname(self) -> str:
        """Get hostname"""
        return self.network_interface.get_hostname()
    
    def add_connection(self, local_addr: str, local_port: int, remote_addr: str = None,
                      remote_port: int = None, state: str = "ESTABLISHED"):
        """Add a network connection"""
        return self.network_monitor.add_connection(
            local_addr, local_port, remote_addr, remote_port, state
        )
    
    def get_commands(self) -> dict:
        """Get available network commands"""
        return {
            'ping': {
                'function': self.cmd_ping,
                'description': 'Ping a host',
                'usage': 'ping <host> [count] [timeout]'
            },
            'netstat': {
                'function': self.cmd_netstat,
                'description': 'Show network connections',
                'usage': 'netstat'
            },
            'ifconfig': {
                'function': self.cmd_ifconfig,
                'description': 'Show network interfaces',
                'usage': 'ifconfig'
            },
            'ipconfig': {
                'function': self.cmd_ipconfig,
                'description': 'Show network interfaces (Windows-style)',
                'usage': 'ipconfig'
            },
            'hostname': {
                'function': self.cmd_hostname,
                'description': 'Show system hostname',
                'usage': 'hostname'
            },
            'netinfo': {
                'function': self.cmd_netinfo,
                'description': 'Show network information',
                'usage': 'netinfo'
            },
            'ports': {
                'function': self.cmd_ports,
                'description': 'Show listening ports',
                'usage': 'ports'
            },
            'netstats': {
                'function': self.cmd_netstats,
                'description': 'Show network statistics',
                'usage': 'netstats'
            },
            'checkport': {
                'function': self.cmd_checkport,
                'description': 'Check if a port is open',
                'usage': 'checkport <host> <port>'
            }
        }
