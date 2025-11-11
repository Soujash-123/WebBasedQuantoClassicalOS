"""
Custom Commands Module
Add your custom commands here - they will hot reload!
"""


def cmd_hello(args=None):
    """Say hello to someone"""
    name = args[0] if args else "World"
    return f"Hello, {name}! 👋"


def cmd_greet(args=None):
    """Greet with a message"""
    if not args:
        return "Usage: greet <name>"
    name = args[0]
    return f"Greetings, {name}! Welcome to AI OS! 🎉"


def cmd_echo(args=None):
    """Echo back the arguments"""
    if not args:
        return "Usage: echo <message>"
    return " ".join(args)


def cmd_time(args=None):
    """Show current time"""
    from datetime import datetime
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def cmd_calc(args=None):
    """Simple calculator"""
    if not args or len(args) < 3:
        return "Usage: calc <num1> <op> <num2>\nExample: calc 5 + 3"
    
    try:
        num1 = float(args[0])
        op = args[1]
        num2 = float(args[2])
        
        if op == '+':
            result = num1 + num2
        elif op == '-':
            result = num1 - num2
        elif op == '*':
            result = num1 * num2
        elif op == '/':
            if num2 == 0:
                return "Error: Division by zero"
            result = num1 / num2
        else:
            return f"Unknown operator: {op}"
        
        return f"{num1} {op} {num2} = {result}"
    except ValueError:
        return "Error: Invalid numbers"


def cmd_grep(args=None):
    """Search for pattern in files"""
    if not args or len(args) < 2:
        return """Usage: grep <pattern> <file>
Options:
  grep <pattern> <file>     - Search for pattern in file
  grep -i <pattern> <file>  - Case-insensitive search
  grep -n <pattern> <file>  - Show line numbers
  grep -c <pattern> <file>  - Count matches only

Examples:
  grep hello test.txt
  grep -i HELLO test.txt
  grep -n "error" log.txt"""
    
    # Parse options
    case_sensitive = True
    show_line_numbers = False
    count_only = False
    pattern_idx = 0
    
    # Check for flags
    while pattern_idx < len(args) and args[pattern_idx].startswith('-'):
        flag = args[pattern_idx]
        if flag == '-i':
            case_sensitive = False
        elif flag == '-n':
            show_line_numbers = True
        elif flag == '-c':
            count_only = True
        pattern_idx += 1
    
    if pattern_idx >= len(args) - 1:
        return "Error: Missing pattern or file\nUsage: grep [options] <pattern> <file>"
    
    pattern = args[pattern_idx]
    filepath = args[pattern_idx + 1]
    
    # Get VFS manager from os_master
    try:
        # Import the unified client to get VFS access
        # This is a workaround - ideally we'd pass VFS as a parameter
        from ai_os.filesystem.vfs_master import VFSLayer
        
        # For now, we'll create a temporary VFS instance
        # In production, you'd get this from the running system
        vfs = VFSLayer()
        
        # Read the file
        content = vfs.vfs_manager.read(filepath)
        
        if content is None:
            return f"grep: {filepath}: No such file or directory"
        
        # Search for pattern
        lines = content.split('\n')
        matches = []
        match_count = 0
        
        for line_num, line in enumerate(lines, 1):
            # Perform search
            search_line = line if case_sensitive else line.lower()
            search_pattern = pattern if case_sensitive else pattern.lower()
            
            if search_pattern in search_line:
                match_count += 1
                if not count_only:
                    if show_line_numbers:
                        matches.append(f"{line_num}:{line}")
                    else:
                        matches.append(line)
        
        # Return results
        if count_only:
            return str(match_count)
        
        if not matches:
            return ""  # grep returns nothing if no matches
        
        return "\n".join(matches)
        
    except Exception as e:
        return f"grep: {filepath}: {str(e)}"


