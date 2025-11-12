"""
Network Tools
Provides ping, traceroute, and other network utilities.
"""

import socket
import subprocess
import platform
import time
from typing import Optional, Dict
from datetime import datetime


class NetworkTools:
    """Network utility tools"""
    
    def __init__(self):
        self.ping_history = []
        self.max_history = 100
    
    def ping(self, host: str, count: int = 4, timeout: int = 5) -> dict:
        """Ping a host"""
        result = {
            'host': host,
            'timestamp': datetime.now().isoformat(),
            'packets_sent': count,
            'packets_received': 0,
            'packet_loss': 100.0,
            'min_rtt': None,
            'max_rtt': None,
            'avg_rtt': None,
            'success': False,
            'error': None,
            'responses': []
        }
        
        try:
            # Try to resolve hostname first
            try:
                ip = socket.gethostbyname(host)
                result['ip_address'] = ip
            except socket.gaierror:
                result['error'] = f"Cannot resolve hostname: {host}"
                return result
            
            # Perform ping using system command
            system = platform.system().lower()
            
            if system == "windows":
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
            
            try:
                output = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout * count + 5
                )
                
                # Parse output
                if output.returncode == 0:
                    result['success'] = True
                    result['packets_received'] = count
                    result['packet_loss'] = 0.0
                    
                    # Try to extract RTT values (simplified)
                    lines = output.stdout.split('\n')
                    rtts = []
                    
                    for line in lines:
                        if 'time=' in line.lower() or 'time<' in line.lower():
                            try:
                                # Extract time value
                                time_part = line.split('time')[-1]
                                time_val = ''.join(c for c in time_part if c.isdigit() or c == '.')
                                if time_val:
                                    rtts.append(float(time_val))
                            except:
                                pass
                    
                    if rtts:
                        result['min_rtt'] = min(rtts)
                        result['max_rtt'] = max(rtts)
                        result['avg_rtt'] = sum(rtts) / len(rtts)
                        result['responses'] = rtts
                else:
                    result['error'] = "Host unreachable or timeout"
                    
            except subprocess.TimeoutExpired:
                result['error'] = "Ping timeout"
            except FileNotFoundError:
                # Fallback: simulate ping using socket
                result = self._socket_ping(host, count, timeout)
                
        except Exception as e:
            result['error'] = str(e)
        
        # Store in history
        self.ping_history.append(result)
        if len(self.ping_history) > self.max_history:
            self.ping_history = self.ping_history[-self.max_history:]
        
        return result
    
    def _socket_ping(self, host: str, count: int, timeout: int) -> dict:
        """Fallback ping using socket connection"""
        result = {
            'host': host,
            'timestamp': datetime.now().isoformat(),
            'packets_sent': count,
            'packets_received': 0,
            'packet_loss': 100.0,
            'success': False,
            'responses': [],
            'method': 'socket'
        }
        
        try:
            ip = socket.gethostbyname(host)
            result['ip_address'] = ip
            
            successful_pings = 0
            rtts = []
            
            for i in range(count):
                try:
                    start_time = time.time()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    sock.connect((ip, 80))  # Try HTTP port
                    sock.close()
                    rtt = (time.time() - start_time) * 1000  # Convert to ms
                    rtts.append(rtt)
                    successful_pings += 1
                except:
                    pass
                
                if i < count - 1:
                    time.sleep(0.5)
            
            result['packets_received'] = successful_pings
            result['packet_loss'] = ((count - successful_pings) / count) * 100
            result['success'] = successful_pings > 0
            
            if rtts:
                result['min_rtt'] = min(rtts)
                result['max_rtt'] = max(rtts)
                result['avg_rtt'] = sum(rtts) / len(rtts)
                result['responses'] = rtts
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def check_port(self, host: str, port: int, timeout: int = 3) -> dict:
        """Check if a port is open"""
        result = {
            'host': host,
            'port': port,
            'open': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result_code = sock.connect_ex((host, port))
            sock.close()
            
            result['open'] = result_code == 0
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_service_name(self, port: int) -> str:
        """Get common service name for port"""
        common_ports = {
            20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'TELNET',
            25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
            143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 3306: 'MySQL',
            3389: 'RDP', 5432: 'PostgreSQL', 6379: 'Redis',
            8080: 'HTTP-ALT', 27017: 'MongoDB'
        }
        return common_ports.get(port, 'UNKNOWN')
    
    def format_ping_result(self, result: dict) -> str:
        """Format ping result for display"""
        lines = [f"PING {result['host']}"]
        
        if 'ip_address' in result:
            lines[0] += f" ({result['ip_address']})"
        
        if result.get('error'):
            lines.append(f"Error: {result['error']}")
            return "\n".join(lines)
        
        if result['success']:
            lines.append(f"{result['packets_received']} packets transmitted, "
                        f"{result['packets_received']} received, "
                        f"{result['packet_loss']:.1f}% packet loss")
            
            if result.get('avg_rtt'):
                lines.append(f"rtt min/avg/max = "
                           f"{result['min_rtt']:.2f}/"
                           f"{result['avg_rtt']:.2f}/"
                           f"{result['max_rtt']:.2f} ms")
        else:
            lines.append(f"0 packets received, 100% packet loss")
        
        return "\n".join(lines)
    
    def get_ping_history(self, limit: int = 10) -> list:
        """Get ping history"""
        return self.ping_history[-limit:]
