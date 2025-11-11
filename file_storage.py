import os
import sqlite3
from pathlib import Path

def init_db(db_path='file_storage.db'):
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS directories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        parent_id INTEGER,
        name TEXT NOT NULL,
        created REAL,
        modified REAL,
        FOREIGN KEY (parent_id) REFERENCES directories (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        directory_id INTEGER,
        name TEXT NOT NULL,
        path TEXT UNIQUE NOT NULL,
        extension TEXT,
        size INTEGER,
        created REAL,
        modified REAL,
        content TEXT,
        FOREIGN KEY (directory_id) REFERENCES directories (id)
    )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_directories_path ON directories(path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)')
    
    conn.commit()
    return conn

def get_or_create_directory(conn, dir_path, parent_id=None):
    """Get directory ID or create it if it doesn't exist."""
    cursor = conn.cursor()
    path = str(Path(dir_path).resolve())
    name = os.path.basename(path)
    
    # Try to get existing directory
    cursor.execute('SELECT id FROM directories WHERE path = ?', (path,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Create new directory record
    cursor.execute('''
    INSERT INTO directories (path, parent_id, name, created, modified)
    VALUES (?, ?, ?, strftime('%s','now'), strftime('%s','now'))
    ''', (path, parent_id, name))
    
    return cursor.lastrowid

def process_file(conn, file_path, dir_id):
    """Process a single file and store its metadata and content."""
    try:
        path_obj = Path(file_path)
        stats = path_obj.stat()
        
        # Read file content (for text files only)
        content = ''
        try:
            # Only read text files less than 1MB
            if stats.st_size < 1024 * 1024:  # 1MB limit
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except (UnicodeDecodeError, PermissionError):
            # Skip binary files or files we can't read
            pass
        
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO files 
        (directory_id, name, path, extension, size, created, modified, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dir_id,
            path_obj.name,
            str(path_obj.resolve()),
            path_obj.suffix.lower(),
            stats.st_size,
            stats.st_ctime,
            stats.st_mtime,
            content if len(content) < 5 * 1024 * 1024 else ''  # 5MB limit
        ))
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def scan_directory(conn, root_path):
    """Recursively scan directory and store file information."""
    root_path = Path(root_path).resolve()
    
    # Get or create root directory
    root_id = get_or_create_directory(conn, root_path)
    
    # Walk through all directories and files
    for dirpath, dirnames, filenames in os.walk(root_path):
        try:
            # Skip virtual environments and other non-essential directories
            if any(d in dirpath for d in ['__pycache__', 'node_modules', '.git', 'venv', '.venv']):
                continue
                
            # Get or create current directory
            dir_id = get_or_create_directory(conn, dirpath, root_id)
            
            # Process files in current directory
            for filename in filenames:
                file_path = Path(dirpath) / filename
                process_file(conn, file_path, dir_id)
                
            # Commit after processing each directory
            conn.commit()
            
        except Exception as e:
            print(f"Error processing directory {dirpath}: {e}")
            continue

def main():
    # Initialize database
    db_path = 'file_storage.db'
    print(f"Initializing database at {db_path}...")
    conn = init_db(db_path)
    
    try:
        # Get the project root directory (one level up from the script)
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        print(f"Scanning directory: {project_root}")
        scan_directory(conn, project_root)
        
        # Print some stats
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM files')
        file_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM directories')
        dir_count = cursor.fetchone()[0]
        
        print(f"\nScan complete!")
        print(f"Directories processed: {dir_count}")
        print(f"Files processed: {file_count}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
