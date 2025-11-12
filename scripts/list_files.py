import os
import base64
import sqlite3
import time
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path

# Configuration
DISK_NAME = 'MainDisk'  # The name of your VFS disk
DATA_DIR = os.path.join('vfs_storage', DISK_NAME, 'data')

def generate_key(password: str) -> bytes:
    """Generate encryption key from password using the same method as StorageAdapter."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'ai_os_vfs_salt_2024',  # Same salt as in StorageAdapter
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def decrypt_file(file_path, cipher_suite):
    """Decrypt the content of a file."""
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
            try:
                return cipher_suite.decrypt(encrypted_data).decode('utf-8')
            except Exception as e:
                return f"[Error decrypting: {str(e)}]"
    except Exception as e:
        return f"[Error reading file: {str(e)}]"

def list_directory(directory, cipher_suite, indent=0):
    """Recursively list directory contents and file contents."""
    try:
        items = sorted(os.listdir(directory))
        for item in items:
            item_path = os.path.join(directory, item)
            display_name = item.replace('.enc', '') if item.endswith('.enc') else item
            
            # Print the item name
            print('  ' * indent + f"📄 {display_name}" if os.path.isfile(item_path) else f"📁 {display_name}")
            
            # If it's a file and we can decrypt it, show preview
            if os.path.isfile(item_path) and item.endswith('.enc'):
                content = decrypt_file(item_path, cipher_suite)
                preview = (content[:100] + '...') if len(content) > 100 else content
                print('  ' * (indent + 1) + f"Content: {preview}")
            # If it's a directory, recurse into it
            elif os.path.isdir(item_path):
                list_directory(item_path, cipher_suite, indent + 1)
    except Exception as e:
        print('  ' * indent + f"[Error accessing {directory}: {str(e)}]")

def init_database():
    """Initialize the SQLite database."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_metadata.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        size INTEGER DEFAULT 0,
        parent_path TEXT,
        created_at REAL,
        modified_at REAL,
        content_preview TEXT,
        is_encrypted BOOLEAN DEFAULT 1,
        encryption_status TEXT,
        last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create index for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_path)')
    
    conn.commit()
    return conn

