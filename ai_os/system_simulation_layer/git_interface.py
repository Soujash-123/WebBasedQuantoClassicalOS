"""
Git Interface
Git-like version control operations.
"""

import os
import json
import shutil
from typing import List, Optional
from datetime import datetime
from .system_logger import SystemLogger


class GitInterface:
    """Git-like version control interface."""
    
    def __init__(
        self,
        repos_dir: str = "./virtual_packages",
        logger: Optional[SystemLogger] = None
    ):
        """
        Initialize git interface.
        
        Args:
            repos_dir: Directory for cloned repositories
            logger: System logger
        """
        self.repos_dir = repos_dir
        self.logger = logger or SystemLogger()
        
        os.makedirs(repos_dir, exist_ok=True)
    
    def clone(self, url: str, dest: Optional[str] = None) -> bool:
        """
        Clone a repository (git clone).
        
        Args:
            url: Repository URL
            dest: Destination directory
            
        Returns:
            True if successful
        """
        # Extract repo name from URL
        repo_name = url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        if not dest:
            dest = repo_name
        
        repo_path = os.path.join(self.repos_dir, dest)
        
        # Check if already exists
        if os.path.exists(repo_path):
            print(f"fatal: destination path '{dest}' already exists")
            return False
        
        print(f"Cloning into '{dest}'...")
        
        # Create repository directory
        os.makedirs(repo_path, exist_ok=True)
        
        # Create .git directory
        git_dir = os.path.join(repo_path, '.git')
        os.makedirs(git_dir, exist_ok=True)
        
        # Create metadata
        metadata = {
            'url': url,
            'branch': 'main',
            'commits': [
                {
                    'hash': 'a1b2c3d4',
                    'author': 'AI OS System',
                    'date': datetime.now().isoformat(),
                    'message': 'Initial commit'
                }
            ],
            'cloned_at': datetime.now().isoformat()
        }
        
        meta_file = os.path.join(git_dir, 'meta.json')
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create sample files
        readme_path = os.path.join(repo_path, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(f"# {repo_name}\n\nCloned from {url}\n")
        
        print(f"remote: Enumerating objects: 3, done.")
        print(f"remote: Counting objects: 100% (3/3), done.")
        print(f"remote: Total 3 (delta 0), reused 0 (delta 0)")
        print(f"Receiving objects: 100% (3/3), done.")
        
        self.logger.log_git('clone', url, success=True)
        
        return True
    
    def pull(self, repo_path: str = '.') -> bool:
        """
        Pull latest changes (git pull).
        
        Args:
            repo_path: Repository path
            
        Returns:
            True if successful
        """
        git_dir = os.path.join(repo_path, '.git')
        
        if not os.path.exists(git_dir):
            print("fatal: not a git repository")
            return False
        
        # Load metadata
        meta_file = os.path.join(git_dir, 'meta.json')
        if not os.path.exists(meta_file):
            print("fatal: repository metadata not found")
            return False
        
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        url = metadata.get('url', 'unknown')
        branch = metadata.get('branch', 'main')
        
        print(f"From {url}")
        print(f" * branch            {branch} -> FETCH_HEAD")
        print("Already up to date.")
        
        self.logger.log_git('pull', url, success=True)
        
        return True
    
    def status(self, repo_path: str = '.') -> bool:
        """
        Show repository status (git status).
        
        Args:
            repo_path: Repository path
            
        Returns:
            True if successful
        """
        git_dir = os.path.join(repo_path, '.git')
        
        if not os.path.exists(git_dir):
            print("fatal: not a git repository")
            return False
        
        # Load metadata
        meta_file = os.path.join(git_dir, 'meta.json')
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        branch = metadata.get('branch', 'main')
        
        print(f"On branch {branch}")
        print("Your branch is up to date with 'origin/{branch}'.")
        print()
        print("nothing to commit, working tree clean")
        
        return True
    
    def log(self, repo_path: str = '.', limit: int = 10) -> bool:
        """
        Show commit history (git log).
        
        Args:
            repo_path: Repository path
            limit: Number of commits to show
            
        Returns:
            True if successful
        """
        git_dir = os.path.join(repo_path, '.git')
        
        if not os.path.exists(git_dir):
            print("fatal: not a git repository")
            return False
        
        # Load metadata
        meta_file = os.path.join(git_dir, 'meta.json')
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        commits = metadata.get('commits', [])
        
        for commit in commits[:limit]:
            print(f"commit {commit['hash']}")
            print(f"Author: {commit['author']}")
            print(f"Date:   {commit['date']}")
            print()
            print(f"    {commit['message']}")
            print()
        
        return True
    
    def branch(self, repo_path: str = '.', branch_name: Optional[str] = None) -> bool:
        """
        List or create branches (git branch).
        
        Args:
            repo_path: Repository path
            branch_name: New branch name (None to list)
            
        Returns:
            True if successful
        """
        git_dir = os.path.join(repo_path, '.git')
        
        if not os.path.exists(git_dir):
            print("fatal: not a git repository")
            return False
        
        # Load metadata
        meta_file = os.path.join(git_dir, 'meta.json')
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        current_branch = metadata.get('branch', 'main')
        
        if branch_name:
            # Create new branch
            print(f"Created branch '{branch_name}'")
            return True
        else:
            # List branches
            print(f"* {current_branch}")
            return True
    
    def run_command(self, args: List[str], context) -> bool:
        """
        Run git command.
        
        Args:
            args: Command arguments
            context: Execution context
            
        Returns:
            True if successful
        """
        if not args:
            print("usage: git <command> [<args>]")
            print()
            print("Commands:")
            print("  clone <url> [dest]  - Clone a repository")
            print("  pull                - Pull latest changes")
            print("  status              - Show working tree status")
            print("  log [n]             - Show commit logs")
            print("  branch [name]       - List or create branches")
            return False
        
        command = args[0]
        
        if command == 'clone':
            if len(args) < 2:
                print("fatal: You must specify a repository to clone")
                return False
            url = args[1]
            dest = args[2] if len(args) > 2 else None
            return self.clone(url, dest)
        
        elif command == 'pull':
            repo_path = args[1] if len(args) > 1 else '.'
            return self.pull(repo_path)
        
        elif command == 'status':
            repo_path = args[1] if len(args) > 1 else '.'
            return self.status(repo_path)
        
        elif command == 'log':
            repo_path = '.'
            limit = 10
            if len(args) > 1:
                try:
                    limit = int(args[1])
                except ValueError:
                    pass
            return self.log(repo_path, limit)
        
        elif command == 'branch':
            repo_path = '.'
            branch_name = args[1] if len(args) > 1 else None
            return self.branch(repo_path, branch_name)
        
        else:
            print(f"git: '{command}' is not a git command")
            return False
