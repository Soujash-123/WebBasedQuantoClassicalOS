"""
System Device Monitor
Detects and monitors real system devices (battery, network, USB, etc.)
"""

import platform
import subprocess
from typing import Dict, Any, List, Optional


class SystemDeviceMonitor:
    """Monitors and detects real system devices."""
    
    def __init__(self):
        """Initialize the system device monitor."""
        self.os_type = platform.system()
        self.has_psutil = self._check_psutil()
        print(f"[SystemDeviceMonitor] Initialized for {self.os_type}")
        if not self.has_psutil:
            print("[SystemDeviceMonitor] Warning: psutil not available. Some features will be limited.")
    
    def _check_psutil(self) -> bool:
        """Check if psutil is available."""
        try:
            import psutil
            return True
        except ImportError:
            return False
    
    def get_battery_status(self) -> Optional[Dict[str, Any]]:
        """
        Get battery status information.
        
        Returns:
            Dictionary with battery info or None if not available
        """
        if not self.has_psutil:
            return {"available": False, "message": "psutil not installed"}
        
        try:
            import psutil
            battery = psutil.sensors_battery()
            
            if battery is None:
                return {"available": False, "message": "No battery detected"}
            
            return {
                "available": True,
                "percent": battery.percent,
                "charging": battery.power_plugged,
                "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "N/A"
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_network_interfaces(self) -> Dict[str, Any]:
        """
        Get network interface information.
        
        Returns:
            Dictionary with network interface details
        """
        if not self.has_psutil:
            return {"available": False, "message": "psutil not installed"}
        
        try:
            import psutil
            interfaces = {}
            
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addresses in net_if_addrs.items():
                interface_info = {
                    "addresses": [],
                    "is_up": net_if_stats[interface_name].isup if interface_name in net_if_stats else False
                }
                
                for addr in addresses:
                    if addr.family == 2:  # AF_INET (IPv4)
                        interface_info["addresses"].append({
                            "type": "IPv4",
                            "address": addr.address,
                            "netmask": addr.netmask
                        })
                    elif addr.family == 23:  # AF_INET6 (IPv6)
                        interface_info["addresses"].append({
                            "type": "IPv6",
                            "address": addr.address
                        })
                
                if interface_info["addresses"]:
                    interfaces[interface_name] = interface_info
            
            return {
                "available": True,
                "interfaces": interfaces,
                "count": len(interfaces)
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_usb_devices(self) -> Dict[str, Any]:
        """
        Get list of connected USB devices.
        
        Returns:
            Dictionary with USB device information
        """
        devices = []
        
        try:
            if self.os_type == "Linux":
                devices = self._get_usb_linux()
            elif self.os_type == "Windows":
                devices = self._get_usb_windows()
            elif self.os_type == "Darwin":  # macOS
                devices = self._get_usb_macos()
            else:
                return {"available": False, "message": f"USB detection not supported on {self.os_type}"}
            
            return {
                "available": True,
                "devices": devices,
                "count": len(devices)
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _get_usb_linux(self) -> List[str]:
        """Get USB devices on Linux using lsusb."""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return [line.split('ID')[1].strip() if 'ID' in line else line for line in lines if line]
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def _get_usb_windows(self) -> List[str]:
        """Get USB devices on Windows using wmic."""
        try:
            result = subprocess.run(
                ['wmic', 'path', 'Win32_USBHub', 'get', 'Description'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                return [line.strip() for line in lines if line.strip()]
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def _get_usb_macos(self) -> List[str]:
        """Get USB devices on macOS using system_profiler."""
        try:
            result = subprocess.run(
                ['system_profiler', 'SPUSBDataType'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Simple parsing - look for device names
                lines = result.stdout.split('\n')
                devices = []
                for line in lines:
                    if ':' in line and 'Product ID' not in line:
                        device_name = line.split(':')[0].strip()
                        if device_name and not device_name.startswith(' '):
                            devices.append(device_name)
                return devices
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        if not self.has_psutil:
            return {
                "available": True,
                "count": "N/A",
                "usage": "N/A",
                "message": "psutil not installed - limited info"
            }
        
        try:
            import psutil
            return {
                "available": True,
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "usage_percent": psutil.cpu_percent(interval=0.1),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        if not self.has_psutil:
            return {"available": False, "message": "psutil not installed"}
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "available": True,
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        if not self.has_psutil:
            return {"available": False, "message": "psutil not installed"}
        
        try:
            import psutil
            partitions = psutil.disk_partitions()
            disk_info = {}
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                except PermissionError:
                    continue
            
            return {
                "available": True,
                "partitions": disk_info,
                "count": len(disk_info)
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive system device summary.
        
        Returns:
            Dictionary with all system information
        """
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "battery": self.get_battery_status(),
            "network": self.get_network_interfaces(),
            "usb": self.get_usb_devices(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info()
        }
