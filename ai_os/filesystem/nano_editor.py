"""
Nano-like Text Editor for AI OS
Simple interactive file editor.
"""

import sys
from typing import Optional


class NanoEditor:
    """Simple text editor similar to nano"""
    
    def __init__(self, vfs_manager):
        """Initialize editor with VFS manager"""
        self.vfs = vfs_manager
        self.content_lines = []
        self.current_file = None
        self.modified = False
    
    def edit_file(self, filepath: str) -> bool:
        """
        Edit a file interactively.
        
        Args:
            filepath: Path to file to edit
            
        Returns:
            True if file was saved
        """
        self.current_file = filepath
        
        # Try to read existing file
        existing_content = self.vfs.read(filepath)
        if existing_content is not None:
            self.content_lines = existing_content.split('\n')
            print(f"Editing existing file: {filepath}")
        else:
            self.content_lines = []
            print(f"Creating new file: {filepath}")
        
        # Show current content
        self._display_content()
        
        # Interactive editing
        print("\n" + "=" * 70)
        print("NANO EDITOR - Commands:")
        print("  Type your content (one line at a time)")
        print("  :w    - Save file")
        print("  :q    - Quit without saving")
        print("  :wq   - Save and quit")
        print("  :x    - Delete current line")
        print("  :i    - Insert line at current position")
        print("  :a    - Append line at end")
        print("  :d    - Display current content")
        print("  :h    - Show this help")
        print("=" * 70)
        
        return self._edit_loop()
    
    def _display_content(self):
        """Display current file content"""
        if not self.content_lines:
            print("\n[Empty file]")
            return
        
        print("\n" + "=" * 70)
        print(f"File: {self.current_file}")
        print("=" * 70)
        for i, line in enumerate(self.content_lines, 1):
            print(f"{i:3}: {line}")
        print("=" * 70)
        print(f"Total lines: {len(self.content_lines)}")
    
    def _edit_loop(self) -> bool:
        """Main editing loop"""
        while True:
            try:
                user_input = input("\nnano> ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith(':'):
                    cmd = user_input[1:].lower()
                    
                    if cmd == 'w':
                        # Save
                        if self._save_file():
                            print("✓ File saved")
                            self.modified = False
                        else:
                            print("✗ Error saving file")
                    
                    elif cmd == 'q':
                        # Quit
                        if self.modified:
                            confirm = input("File modified. Quit without saving? (y/n): ")
                            if confirm.lower() != 'y':
                                continue
                        print("Exiting editor")
                        return False
                    
                    elif cmd == 'wq':
                        # Save and quit
                        if self._save_file():
                            print("✓ File saved")
                            return True
                        else:
                            print("✗ Error saving file")
                            return False
                    
                    elif cmd == 'x':
                        # Delete line
                        if not self.content_lines:
                            print("File is empty")
                            continue
                        
                        try:
                            line_num = int(input("Line number to delete: "))
                            if 1 <= line_num <= len(self.content_lines):
                                deleted = self.content_lines.pop(line_num - 1)
                                print(f"✓ Deleted line {line_num}: {deleted}")
                                self.modified = True
                                self._display_content()
                            else:
                                print("Invalid line number")
                        except ValueError:
                            print("Invalid input")
                    
                    elif cmd == 'i':
                        # Insert line
                        try:
                            line_num = int(input("Insert at line number: "))
                            content = input("Content: ")
                            if 1 <= line_num <= len(self.content_lines) + 1:
                                self.content_lines.insert(line_num - 1, content)
                                print(f"✓ Inserted at line {line_num}")
                                self.modified = True
                                self._display_content()
                            else:
                                print("Invalid line number")
                        except ValueError:
                            print("Invalid input")
                    
                    elif cmd == 'a':
                        # Append line
                        content = input("Content: ")
                        self.content_lines.append(content)
                        print(f"✓ Appended line {len(self.content_lines)}")
                        self.modified = True
                        self._display_content()
                    
                    elif cmd == 'd':
                        # Display content
                        self._display_content()
                    
                    elif cmd == 'h':
                        # Help
                        print("\nNano Editor Commands:")
                        print("  :w    - Save file")
                        print("  :q    - Quit without saving")
                        print("  :wq   - Save and quit")
                        print("  :x    - Delete line")
                        print("  :i    - Insert line")
                        print("  :a    - Append line")
                        print("  :d    - Display content")
                        print("  :h    - Show this help")
                    
                    else:
                        print(f"Unknown command: :{cmd}")
                        print("Type :h for help")
                
                else:
                    # Regular text - append as new line
                    self.content_lines.append(user_input)
                    self.modified = True
                    print(f"✓ Added line {len(self.content_lines)}")
            
            except KeyboardInterrupt:
                print("\n\nUse :q to quit")
            except EOFError:
                break
        
        return False
    
    def _save_file(self) -> bool:
        """Save file to VFS"""
        content = '\n'.join(self.content_lines)
        return self.vfs.write(self.current_file, content)


def nano_command(vfs_manager, args=None, gui_mode=False):
    """
    Nano command handler.
    
    Args:
        vfs_manager: VFS manager instance
        args: Command arguments (filename)
        gui_mode: If True, returns content for GUI editor
        
    Returns:
        If gui_mode is True, returns file content as string
        Otherwise returns result message
    """
    if not args or (isinstance(args, list) and not args):
        return "Error: No file specified. Usage: nano <filename>"
    
    # Handle both string and list args
    if isinstance(args, str):
        filepath = args
    else:
        # Handle --gui flag
        if '--gui' in args:
            args.remove('--gui')
            gui_mode = True
        filepath = ' '.join(args).strip()
    
    # In GUI mode, just read the file and return its content
    if gui_mode:
        content = vfs_manager.read(filepath)
        if content is not None:
            return content
        return ""  # Return empty string for new files
    
    # In terminal mode, use the interactive editor
    editor = NanoEditor(vfs_manager)
    saved = editor.edit_file(filepath)
    
    if saved:
        return f"File saved: {filepath}"
    return "Edit cancelled"
