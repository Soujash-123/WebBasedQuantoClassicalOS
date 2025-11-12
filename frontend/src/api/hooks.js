/**
 * React Hooks for API Integration
 * Custom hooks for fetching and managing backend data
 */

import { useState, useEffect, useCallback } from 'react';
import apiClient from './client';

/**
 * Hook for fetching data with loading and error states
 */
export const useAPI = (apiFunction, dependencies = [], options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { autoFetch = true, onSuccess, onError } = options;

  const fetchData = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFunction(...args);
      setData(result);
      if (onSuccess) onSuccess(result);
      return result;
    } catch (err) {
      setError(err.message);
      if (onError) onError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunction, onSuccess, onError]);

  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, dependencies);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook for system information
 */
export const useSystemInfo = () => {
  return useAPI(() => apiClient.getSystemInfo());
};

/**
 * Hook for system status with auto-refresh
 */
export const useSystemStatus = (refreshInterval = 5000) => {
  const { data, loading, error, refetch } = useAPI(() => apiClient.getSystemStatus());

  useEffect(() => {
    if (refreshInterval) {
      const interval = setInterval(refetch, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, refetch]);

  return { data, loading, error, refetch };
};

/**
 * Hook for file listing
 */
export const useFiles = (path = '/') => {
  const [currentPath, setCurrentPath] = useState(path);
  const { data, loading, error, refetch } = useAPI(
    () => apiClient.listFiles(currentPath),
    [currentPath]
  );

  const navigateTo = (newPath) => {
    setCurrentPath(newPath);
  };

  return { 
    files: data?.files || [], 
    count: data?.count || 0,
    currentPath,
    loading, 
    error, 
    refetch,
    navigateTo
  };
};

/**
 * Hook for terminal command execution
 */
export const useTerminal = () => {
  const [history, setHistory] = useState(['WebOS Terminal v1.0.0', 'Type "help" for available commands']);
  const [currentDirectory, setCurrentDirectory] = useState('~');
  const [loading, setLoading] = useState(false);

  const executeCommand = async (command, args = []) => {
    setLoading(true);
    try {
      const result = await apiClient.executeCommand(command, args);
      
      // Handle cd command to update current directory
      if (command.startsWith('cd ')) {
        const newDir = command.slice(3).trim();
        if (newDir) {
          setCurrentDirectory(newDir === '~' ? '~' : newDir);
        }
      }
      
      setHistory(prev => [...prev, `user@webos:${currentDirectory}$ ${command}`, result.output]);
      return result;
    } catch (error) {
      setHistory(prev => [...prev, `user@webos:${currentDirectory}$ ${command}`, `Error: ${error.message}`]);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setHistory(['WebOS Terminal v1.0.0']);
    setCurrentDirectory('~');
  };

  return { history, currentDirectory, executeCommand, clearHistory, loading };
};

/**
 * Hook for process list with auto-refresh
 */
export const useProcesses = (refreshInterval = 3000) => {
  const { data, loading, error, refetch } = useAPI(() => apiClient.listProcesses());

  useEffect(() => {
    if (refreshInterval) {
      const interval = setInterval(refetch, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, refetch]);

  return { 
    processes: data?.processes || [], 
    count: data?.count || 0,
    loading, 
    error, 
    refetch 
  };
};

/**
 * Hook for process statistics with auto-refresh
 */
export const useProcessStats = (refreshInterval = 2000) => {
  const { data, loading, error, refetch } = useAPI(() => apiClient.getProcessStats());

  useEffect(() => {
    if (refreshInterval) {
      const interval = setInterval(refetch, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, refetch]);

  return { stats: data?.stats || {}, loading, error, refetch };
};

/**
 * Hook for system uptime with auto-refresh
 */
export const useUptime = (refreshInterval = 1000) => {
  const { data, loading, error, refetch } = useAPI(() => apiClient.getSystemUptime());

  useEffect(() => {
    if (refreshInterval) {
      const interval = setInterval(refetch, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, refetch]);

  return { 
    uptime: data?.uptime_formatted || '0h 0m 0s',
    uptimeSeconds: data?.uptime_seconds || 0,
    startTime: data?.start_time,
    loading, 
    error, 
    refetch 
  };
};

/**
 * Hook for available commands
 */
export const useCommands = () => {
  return useAPI(() => apiClient.getShellCommands());
};