def save_to_database(conn, file_info):
    """Save file information to the database."""
    cursor = conn.cursor()
    
    # Check if the file already exists
    cursor.execute('SELECT id FROM files WHERE path = ?', (file_info['path'],))
    exists = cursor.fetchone()
    
    if exists:
        # Update existing record
        cursor.execute('''
        UPDATE files 
        SET name = ?, type = ?, size = ?, parent_path = ?, 
            modified_at = ?, content_preview = ?, 
            is_encrypted = ?, encryption_status = ?, last_scanned = CURRENT_TIMESTAMP
        WHERE path = ?
        ''', (
            file_info['name'], file_info['type'], file_info['size'], 
            file_info['parent_path'], file_info['modified_at'], 
            file_info['content_preview'], file_info['is_encrypted'],
            file_info['encryption_status'], file_info['path']
        ))
    else:
        # Insert new record
        cursor.execute('''
        INSERT INTO files 
        (path, name, type, size, parent_path, created_at, modified_at, 
         content_preview, is_encrypted, encryption_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_info['path'], file_info['name'], file_info['type'], 
            file_info['size'], file_info['parent_path'], 
            file_info.get('created_at', time.time()),
            file_info['modified_at'], 
            file_info['content_preview'], 
            file_info['is_encrypted'],
            file_info['encryption_status']
        ))
    
    conn.commit()

def list_directory(directory, cipher_suite, indent=0, conn=None):
    """Recursively list directory contents and file contents."""
    try:
        items = sorted(os.listdir(directory))
        for item in items:
            item_path = os.path.join(directory, item)
            rel_path = os.path.relpath(item_path, os.path.dirname(os.path.dirname(DATA_DIR)))
            
            # Skip the .db file to avoid reading our own database
            if item.endswith('.db'):
                continue
                
            is_encrypted = item.endswith('.enc')
            display_name = item.replace('.enc', '') if is_encrypted else item
            is_dir = os.path.isdir(item_path)
            
            # Get file stats
            try:
                stat = os.stat(item_path)
                file_size = stat.st_size
                modified_time = stat.st_mtime
                created_time = stat.st_ctime
            except Exception as e:
                print(f"  " * indent + f"[Error getting stats for {item_path}: {str(e)}]")
                continue
            
            # Prepare file info for database
            file_info = {
                'path': rel_path.replace('\\', '/'),  # Use forward slashes for consistency
                'name': display_name,
                'type': 'directory' if is_dir else 'file',
                'size': 0 if is_dir else file_size,
                'parent_path': os.path.dirname(rel_path).replace('\\', '/') or '/',
                'created_at': created_time,
                'modified_at': modified_time,
                'content_preview': '',
                'is_encrypted': is_encrypted,
                'encryption_status': 'encrypted' if is_encrypted else 'not_encrypted'
            }
            
            # If it's a file and we can decrypt it, show preview
            if not is_dir and is_encrypted:
                try:
                    with open(item_path, 'rb') as f:
                        encrypted_data = f.read()
                        try:
                            decrypted = cipher_suite.decrypt(encrypted_data).decode('utf-8')
                            preview = (decrypted[:200] + '...') if len(decrypted) > 200 else decrypted
                            file_info['content_preview'] = preview
                            print('  ' * indent + f"📄 {display_name}")
                            print('  ' * (indent + 1) + f"Content: {preview}")
                        except Exception as e:
                            file_info['encryption_status'] = f'decryption_error: {str(e)}'
                            print('  ' * indent + f"📄 {display_name} [Error decrypting: {str(e)}]")
                except Exception as e:
                    file_info['encryption_status'] = f'read_error: {str(e)}'
                    print('  ' * indent + f"📄 {display_name} [Error reading file: {str(e)}]")
            elif not is_dir:
                try:
                    with open(item_path, 'r', encoding='utf-8') as f:
                        content = f.read(500)  # Read first 500 chars for preview
                        file_info['content_preview'] = content
                        print('  ' * indent + f"📄 {display_name}")
                        print('  ' * (indent + 1) + f"Content: {content[:200]}...")
                except Exception as e:
                    file_info['encryption_status'] = f'read_error: {str(e)}'
                    print('  ' * indent + f"📄 {display_name} [Error reading file: {str(e)}]")
            else:
                print('  ' * indent + f"📁 {display_name}")
            
            # Save to database
            if conn:
                save_to_database(conn, file_info)
            
            # If it's a directory, recurse into it
            if is_dir:
                list_directory(item_path, cipher_suite, indent + 1, conn)
                
    except Exception as e:
        print('  ' * indent + f"[Error accessing {directory}: {str(e)}]")

def main():
    # Initialize database
    print("Initializing database...")
    conn = init_database()
    
    try:
        # Initialize Fernet cipher
        try:
            encryption_key = generate_key(DISK_NAME)
            cipher_suite = Fernet(encryption_key)
        except Exception as e:
            print(f"Error initializing encryption: {e}")
            return
        
        # Get absolute path to the data directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(base_dir), DATA_DIR)
        
        if not os.path.exists(data_dir):
            print(f"Error: Directory not found: {data_dir}")
            return
        
        print(f"\n📂 Scanning {os.path.basename(data_dir)}/...\n")
        
        # Start scanning
        start_time = time.time()
        list_directory(data_dir, cipher_suite, 0, conn)
        
        # Print summary
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM files WHERE type = "directory"')
        total_dirs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM files WHERE is_encrypted = 1')
        encrypted_files = cursor.fetchone()[0]
        
        print(f"\n✅ Scan completed in {time.time() - start_time:.2f} seconds")
        print(f"📊 Summary:")
        print(f"   - Total files: {total_files - total_dirs}")
        print(f"   - Directories: {total_dirs}")
        print(f"   - Encrypted files: {encrypted_files}")
        print(f"\n💾 Database saved to: {os.path.abspath('file_metadata.db')}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
