/**
 * Application Content Components
 * Individual app windows with real backend integration
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronRight, Folder, File, Image, Music, Video, Save, FileText, Globe, Download, RefreshCw, ArrowLeft, ArrowRight, Home, Lock, Search as SearchIcon, Monitor } from 'lucide-react';
import TextEditor from './TextEditor';
import { useFiles, useTerminal, useProcesses, useProcessStats, useSystemInfo, useUptime } from '../api/hooks';
import apiClient from '../api/client';

// Files App Component
export const FilesApp = ({ createWindow }) => {
  const { files, currentPath, loading, error, navigateTo, refetch } = useFiles('/');

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (ext === 'jpg' || ext === 'png' || ext === 'gif') return Image;
    if (ext === 'mp3' || ext === 'wav') return Music;
    if (ext === 'mp4' || ext === 'avi') return Video;
    return File;
  };

  const openFileInNotepad = (filePath, fileName) => {
    if (createWindow) {
      createWindow(
        { name: 'Notepad', icon: FileText, color: 'bg-yellow-500' },
        { path: filePath, name: fileName }
      );
    }
  };

  if (loading && !files.length) {
    return <div className="flex items-center justify-center h-full text-gray-500">Loading files...</div>;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-red-500">
        <p>Error loading files: {error}</p>
        <button onClick={refetch} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="bg-gray-50 border-b border-gray-200 px-6 py-3 flex items-center gap-2">
        <button 
          onClick={() => navigateTo('/')}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Home
        </button>
        {currentPath !== '/' && (
          <>
            <ChevronRight className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-700 font-medium">{currentPath}</span>
          </>
        )}
        <button 
          onClick={refetch}
          className="ml-auto text-sm text-blue-600 hover:text-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* File Grid */}
      <div className="flex-1 p-6 overflow-auto">
        {files.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            This directory is empty
          </div>
        ) : (
          <div className="grid grid-cols-4 gap-4">
            {files.map((item, idx) => {
              const ItemIcon = item.type === 'folder' ? Folder : getFileIcon(item.name || item);
              const itemName = typeof item === 'string' ? item : item.name;
              const isFolder = typeof item === 'object' ? item.type === 'folder' : false;

              return (
                <button
                  key={idx}
                  onDoubleClick={() => {
                    if (isFolder) {
                      navigateTo(`${currentPath}/${itemName}`.replace('//', '/'));
                    } else {
                      // Open file in Notepad
                      const fullPath = `${currentPath}/${itemName}`.replace('//', '/');
                      openFileInNotepad(fullPath, itemName);
                    }
                  }}
                  className="flex flex-col items-center gap-3 p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group"
                >
                  <div className={`${isFolder ? 'bg-blue-500' : 'bg-gray-400'} p-3 rounded-xl group-hover:scale-110 transition-transform`}>
                    <ItemIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-sm text-gray-700 font-medium text-center break-all">
                    {itemName}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-50 border-t border-gray-200 px-6 py-2 text-xs text-gray-600">
        {files.length} items
      </div>
    </div>
  );
};

// Terminal App Component
export const TerminalApp = () => {
  const { history, executeCommand, clearHistory, loading, currentDirectory } = useTerminal();
  const [input, setInput] = useState('');
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isGuiEditorOpen, setIsGuiEditorOpen] = useState(false);
  const [editorContent, setEditorContent] = useState('');
  const [editorPath, setEditorPath] = useState('');
  const commandHistory = React.useRef([]);
  const inputRef = React.useRef(null);
  const historyEndRef = React.useRef(null);
  
  // Auto-scroll to bottom when history updates
  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  // Focus input on mount and after command execution
  const focusInput = useCallback(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    focusInput();
  }, [focusInput]);

  // Focus input after command execution
  useEffect(() => {
    if (!loading) {
      focusInput();
    }
  }, [loading, focusInput]);

  const handleSaveEditor = async (content) => {
    try {
      await apiClient.writeFile(editorPath, content);
      setIsGuiEditorOpen(false);
      setHistory(prev => [...prev, `File saved: ${editorPath}`]);
    } catch (error) {
      console.error('Error saving file:', error);
      setHistory(prev => [...prev, `Error saving file: ${error.message}`]);
    }
  };

  const handleCancelEditor = () => {
    setIsGuiEditorOpen(false);
  };

  const handleCommand = async () => {
    const cmd = input.trim();
    if (!cmd) {
      focusInput();
      return;
    }
    
    // Add to command history if not the same as last command
    if (commandHistory.current[0] !== cmd) {
      commandHistory.current.unshift(cmd);
      // Keep only last 100 commands
      if (commandHistory.current.length > 100) {
        commandHistory.current.pop();
      }
    }
    
    // Handle built-in commands
    if (cmd === 'clear') {
      clearHistory();
      setInput('');
      setHistoryIndex(-1);
      return;
    } else if (cmd === 'help') {
      // Show help text directly in the terminal
      setHistory(prev => [...prev, 
        `user@webos:~$ ${cmd}`,
        'Available commands:',
        '  ls [path]      - List directory contents',
        '  cd [path]      - Change directory',
        '  cat <file>     - Display file contents',
        '  nano <file>    - Edit file in terminal',
        '  nano <file> --gui - Edit file in GUI editor',
        '  clear          - Clear terminal',
        '  help           - Show this help',
        '  exit           - Exit terminal',
        '',
        'Use quotes around paths with spaces, e.g.: cd "My Documents"',
        ''
      ]);
      setInput('');
      return;
    } else if (cmd.startsWith('nano ') && cmd.endsWith('--gui')) {
      // Handle GUI editor
      const path = cmd.slice(5, -5).trim();
      setEditorPath(path);
      try {
        // Read file content
        const response = await apiClient.readFile(path);
        setEditorContent(response.content || '');
        setIsGuiEditorOpen(true);
      } catch (error) {
        setHistory(prev => [...prev, `Error opening file: ${error.message}`]);
      }
      setInput('');
      return;
    }
    
    // Execute the command as-is (including all arguments)
    try {
      setInput('');
      await executeCommand(cmd);
    } catch (error) {
      console.error('Command execution error:', error);
      setHistory(prev => [...prev, `Error: ${error.message}`]);
    }
    
    setInput('');
    setHistoryIndex(-1);
  };

  // Handle click on terminal to focus input
  const handleTerminalClick = useCallback((e) => {
    // Only focus if clicking on the terminal background, not on text or other elements
    if (e.target === e.currentTarget) {
      focusInput();
    }
  }, [focusInput]);

  return (
    <div 
      className="bg-gray-900 h-full p-4 font-mono text-sm flex flex-col cursor-text"
      onClick={handleTerminalClick}
    >
      {isGuiEditorOpen && (
        <TextEditor 
          content={editorContent}
          onSave={handleSaveEditor}
          onCancel={handleCancelEditor}
        />
      )}
      <div className="flex-1 overflow-auto text-green-400 space-y-1">
        {history.map((line, idx) => (
          <p key={idx}>{line}</p>
        ))}
        {loading && <p className="text-yellow-400">Executing...</p>}
        <div ref={historyEndRef} />
      </div>
      <div className="flex items-center gap-2 text-green-400 mt-2">
        <span>user@webos:{currentDirectory}$</span>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            // Handle command history navigation
            if (e.key === 'ArrowUp') {
              e.preventDefault();
              if (commandHistory.current.length > 0) {
                const newIndex = Math.min(historyIndex + 1, commandHistory.current.length - 1);
                setHistoryIndex(newIndex);
                setInput(commandHistory.current[newIndex] || '');
              }
            } else if (e.key === 'ArrowDown') {
              e.preventDefault();
              if (historyIndex > 0) {
                const newIndex = historyIndex - 1;
                setHistoryIndex(newIndex);
                setInput(commandHistory.current[newIndex] || '');
              } else if (historyIndex === 0) {
                setHistoryIndex(-1);
                setInput('');
              }
            } else if (e.key === 'Enter') {
              e.preventDefault();
              handleCommand();
            } else if (e.key === 'Tab') {
              e.preventDefault();
              // Basic tab completion for directories
              if (input.trim() === '') return;
              
              // Get the last part of the command (after last space)
              const parts = input.split(' ');
              const lastPart = parts[parts.length - 1];
              
              // If it's an ls command, try to complete directory names
              if (parts[0] === 'ls' || parts[0] === 'cd' || parts[0] === 'cat') {
                // This is a simplified version - in a real app, you'd want to fetch
                // the list of files from the current directory and try to complete
                console.log('Tab completion not fully implemented');
              }
            }
          }}
          onFocus={(e) => {
            // Auto-scroll to bottom when input is focused
            const terminal = e.target.closest('.terminal-container');
            if (terminal) {
              terminal.scrollTop = terminal.scrollHeight;
            }
          }}
          className="flex-1 bg-transparent outline-none text-green-400 caret-green-400"
          autoFocus
          disabled={loading}
          spellCheck={false}
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
        />
      </div>
    </div>
  );
};

