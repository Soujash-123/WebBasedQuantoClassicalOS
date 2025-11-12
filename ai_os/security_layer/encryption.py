"""
Encryption Manager
Provides file and data encryption/decryption services.
"""

import os
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class EncryptionManager:
    """Manages encryption and decryption operations"""
    
    def __init__(self):
        self.keys = {}  # Store encryption keys
        self.default_key = None
    
    def generate_key(self, password: Optional[str] = None, salt: Optional[bytes] = None) -> bytes:
        """Generate an encryption key"""
        if password:
            # Derive key from password
            if salt is None:
                salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key, salt
        else:
            # Generate random key
            return Fernet.generate_key(), None
    
    def set_default_key(self, key: bytes):
        """Set default encryption key"""
        self.default_key = key
    
    def store_key(self, name: str, key: bytes):
        """Store a named encryption key"""
        self.keys[name] = key
    
    def get_key(self, name: Optional[str] = None) -> Optional[bytes]:
        """Get encryption key by name or default"""
        if name:
            return self.keys.get(name)
        return self.default_key
    
    def encrypt_data(self, data: Union[str, bytes], key: Optional[bytes] = None) -> bytes:
        """Encrypt data"""
        if key is None:
            key = self.default_key
        
        if key is None:
            raise ValueError("No encryption key available")
        
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode()
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        return encrypted
    
    def decrypt_data(self, encrypted_data: bytes, key: Optional[bytes] = None) -> bytes:
        """Decrypt data"""
        if key is None:
            key = self.default_key
        
        if key is None:
            raise ValueError("No encryption key available")
        
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data)
        return decrypted
    
    def encrypt_file(self, input_file: str, output_file: Optional[str] = None, 
                    key: Optional[bytes] = None) -> str:
        """Encrypt a file"""
        if output_file is None:
            output_file = input_file + ".encrypted"
        
        # Read file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Encrypt
        encrypted = self.encrypt_data(data, key)
        
        # Write encrypted file
        with open(output_file, 'wb') as f:
            f.write(encrypted)
        
        return output_file
    
    def decrypt_file(self, input_file: str, output_file: Optional[str] = None,
                    key: Optional[bytes] = None) -> str:
        """Decrypt a file"""
        if output_file is None:
            if input_file.endswith('.encrypted'):
                output_file = input_file[:-10]  # Remove .encrypted
            else:
                output_file = input_file + ".decrypted"
        
        # Read encrypted file
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        decrypted = self.decrypt_data(encrypted_data, key)
        
        # Write decrypted file
        with open(output_file, 'wb') as f:
            f.write(decrypted)
        
        return output_file
    
    def encrypt_string(self, text: str, key: Optional[bytes] = None) -> str:
        """Encrypt a string and return base64 encoded result"""
        encrypted = self.encrypt_data(text, key)
        return base64.b64encode(encrypted).decode()
    
    def decrypt_string(self, encrypted_text: str, key: Optional[bytes] = None) -> str:
        """Decrypt a base64 encoded string"""
        encrypted_bytes = base64.b64decode(encrypted_text.encode())
        decrypted = self.decrypt_data(encrypted_bytes, key)
        return decrypted.decode()
    
    def key_to_string(self, key: bytes) -> str:
        """Convert key to string for storage"""
        return base64.b64encode(key).decode()
    
    def string_to_key(self, key_string: str) -> bytes:
        """Convert string back to key"""
        return base64.b64decode(key_string.encode())
