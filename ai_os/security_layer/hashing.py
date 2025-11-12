"""
Hashing Manager
Provides hashing and password verification services.
"""

import hashlib
import os
import hmac
from typing import Optional


class HashingManager:
    """Manages hashing operations"""
    
    def __init__(self):
        self.salt_length = 32
    
    def generate_salt(self, length: Optional[int] = None) -> bytes:
        """Generate a random salt"""
        if length is None:
            length = self.salt_length
        return os.urandom(length)
    
    def hash_sha256(self, data: str) -> str:
        """Hash data using SHA256"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def hash_sha512(self, data: str) -> str:
        """Hash data using SHA512"""
        return hashlib.sha512(data.encode()).hexdigest()
    
    def hash_md5(self, data: str) -> str:
        """Hash data using MD5 (not recommended for security)"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hash a password with salt using PBKDF2
        Returns (hash, salt)
        """
        if salt is None:
            salt = self.generate_salt()
        
        # Use PBKDF2 with SHA256
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000  # iterations
        )
        
        return hash_obj.hex(), salt.hex()
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify a password against a stored hash"""
        try:
            # Convert salt back to bytes
            salt_bytes = bytes.fromhex(salt)
            
            # Hash the provided password
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt_bytes,
                100000
            )
            
            # Compare hashes
            return hash_obj.hex() == stored_hash
        except Exception:
            return False
    
    def hash_file(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Hash a file"""
        if algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'sha512':
            hasher = hashlib.sha512()
        elif algorithm == 'md5':
            hasher = hashlib.md5()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def hmac_sign(self, message: str, key: str, algorithm: str = 'sha256') -> str:
        """Create HMAC signature"""
        if algorithm == 'sha256':
            digest = hashlib.sha256
        elif algorithm == 'sha512':
            digest = hashlib.sha512
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        signature = hmac.new(
            key.encode(),
            message.encode(),
            digest
        ).hexdigest()
        
        return signature
    
    def hmac_verify(self, message: str, signature: str, key: str, 
                   algorithm: str = 'sha256') -> bool:
        """Verify HMAC signature"""
        expected = self.hmac_sign(message, key, algorithm)
        return hmac.compare_digest(expected, signature)
    
    def checksum(self, data: str) -> str:
        """Generate simple checksum"""
        return self.hash_sha256(data)
    
    def verify_checksum(self, data: str, checksum: str) -> bool:
        """Verify checksum"""
        return self.checksum(data) == checksum