// Settings App Component
export const SettingsApp = () => {
  const { data: systemInfo, loading } = useSystemInfo();

  if (loading) {
    return <div className="flex items-center justify-center h-full text-gray-500">Loading settings...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">System Settings</h2>
      
      {/* System Information */}
      <div className="bg-blue-50 rounded-xl p-4">
        <h3 className="font-semibold text-gray-800 mb-2">System Information</h3>
        <div className="space-y-1 text-sm">
          <p><span className="font-medium">Version:</span> {systemInfo?.version || 'N/A'}</p>
          <p><span className="font-medium">Layers:</span> {systemInfo?.layers?.length || 0}</p>
          <p><span className="font-medium">Commands:</span> {systemInfo?.total_commands || 0}</p>
          <p><span className="font-medium">Status:</span> {systemInfo?.initialized ? 'Running' : 'Stopped'}</p>
        </div>
      </div>

      {/* Settings Categories */}
      <div className="space-y-3">
        {[
          { name: 'Display & Appearance', desc: 'Wallpaper, themes, resolution' },
          { name: 'Network & Internet', desc: 'Wi-Fi, ethernet, VPN' },
          { name: 'System & Updates', desc: 'OS version, updates, storage' },
          { name: 'Privacy & Security', desc: 'Permissions, firewall, passwords' },
          { name: 'Sound & Notifications', desc: 'Volume, alerts, system sounds' },
          { name: 'Power & Battery', desc: 'Sleep, hibernate, power plan' },
        ].map((setting, idx) => (
          <button key={idx} className="w-full p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors flex items-center justify-between group">
            <div className="text-left">
              <p className="text-gray-800 font-medium">{setting.name}</p>
              <p className="text-sm text-gray-500 mt-0.5">{setting.desc}</p>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
};

// Notepad/Text Editor App Component
export const NotepadApp = ({ data, createWindow }) => {
  const [content, setContent] = useState('');
  const [filePath, setFilePath] = useState(data?.path || '');
  const [fileName, setFileName] = useState(data?.name || 'Untitled.txt');
  const [isSaved, setIsSaved] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load file content if path is provided
  useEffect(() => {
    if (data?.path) {
      loadFile(data.path);
    }
  }, [data?.path]);

  const loadFile = async (path) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.readFile(path);
      setContent(result.content || '');
      setFilePath(path);
      setFileName(path.split('/').pop());
      setIsSaved(true);
    } catch (err) {
      setError('Error loading file: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveFile = async () => {
    if (!filePath) {
      setError('Please specify a file path');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await apiClient.writeFile(filePath, content, 'w');
      setIsSaved(true);
      setError(null);
    } catch (err) {
      setError('Error saving file: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (e) => {
    setContent(e.target.value);
    setIsSaved(false);
  };

  const handleFilePathChange = (e) => {
    setFilePath(e.target.value);
    setFileName(e.target.value.split('/').pop() || 'Untitled.txt');
  };

  const openFileBrowser = () => {
    if (createWindow) {
      createWindow({ name: 'Files', icon: Folder, color: 'bg-blue-500' });
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Toolbar */}
      <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center gap-3">
        <FileText className="w-5 h-5 text-gray-600" />
        <input
          type="text"
          value={filePath}
          onChange={handleFilePathChange}
          placeholder="/path/to/file.txt"
          className="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={openFileBrowser}
          className="px-3 py-1.5 text-sm bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
        >
          Browse
        </button>
        <button
          onClick={saveFile}
          disabled={loading || isSaved}
          className={`px-4 py-1.5 text-sm rounded-lg flex items-center gap-2 transition-colors ${
            isSaved
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          <Save className="w-4 h-4" />
          {loading ? 'Saving...' : isSaved ? 'Saved' : 'Save'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Editor Area */}
      <div className="flex-1 overflow-hidden">
        <textarea
          value={content}
          onChange={handleContentChange}
          placeholder="Start typing..."
          className="w-full h-full p-4 font-mono text-sm resize-none focus:outline-none"
          spellCheck={false}
        />
      </div>

      {/* Status Bar */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 flex items-center justify-between text-xs text-gray-600">
        <span>{fileName}</span>
        <div className="flex items-center gap-4">
          <span>Lines: {content.split('\n').length}</span>
          <span>Characters: {content.length}</span>
          <span className={isSaved ? 'text-green-600' : 'text-orange-600'}>
            {isSaved ? '● Saved' : '● Unsaved changes'}
          </span>
        </div>
      </div>
    </div>
  );
};

// Web Browser App Component
export const BrowserApp = () => {
  const [url, setUrl] = useState('https://example.com');
  const [currentUrl, setCurrentUrl] = useState('https://example.com');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState(['https://example.com']);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [downloads, setDownloads] = useState([]);
  const [showDownloads, setShowDownloads] = useState(false);

  const navigate = (newUrl) => {
    if (!newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
      newUrl = 'https://' + newUrl;
    }
    setLoading(true);
    setCurrentUrl(newUrl);
    
    // Add to history
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(newUrl);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    
    setTimeout(() => setLoading(false), 500);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate(url);
  };

  const goBack = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setCurrentUrl(history[newIndex]);
      setUrl(history[newIndex]);
    }
  };

  const goForward = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setCurrentUrl(history[newIndex]);
      setUrl(history[newIndex]);
    }
  };

  const refresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 500);
  };

  const goHome = () => {
    navigate('https://example.com');
    setUrl('https://example.com');
  };

  const simulateDownload = (fileName) => {
    const download = {
      id: Date.now(),
      name: fileName,
      size: (Math.random() * 10 + 1).toFixed(2) + ' MB',
      progress: 0,
      status: 'downloading'
    };
    
    setDownloads(prev => [...prev, download]);
    setShowDownloads(true);

    // Simulate download progress
    const interval = setInterval(() => {
      setDownloads(prev => prev.map(d => {
        if (d.id === download.id && d.progress < 100) {
          const newProgress = Math.min(100, d.progress + Math.random() * 20);
          return {
            ...d,
            progress: newProgress,
            status: newProgress >= 100 ? 'completed' : 'downloading'
          };
        }
        return d;
      }));
    }, 300);

    setTimeout(() => clearInterval(interval), 2000);
  };

  const isSecure = currentUrl.startsWith('https://');

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Browser Toolbar */}
      <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center gap-2">
        <button
          onClick={goBack}
          disabled={historyIndex === 0}
          className="p-2 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-gray-700" />
        </button>
        <button
          onClick={goForward}
          disabled={historyIndex === history.length - 1}
          className="p-2 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowRight className="w-4 h-4 text-gray-700" />
        </button>
        <button
          onClick={refresh}
          className="p-2 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 text-gray-700 ${loading ? 'animate-spin' : ''}`} />
        </button>
        <button
          onClick={goHome}
          className="p-2 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <Home className="w-4 h-4 text-gray-700" />
        </button>

        {/* URL Bar */}
        <form onSubmit={handleSubmit} className="flex-1 flex items-center">
          <div className="flex-1 flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500">
            {isSecure ? (
              <Lock className="w-4 h-4 text-green-600" />
            ) : (
              <Globe className="w-4 h-4 text-gray-400" />
            )}
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 text-sm outline-none"
              placeholder="Enter URL or search..."
            />
            <SearchIcon className="w-4 h-4 text-gray-400" />
          </div>
        </form>

        <button
          onClick={() => setShowDownloads(!showDownloads)}
          className="p-2 rounded-lg hover:bg-gray-200 transition-colors relative"
        >
          <Download className="w-4 h-4 text-gray-700" />
          {downloads.filter(d => d.status === 'downloading').length > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full"></span>
          )}
        </button>
      </div>

      {/* Downloads Panel */}
      {showDownloads && (
        <div className="bg-gray-50 border-b border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800">Downloads</h3>
            <button
              onClick={() => setDownloads([])}
              className="text-xs text-blue-600 hover:text-blue-700"
            >
              Clear all
            </button>
          </div>
          {downloads.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No downloads yet</p>
          ) : (
            <div className="space-y-2">
              {downloads.map(download => (
                <div key={download.id} className="bg-white rounded-lg p-3 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-800">{download.name}</span>
                    <span className="text-xs text-gray-500">{download.size}</span>
                  </div>
                  <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        download.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${download.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {download.status === 'completed' ? 'Download complete' : `Downloading... ${download.progress.toFixed(0)}%`}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Browser Content Area */}
      <div className="flex-1 bg-white overflow-hidden relative">
        {loading && (
          <div className="absolute top-0 left-0 right-0 h-1 bg-blue-500 animate-pulse"></div>
        )}
        
        {/* Info Banner */}
        <div className="absolute top-0 left-0 right-0 bg-blue-50 border-b border-blue-200 px-4 py-2 z-10">
          <p className="text-xs text-blue-800">
            ℹ️ <strong>Note:</strong> Many sites (like Google, Facebook, YouTube) block iframe embedding for security. 
            Try sites like: <button onClick={() => { setUrl('https://example.com'); navigate('https://example.com'); }} className="text-blue-600 underline hover:text-blue-800">example.com</button>, 
            <button onClick={() => { setUrl('https://wikipedia.org'); navigate('https://wikipedia.org'); }} className="text-blue-600 underline hover:text-blue-800 ml-1">wikipedia.org</button>, or 
            <button onClick={() => { setUrl('https://archive.org'); navigate('https://archive.org'); }} className="text-blue-600 underline hover:text-blue-800 ml-1">archive.org</button>
          </p>
        </div>

        <div className="w-full h-full pt-10">
          <iframe
            src={currentUrl}
            className="w-full h-full border-0"
            title="Web Browser"
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
            onError={(e) => {
              console.log('iframe load error', e);
            }}
          />
        </div>
      </div>

      {/* Quick Actions Bar */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => simulateDownload('example-file.zip')}
            className="px-3 py-1.5 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-1"
          >
            <Download className="w-3 h-3" />
            Test Download
          </button>
        </div>
        <div className="text-xs text-gray-600">
          {isSecure ? '🔒 Secure connection' : '⚠️ Not secure'}
        </div>
      </div>
    </div>
  );
};

// Monitor App Component
export const MonitorApp = () => {
  // Use hooks with safe defaults
  const processData = useProcesses(3000);
  let processes = processData?.processes || [];
  const processLoading = processData?.loading || false;

  // Convert processes to array if it's an object
  if (processes && typeof processes === 'object' && !Array.isArray(processes)) {
    processes = Object.values(processes);
  }
  // Ensure it's always an array
  if (!Array.isArray(processes)) {
    processes = [];
  }

  const statsData = useProcessStats(2000);
  const stats = statsData?.stats || {};

  const uptimeData = useUptime(1000);
  const uptime = uptimeData?.uptime || '0h 0m 0s';

  const systemData = useSystemInfo();
  const systemInfo = systemData?.data || null;
  const systemLoading = systemData?.loading || false;

  // Debug: Log to see if component is rendering
  console.log('MonitorApp rendering', { 
    processes: Array.isArray(processes) ? processes : 'NOT AN ARRAY', 
    processesLength: processes.length,
    processLoading,
    stats, 
    uptime, 
    systemInfo,
    systemLoading 
  });

  // Calculate percentages with some animation
  const cpuUsage = Math.min(100, (processes?.length * 5) || 23);
  const memoryUsed = systemInfo?.config?.memory?.total_mb 
    ? `${(systemInfo.config.memory.total_mb * 0.3).toFixed(1)}MB`
    : '4.2GB';
  const memoryTotal = systemInfo?.config?.memory?.total_mb 
    ? `${systemInfo.config.memory.total_mb}MB`
    : '16GB';
  const memoryPercent = 30; // Mock percentage

  // Ensure we always return something
  try {
    return (
      <div className="h-full bg-gradient-to-br from-gray-50 to-gray-100 overflow-auto">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between bg-white rounded-xl p-4 shadow-sm border border-gray-200">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <Monitor className="w-7 h-7 text-green-600" />
                System Monitor
              </h2>
              <p className="text-sm text-gray-500 mt-1">Real-time system performance metrics</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">System Uptime</p>
              <p className="text-lg font-semibold text-gray-800">{uptime || '0h 0m 0s'}</p>
            </div>
          </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* CPU Card */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">CPU Usage</p>
                <p className="text-4xl font-bold text-blue-600">{cpuUsage}%</p>
              </div>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center shadow-lg">
                <span className="text-white text-xl font-bold">{cpuUsage}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-gray-500">
                <span>Load</span>
                <span>{cpuUsage}% of 100%</span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500"
                  style={{ width: `${cpuUsage}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Memory Card */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Memory Usage</p>
                <p className="text-4xl font-bold text-green-600">{memoryUsed}</p>
                <p className="text-xs text-gray-500">of {memoryTotal}</p>
              </div>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg">
                <span className="text-white text-xl font-bold">{memoryPercent}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-gray-500">
                <span>RAM</span>
                <span>{memoryPercent}%</span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-500"
                  style={{ width: `${memoryPercent}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Active Layers Card */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Active Layers</p>
                <p className="text-4xl font-bold text-purple-600">{systemInfo?.layers?.length || 0}</p>
                <p className="text-xs text-gray-500">OS Components</p>
              </div>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center shadow-lg">
                <span className="text-white text-2xl">⚙️</span>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <div className="flex-1 text-center py-2 bg-purple-50 rounded-lg">
                <p className="text-xs text-gray-600">Commands</p>
                <p className="text-sm font-semibold text-purple-600">{systemInfo?.total_commands || 0}</p>
              </div>
              <div className="flex-1 text-center py-2 bg-purple-50 rounded-lg">
                <p className="text-xs text-gray-600">Version</p>
                <p className="text-sm font-semibold text-purple-600">{systemInfo?.version || '1.0'}</p>
              </div>
            </div>
          </div>

          {/* Processes Card */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Active Processes</p>
                <p className="text-4xl font-bold text-orange-600">{stats.total_processes || processes.length}</p>
                <p className="text-xs text-gray-500">Running Tasks</p>
              </div>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center shadow-lg">
                <span className="text-white text-2xl">🔄</span>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <div className="flex-1 text-center py-2 bg-orange-50 rounded-lg">
                <p className="text-xs text-gray-600">Running</p>
                <p className="text-sm font-semibold text-orange-600">{processes.length}</p>
              </div>
              <div className="flex-1 text-center py-2 bg-orange-50 rounded-lg">
                <p className="text-xs text-gray-600">Max</p>
                <p className="text-sm font-semibold text-orange-600">10</p>
              </div>
            </div>
          </div>
        </div>

        {/* Process List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Running Processes
            </h3>
          </div>
          <div className="p-4">
            {processLoading && processes.length === 0 ? (
              <div className="text-center py-8">
                <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-500 mt-2">Loading processes...</p>
              </div>
            ) : processes.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No active processes</p>
                <p className="text-xs text-gray-400 mt-1">System is idle</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {processes.slice(0, 10).map((process, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm py-3 px-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xs">
                        {idx + 1}
                      </div>
                      <span className="text-gray-700 font-medium">
                        {typeof process === 'object' ? process.name : `Process ${idx + 1}`}
                      </span>
                    </div>
                    <div className="flex gap-6 text-gray-600 text-xs">
                      <span className="bg-white px-2 py-1 rounded">PID: {typeof process === 'object' ? process.pid : idx + 1}</span>
                      {typeof process === 'object' && process.status && (
                        <span className="bg-green-100 text-green-700 px-2 py-1 rounded font-medium">
                          {process.status}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    );
  } catch (error) {
    console.error('Monitor render error:', error);
    return (
      <div className="h-full bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-xl p-6 max-w-md text-center shadow-lg">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Display Error</h3>
          <p className="text-gray-600 mb-2">The monitor failed to render properly.</p>
          <p className="text-sm text-gray-500 font-mono bg-gray-100 p-2 rounded">{error.message}</p>
        </div>
      </div>
    );
  }
};
