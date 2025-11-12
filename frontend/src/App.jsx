import React, { useState, useRef, useEffect } from 'react';
import { Monitor, Folder, Settings, Terminal, Maximize2, Minimize2, X, Menu, Search, Bell, Wifi, Battery, Volume2, ChevronRight, File, Image, Music, Video, Trash2, FileText, Globe } from 'lucide-react';
import { FilesApp, TerminalApp, SettingsApp, MonitorApp, NotepadApp, BrowserApp } from './components/AppContent';

const WebOS = () => {
  const [windows, setWindows] = useState([]);
  const [nextId, setNextId] = useState(1);
  const [activeWindow, setActiveWindow] = useState(null);
  const [startMenuOpen, setStartMenuOpen] = useState(false);
  const [time, setTime] = useState(new Date());
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [contextMenu, setContextMenu] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const createWindow = (app, data = null) => {
    const newWindow = {
      id: nextId,
      app,
      data,
      position: { x: 100 + (nextId * 30), y: 50 + (nextId * 30) },
      size: { width: 800, height: 550 },
      minimized: false,
      maximized: false
    };
    setWindows([...windows, newWindow]);
    setActiveWindow(nextId);
    setNextId(nextId + 1);
    setStartMenuOpen(false);
  };

  const closeWindow = (id) => {
    setWindows(windows.filter(w => w.id !== id));
    if (activeWindow === id) setActiveWindow(null);
  };

  const minimizeWindow = (id) => {
    setWindows(windows.map(w => w.id === id ? { ...w, minimized: true } : w));
    if (activeWindow === id) setActiveWindow(null);
  };

  const restoreWindow = (id) => {
    setWindows(windows.map(w => w.id === id ? { ...w, minimized: false } : w));
    setActiveWindow(id);
  };

  const toggleMaximize = (id) => {
    setWindows(windows.map(w => 
      w.id === id ? { ...w, maximized: !w.maximized } : w
    ));
  };

  const addNotification = (message) => {
    const id = Date.now();
    setNotifications([...notifications, { id, message, time: new Date() }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const handleContextMenu = (e) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  useEffect(() => {
    document.addEventListener('click', closeContextMenu);
    return () => document.removeEventListener('click', closeContextMenu);
  }, []);

  const apps = [
    { name: 'Files', icon: Folder, color: 'bg-blue-500' },
    { name: 'Terminal', icon: Terminal, color: 'bg-gray-800' },
    { name: 'Notepad', icon: FileText, color: 'bg-yellow-500' },
    { name: 'Browser', icon: Globe, color: 'bg-cyan-500' },
    { name: 'Settings', icon: Settings, color: 'bg-purple-500' },
    { name: 'Monitor', icon: Monitor, color: 'bg-green-500' }
  ];

  return (
    <div 
      className="h-screen w-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 overflow-hidden relative"
      onContextMenu={handleContextMenu}
    >
      {/* Desktop Area */}
      <div className="h-full w-full relative pb-16">
        {/* Desktop Icons */}
        <div className="p-6 grid grid-cols-1 gap-4 w-24">
          {apps.slice(0, 2).map((app, idx) => (
            <button
              key={idx}
              onDoubleClick={() => createWindow(app)}
              className="flex flex-col items-center gap-2 p-3 rounded-lg hover:bg-white/10 transition-colors"
            >
              <div className={`${app.color} p-3 rounded-xl shadow-lg`}>
                <app.icon className="w-6 h-6 text-white" />
              </div>
              <span className="text-white text-xs font-medium">{app.name}</span>
            </button>
          ))}
        </div>

        {/* Windows */}
        {windows.map(win => (
          <Window
            key={win.id}
            window={win}
            isActive={activeWindow === win.id}
            onClose={() => closeWindow(win.id)}
            onMinimize={() => minimizeWindow(win.id)}
            onMaximize={() => toggleMaximize(win.id)}
            onFocus={() => setActiveWindow(win.id)}
            setWindows={setWindows}
            windows={windows}
            createWindow={createWindow}
          />
        ))}

        {/* Notifications */}
        <div className="absolute top-4 right-4 space-y-2 z-50">
          {notifications.map(notif => (
            <div
              key={notif.id}
              className="bg-black/80 backdrop-blur-xl text-white px-4 py-3 rounded-lg shadow-2xl border border-white/10 animate-slide-in max-w-sm"
            >
              <div className="flex items-start gap-3">
                <Bell className="w-5 h-5 text-blue-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">{notif.message}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {notif.time.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Taskbar */}
      <div className="absolute bottom-0 left-0 right-0 h-16 bg-black/40 backdrop-blur-xl border-t border-white/10 flex items-center px-4 gap-2">
        {/* Start Button */}
        <button
          onClick={() => setStartMenuOpen(!startMenuOpen)}
          className="h-10 w-10 rounded-lg bg-white/10 hover:bg-white/20 transition-colors flex items-center justify-center"
        >
          <Menu className="w-5 h-5 text-white" />
        </button>

        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="h-10 bg-white/10 rounded-lg flex items-center px-3 gap-2">
            <Search className="w-4 h-4 text-white/60" />
            <input
              type="text"
              placeholder="Search apps, files, settings..."
              className="flex-1 bg-transparent text-white text-sm outline-none placeholder-white/40"
            />
          </div>
        </div>

        {/* Running Apps */}
        <div className="flex-1 flex items-center gap-2">
          {windows.map(win => (
            <button
              key={win.id}
              onClick={() => win.minimized ? restoreWindow(win.id) : setActiveWindow(win.id)}
              className={`h-10 px-4 rounded-lg flex items-center gap-2 transition-colors ${
                activeWindow === win.id && !win.minimized
                  ? 'bg-white/20'
                  : 'bg-white/10 hover:bg-white/15'
              }`}
            >
              <win.app.icon className="w-4 h-4 text-white" />
              <span className="text-white text-sm">{win.app.name}</span>
            </button>
          ))}
        </div>

        {/* System Tray */}
        <div className="flex items-center gap-2">
          <button className="h-8 w-8 rounded-lg hover:bg-white/10 flex items-center justify-center transition-colors">
            <Wifi className="w-4 h-4 text-white" />
          </button>
          <button className="h-8 w-8 rounded-lg hover:bg-white/10 flex items-center justify-center transition-colors">
            <Volume2 className="w-4 h-4 text-white" />
          </button>
          <button className="h-8 w-8 rounded-lg hover:bg-white/10 flex items-center justify-center transition-colors">
            <Battery className="w-4 h-4 text-white" />
          </button>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="h-8 w-8 rounded-lg hover:bg-white/10 flex items-center justify-center transition-colors relative"
          >
            <Bell className="w-4 h-4 text-white" />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            )}
          </button>
          <div className="ml-2 px-3 h-10 flex items-center">
            <span className="text-white text-sm font-medium">
              {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
      </div>

      {/* Start Menu */}
      {startMenuOpen && (
        <div className="absolute bottom-20 left-4 w-[32rem] bg-black/70 backdrop-blur-xl rounded-2xl border border-white/10 p-6 shadow-2xl">
          <div className="mb-6">
            <h3 className="text-white text-2xl font-bold mb-1">Welcome back!</h3>
            <p className="text-white/60 text-sm">What would you like to do today?</p>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {apps.map((app, idx) => (
              <button
                key={idx}
                onClick={() => createWindow(app)}
                className="flex flex-col items-center gap-3 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
              >
                <div className={`${app.color} p-3 rounded-xl shadow-lg`}>
                  <app.icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-white text-sm font-medium">{app.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="absolute bg-black/80 backdrop-blur-xl rounded-lg shadow-2xl border border-white/20 py-2 min-w-48 z-50"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <button
            onClick={() => {
              addNotification('Refreshing desktop...');
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-white text-sm hover:bg-white/10 transition-colors"
          >
            Refresh
          </button>
          <button
            onClick={() => {
              createWindow(apps[0]);
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-white text-sm hover:bg-white/10 transition-colors"
          >
            New Folder
          </button>
          <div className="h-px bg-white/10 my-2"></div>
          <button
            onClick={() => {
              createWindow(apps[2]);
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-white text-sm hover:bg-white/10 transition-colors"
          >
            Display Settings
          </button>
          <button
            onClick={() => {
              createWindow(apps[3]);
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-white text-sm hover:bg-white/10 transition-colors"
          >
            System Monitor
          </button>
        </div>
      )}

      {/* Notification Center */}
      {showNotifications && (
        <div className="absolute bottom-20 right-4 w-80 bg-black/70 backdrop-blur-xl rounded-2xl border border-white/10 p-4 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold">Notifications</h3>
            <button 
              onClick={() => setNotifications([])}
              className="text-white/60 hover:text-white text-xs transition-colors"
            >
              Clear all
            </button>
          </div>
          {notifications.length === 0 ? (
            <p className="text-white/40 text-sm text-center py-8">No new notifications</p>
          ) : (
            <div className="space-y-2">
              {notifications.map(notif => (
                <div key={notif.id} className="bg-white/5 rounded-lg p-3">
                  <p className="text-white text-sm">{notif.message}</p>
                  <p className="text-white/40 text-xs mt-1">
                    {notif.time.toLocaleTimeString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const Window = ({ window, isActive, onClose, onMinimize, onMaximize, onFocus, setWindows, windows, createWindow }) => {
  const [dragging, setDragging] = useState(false);
  const [resizing, setResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const windowRef = useRef(null);

  const handleMouseDown = (e) => {
    if (e.target.closest('.window-controls')) return;
    onFocus();
    setDragging(true);
    setDragStart({
      x: e.clientX - window.position.x,
      y: e.clientY - window.position.y
    });
  };

  const handleMouseMove = (e) => {
    if (dragging) {
      const newX = e.clientX - dragStart.x;
      const newY = Math.max(0, e.clientY - dragStart.y);
      setWindows(windows.map(w =>
        w.id === window.id ? { ...w, position: { x: newX, y: newY } } : w
      ));
    }
    if (resizing) {
      const newWidth = Math.max(400, e.clientX - window.position.x);
      const newHeight = Math.max(300, e.clientY - window.position.y);
      setWindows(windows.map(w =>
        w.id === window.id ? { ...w, size: { width: newWidth, height: newHeight } } : w
      ));
    }
  };

  const handleMouseUp = () => {
    setDragging(false);
    setResizing(false);
  };

  useEffect(() => {
    if (dragging || resizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [dragging, resizing]);

  if (window.minimized) return null;

  const style = window.maximized
    ? { top: 0, left: 0, right: 0, bottom: '4rem', width: '100%', height: 'calc(100% - 4rem)' }
    : {
        left: `${window.position.x}px`,
        top: `${window.position.y}px`,
        width: `${window.size.width}px`,
        height: `${window.size.height}px`
      };

  return (
    <div
      ref={windowRef}
      style={style}
      className={`absolute bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col ${
        isActive ? 'z-50' : 'z-40'
      }`}
      onClick={onFocus}
    >
      {/* Title Bar */}
      <div
        onMouseDown={handleMouseDown}
        className="h-12 bg-gradient-to-r from-gray-100 to-gray-50 border-b border-gray-200 flex items-center justify-between px-4 cursor-move select-none"
      >
        <div className="flex items-center gap-3">
          <div className={`${window.app.color} p-1.5 rounded-lg`}>
            <window.app.icon className="w-4 h-4 text-white" />
          </div>
          <span className="text-gray-800 font-medium text-sm">{window.app.name}</span>
        </div>
        <div className="flex items-center gap-2 window-controls">
          <button
            onClick={onMinimize}
            className="w-8 h-8 rounded-lg hover:bg-gray-200 flex items-center justify-center transition-colors"
          >
            <Minimize2 className="w-4 h-4 text-gray-600" />
          </button>
          <button
            onClick={onMaximize}
            className="w-8 h-8 rounded-lg hover:bg-gray-200 flex items-center justify-center transition-colors"
          >
            <Maximize2 className="w-4 h-4 text-gray-600" />
          </button>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-red-500 hover:text-white flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Window Content */}
      <div className="flex-1 overflow-auto">
        <AppContent app={window.app} data={window.data} createWindow={createWindow} />
      </div>

      {/* Resize Handle */}
      {!window.maximized && (
        <div
          onMouseDown={(e) => {
            e.stopPropagation();
            setResizing(true);
          }}
          className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize"
        />
      )}
    </div>
  );
};

const AppContent = ({ app, data, createWindow }) => {
  const appComponents = {
    Files: FilesApp,
    Terminal: TerminalApp,
    Notepad: NotepadApp,
    Browser: BrowserApp,
    Settings: SettingsApp,
    Monitor: MonitorApp
  };

  const Component = appComponents[app.name];
  
  return Component ? <Component data={data} createWindow={createWindow} /> : <p className="text-gray-600 p-6">Application content</p>;
};

export default WebOS;