def cmd_find(args=None):
    """Find files in VFS"""
    if not args:
        return """Usage: find <path> [options]
Options:
  find <path>              - List all files in path
  find <path> -name <pattern> - Find files matching pattern

Examples:
  find /
  find /home -name "*.txt"
  find / -name test"""
    
    path = args[0]
    name_pattern = None
    
    # Parse options
    i = 1
    while i < len(args):
        if args[i] == '-name' and i + 1 < len(args):
            name_pattern = args[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        from ai_os.filesystem.vfs_master import VFSLayer
        vfs = VFSLayer()
        
        # Recursive search
        results = []
        
        def search_recursive(current_path):
            try:
                files = vfs.vfs_manager.ls(current_path)
                for file in files:
                    file_path = file['path']
                    file_name = file['name']
                    
                    # Check if matches pattern
                    if name_pattern:
                        # Simple pattern matching
                        if '*' in name_pattern:
                            # Wildcard matching
                            pattern_parts = name_pattern.split('*')
                            matches = all(part in file_name for part in pattern_parts if part)
                        else:
                            # Exact match
                            matches = name_pattern in file_name
                        
                        if matches:
                            results.append(file_path)
                    else:
                        results.append(file_path)
                    
                    # Recurse into directories
                    if file['type'] == 'folder':
                        search_recursive(file_path)
            except:
                pass  # Skip inaccessible directories
        
        search_recursive(path)
        
        if not results:
            return f"find: No files found in {path}"
        
        return "\n".join(results)
        
    except Exception as e:
        return f"find: {path}: {str(e)}"


def cmd_python(args=None):
    """Python interpreter - execute Python code"""
    if not args:
        return """Python 3.x Interpreter
Usage: python <script.py> [args]
       python -c "<code>"  - Execute Python code directly
       python --version    - Show Python version

Examples:
  python script.py
  python -c "print('Hello, World!')"
  python -c "import math; print(math.pi)"

Note: Python is pre-installed in this AI OS."""
    
    import sys
    import subprocess
    from io import StringIO
    
    # Check for version flag
    if args[0] == '--version' or args[0] == '-V':
        return f"Python {sys.version}"
    
    # Execute code directly with -c flag
    if args[0] == '-c':
        if len(args) < 2:
            return "Error: -c option requires code argument"
        
        code = ' '.join(args[1:])
        
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # Execute the code
            exec(code)
            
            # Get output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            return output.strip() if output else "Code executed successfully"
        except Exception as e:
            sys.stdout = old_stdout
            return f"Python Error: {type(e).__name__}: {str(e)}"
    
    # Execute Python script file
    script_path = args[0]
    script_args = args[1:] if len(args) > 1 else []
    
    try:
        from ai_os.filesystem.vfs_master import VFSLayer
        vfs = VFSLayer()
        
        # Read the script
        script_content = vfs.vfs_manager.read(script_path)
        
        if script_content is None:
            return f"python: can't open file '{script_path}': No such file or directory"
        
        # Prepare execution environment
        old_stdout = sys.stdout
        old_argv = sys.argv
        sys.stdout = StringIO()
        sys.argv = [script_path] + script_args
        
        try:
            # Execute the script
            exec(script_content, {'__name__': '__main__'})
            
            # Get output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            sys.argv = old_argv
            
            return output.strip() if output else "Script executed successfully"
        except Exception as e:
            sys.stdout = old_stdout
            sys.argv = old_argv
            return f"Python Error in {script_path}:\n{type(e).__name__}: {str(e)}"
            
    except Exception as e:
        return f"python: {script_path}: {str(e)}"


def cmd_pip(args=None):
    """Python package manager (simulated)"""
    if not args:
        return """pip - Python Package Installer
Usage:
  pip install <package>   - Install a package
  pip uninstall <package> - Uninstall a package
  pip list                - List installed packages
  pip show <package>      - Show package information
  pip --version           - Show pip version

Examples:
  pip install requests
  pip list
  pip show numpy

Note: This is a simulated pip for the AI OS environment."""
    
    import sys
    
    command = args[0]
    
    if command == '--version' or command == '-V':
        return f"pip 24.0 from {sys.prefix}/lib/python/site-packages/pip (python {sys.version_info.major}.{sys.version_info.minor})"
    
    if command == 'list':
        # List some common pre-installed packages
        packages = [
            "pip                    24.0",
            "setuptools             69.0.0",
            "wheel                  0.42.0",
            "numpy                  1.26.0",
            "pandas                 2.1.0",
            "requests               2.31.0",
            "matplotlib             3.8.0",
            "scikit-learn           1.3.0",
            "tensorflow             2.15.0",
            "torch                  2.1.0"
        ]
        return "\n".join(packages)
    
    if command == 'install':
        if len(args) < 2:
            return "ERROR: You must give at least one requirement to install"
        
        package = args[1]
        return f"""Collecting {package}
  Downloading {package}-1.0.0-py3-none-any.whl (100 kB)
Installing collected packages: {package}
Successfully installed {package}-1.0.0

Note: Package installation simulated in AI OS environment."""
    
    if command == 'uninstall':
        if len(args) < 2:
            return "ERROR: You must give at least one requirement to uninstall"
        
        package = args[1]
        return f"""Found existing installation: {package} 1.0.0
Uninstalling {package}-1.0.0:
Successfully uninstalled {package}-1.0.0"""
    
    if command == 'show':
        if len(args) < 2:
            return "ERROR: Please provide a package name"
        
        package = args[1]
        return f"""Name: {package}
Version: 1.0.0
Summary: {package} package for AI OS
Home-page: https://pypi.org/project/{package}/
Author: Python Community
License: MIT
Location: /usr/local/lib/python3.x/site-packages
Requires: 
Required-by: """
    
    return f"ERROR: unknown command '{command}'"


def cmd_wc(args=None):
    """Count lines, words, and characters in files"""
    if not args:
        return """Usage: wc <file>
Options:
  wc <file>       - Show lines, words, and bytes
  wc -l <file>    - Count lines only
  wc -w <file>    - Count words only
  wc -c <file>    - Count characters only

Examples:
  wc test.txt
  wc -l log.txt"""
    
    # Parse options
    count_lines = False
    count_words = False
    count_chars = False
    file_idx = 0
    
    while file_idx < len(args) and args[file_idx].startswith('-'):
        flag = args[file_idx]
        if flag == '-l':
            count_lines = True
        elif flag == '-w':
            count_words = True
        elif flag == '-c':
            count_chars = True
        file_idx += 1
    
    if file_idx >= len(args):
        return "Error: Missing file\nUsage: wc [options] <file>"
    
    filepath = args[file_idx]
    
    # If no specific option, count all
    if not (count_lines or count_words or count_chars):
        count_lines = count_words = count_chars = True
    
    try:
        from ai_os.filesystem.vfs_master import VFSLayer
        vfs = VFSLayer()
        
        content = vfs.vfs_manager.read(filepath)
        
        if content is None:
            return f"wc: {filepath}: No such file or directory"
        
        lines = len(content.split('\n'))
        words = len(content.split())
        chars = len(content)
        
        result = []
        if count_lines:
            result.append(str(lines))
        if count_words:
            result.append(str(words))
        if count_chars:
            result.append(str(chars))
        
        result.append(filepath)
        return " ".join(result)
        
    except Exception as e:
        return f"wc: {filepath}: {str(e)}"


# Export commands for registration
CUSTOM_COMMANDS = {
    'hello': {
        'function': cmd_hello,
        'description': 'Say hello to someone',
        'usage': 'hello [name]',
        'layer': 'custom'
    },
    'greet': {
        'function': cmd_greet,
        'description': 'Greet with a message',
        'usage': 'greet <name>',
        'layer': 'custom'
    },
    'echo': {
        'function': cmd_echo,
        'description': 'Echo back the arguments',
        'usage': 'echo <message>',
        'layer': 'custom'
    },
    'time': {
        'function': cmd_time,
        'description': 'Show current time',
        'usage': 'time',
        'layer': 'custom'
    },
    'calc': {
        'function': cmd_calc,
        'description': 'Simple calculator',
        'usage': 'calc <num1> <op> <num2>',
        'layer': 'custom'
    },
    'grep': {
        'function': cmd_grep,
        'description': 'Search for pattern in files',
        'usage': 'grep [options] <pattern> <file>',
        'layer': 'custom'
    },
    'find': {
        'function': cmd_find,
        'description': 'Find files in VFS',
        'usage': 'find <path> [options]',
        'layer': 'custom'
    },
    'wc': {
        'function': cmd_wc,
        'description': 'Count lines, words, and characters',
        'usage': 'wc [options] <file>',
        'layer': 'custom'
    },
    'python': {
        'function': cmd_python,
        'description': 'Python interpreter - execute Python code',
        'usage': 'python <script.py> | python -c "<code>"',
        'layer': 'custom'
    },
    'pip': {
        'function': cmd_pip,
        'description': 'Python package manager',
        'usage': 'pip <command> [options]',
        'layer': 'custom'
    }
}


def on_reload():
    """Called when this module is hot reloaded"""
    print("[CustomCommands] Module reloaded! ✓")
