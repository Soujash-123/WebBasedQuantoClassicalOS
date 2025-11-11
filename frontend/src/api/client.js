/**
 * API Client for Web-Based Virtual OS Backend
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // System APIs
  async getSystemInfo() {
    return this.request('/system/info');
  }

  async getSystemStatus() {
    return this.request('/system/status');
  }

  async getSystemLayers() {
    return this.request('/system/layers');
  }

  async getSystemCommands() {
    return this.request('/system/commands');
  }

  async getSystemUptime() {
    return this.request('/system/uptime');
  }

  async getSystemConfig() {
    return this.request('/system/config');
  }

  async reloadSystem() {
    return this.request('/system/reload', { method: 'POST' });
  }

  // Shell APIs
  async executeCommand(command) {
    // Send the complete command as a single string
    return this.request('/shell/execute', {
      method: 'POST',
      body: JSON.stringify({ command }),
    });
  }

  async getShellCommands() {
    return this.request('/shell/commands');
  }

  async getCommandInfo(commandName) {
    return this.request(`/shell/command/${commandName}`);
  }

  async executeBatchCommands(commands) {
    return this.request('/shell/batch', {
      method: 'POST',
      body: JSON.stringify(commands),
    });
  }

  // File APIs
  async listFiles(path = '/') {
    return this.request(`/files/list?path=${encodeURIComponent(path)}`);
  }

  async readFile(path) {
    return this.request('/files/read', {
      method: 'POST',
      body: JSON.stringify({ path })
    });
  }
  
  async writeFile(path, content, mode = 'w') {
    return this.request('/files/write', {
      method: 'POST',
      body: JSON.stringify({ path, content, mode }),
    });
  }

  async deleteFile(path) {
    return this.request('/files/delete', {
      method: 'POST',
      body: JSON.stringify({ path }),
    });
  }

  async createDirectory(path) {
    return this.request('/files/mkdir', {
      method: 'POST',
      body: JSON.stringify({ path }),
    });
  }

  async getFileInfo(path) {
    return this.request(`/files/info?path=${encodeURIComponent(path)}`);
  }

  async getDirectoryTree(path = '/', maxDepth = 3) {
    return this.request(`/files/tree?path=${encodeURIComponent(path)}&max_depth=${maxDepth}`);
  }

  // Process APIs
  async listProcesses() {
    return this.request('/process/list');
  }

  async getProcessInfo(pid) {
    return this.request(`/process/info/${pid}`);
  }

  async startProcess(name, command = null, args = []) {
    return this.request('/process/start', {
      method: 'POST',
      body: JSON.stringify({ name, command, args }),
    });
  }

  async stopProcess(pid) {
    return this.request('/process/stop', {
      method: 'POST',
      body: JSON.stringify({ pid }),
    });
  }

  async getProcessStats() {
    return this.request('/process/stats');
  }

  // Health & Utility
  async healthCheck() {
    return this.request('/health');
  }

  async getHotReloadStatus() {
    return this.request('/hot-reload/status');
  }

  async triggerHotReload() {
    return this.request('/hot-reload/trigger', { method: 'POST' });
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
