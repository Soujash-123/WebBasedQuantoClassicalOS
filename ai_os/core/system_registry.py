"""
System Registry
Central registry for tracking loaded modules and components.
"""

from typing import Any, Dict, Optional, List


class SystemRegistry:
    """Central registry for managing system modules and components."""
    
    def __init__(self):
        """Initialize the System Registry."""
        self.modules: Dict[str, Any] = {}
        print("[SystemRegistry] System Registry initialized")
    
    def register_module(self, name: str, instance: Any) -> bool:
        """
        Register a module in the system.
        
        Args:
            name: Unique name for the module
            instance: Module instance to register
            
        Returns:
            True if registration successful, False if module already exists
        """
        if name in self.modules:
            print(f"[SystemRegistry] Warning: Module '{name}' already registered. Skipping.")
            return False
        
        self.modules[name] = instance
        print(f"[SystemRegistry] Module '{name}' registered successfully")
        return True
    
    def get_module(self, name: str) -> Optional[Any]:
        """
        Retrieve a registered module.
        
        Args:
            name: Name of the module to retrieve
            
        Returns:
            Module instance or None if not found
        """
        if name not in self.modules:
            print(f"[SystemRegistry] Warning: Module '{name}' not found")
            return None
        
        return self.modules[name]
    
    def deregister_module(self, name: str) -> bool:
        """
        Remove a module from the registry.
        
        Args:
            name: Name of the module to remove
            
        Returns:
            True if deregistration successful, False if module not found
        """
        if name not in self.modules:
            print(f"[SystemRegistry] Warning: Module '{name}' not found for deregistration")
            return False
        
        del self.modules[name]
        print(f"[SystemRegistry] Module '{name}' deregistered successfully")
        return True
    
    def list_modules(self) -> List[str]:
        """
        Get list of all registered module names.
        
        Returns:
            List of registered module names
        """
        return list(self.modules.keys())
    
    def is_registered(self, name: str) -> bool:
        """
        Check if a module is registered.
        
        Args:
            name: Name of the module to check
            
        Returns:
            True if module is registered, False otherwise
        """
        return name in self.modules
    
    def clear_registry(self) -> None:
        """Clear all registered modules."""
        count = len(self.modules)
        self.modules.clear()
        print(f"[SystemRegistry] Registry cleared. {count} module(s) removed")
