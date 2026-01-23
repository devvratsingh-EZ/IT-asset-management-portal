/**
 * Centralized API Service Layer with automatic token refresh and logging
 */

import { APP_CONFIG } from '../data/constants';

const API_BASE_URL = APP_CONFIG.apiBaseUrl;

// Logger utility
const logger = {
  log: (endpoint, method, message, extra = {}) => {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] ${method} ${endpoint} - ${message}`, extra);
  },
  success: (endpoint, method, message, extra = {}) => {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`%c[${timestamp}] ${method} ${endpoint} - ✓ ${message}`, 'color: green; font-weight: bold;', extra);
  },
  auth: (endpoint, method, status, message, extra = {}) => {
    const timestamp = new Date().toLocaleTimeString();
    const color = status === 'pass' ? 'color: green;' : 'color: red;';
    console.log(`%c[${timestamp}] ${method} ${endpoint} - AUTH ${status.toUpperCase()} - ${message}`, color, extra);
  },
  error: (endpoint, method, message, extra = {}) => {
    const timestamp = new Date().toLocaleTimeString();
    console.error(`[${timestamp}] ${method} ${endpoint} - ✗ ${message}`, extra);
  }
};

/**
 * Decode JWT payload (client-side, no verification needed)
 * This is safe because we only use it to extract claims before verifying the token
 */
function decodeJWT(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const decoded = JSON.parse(atob(parts[1]));
    return decoded;
  } catch (error) {
    return null;
  }
}

// In-memory token storage (not localStorage)
let accessToken = null;
let tokenExpiresAt = null;
let isRefreshing = false;
let refreshSubscribers = [];

/**
 * Token management
 */
export const tokenManager = {
  setToken(token, expiresAt) {
    accessToken = token;
    tokenExpiresAt = expiresAt;
    logger.log('TOKEN', 'SET', 'Token stored in memory', { expiresAt });
  },
  
  getToken() {
    return accessToken;
  },
  
  clearToken() {
    logger.log('TOKEN', 'CLEAR', 'Token cleared from memory');
    accessToken = null;
    tokenExpiresAt = null;
  },
  
  isExpired() {
    if (!tokenExpiresAt) return true;
    return new Date(tokenExpiresAt) < new Date();
  }
};

/**
 * Subscribe to token refresh completion
 */
function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback);
}

function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach(callback => callback(newToken));
  refreshSubscribers = [];
}

function onRefreshFailed() {
  refreshSubscribers.forEach(callback => callback(null));
  refreshSubscribers = [];
}

/**
 * Refresh access token using HttpOnly cookie
 */
async function refreshAccessToken() {
  const endpoint = '/auth/refresh';
  const method = 'POST';
  
  logger.log(endpoint, method, 'Attempting token refresh');
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      const data = await response.json();
      tokenManager.setToken(data.access_token, data.expires_at);
      logger.success(endpoint, method, 'Token refreshed successfully');
      return data.access_token;
    } else {
      logger.auth(endpoint, method, 'fail', 'Token refresh rejected', { status: response.status });
      return null;
    }
  } catch (error) {
    logger.error(endpoint, method, 'Token refresh failed', error);
    return null;
  }
}

/**
 * Generic fetch wrapper with 401 handling and auto-retry
 */
async function fetchApi(endpoint, options = {}, method = 'GET') {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  // Add auth header if token exists
  if (accessToken) {
    defaultHeaders['Authorization'] = `Bearer ${accessToken}`;
  }

  const config = {
    ...options,
    credentials: 'include',
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  // Log the API call being made
  logger.log(endpoint, method, 'API call initiated', { hasToken: !!accessToken });

  try {
    let response = await fetch(url, config);
    
    // Handle 401 - try refresh
    if (response.status === 401 && !options._isRetry) {
      logger.auth(endpoint, method, 'fail', 'Unauthorized (401) - Attempting token refresh');
      
      if (!isRefreshing) {
        isRefreshing = true;
        
        const newToken = await refreshAccessToken();
        isRefreshing = false;
        
        if (newToken) {
          logger.auth(endpoint, method, 'pass', 'Token refreshed, retrying request');
          onTokenRefreshed(newToken);
          
          // Retry original request with new token
          config.headers['Authorization'] = `Bearer ${newToken}`;
          config._isRetry = true;
          return fetchApi(endpoint, config, method);
        } else {
          onRefreshFailed();
          logger.auth(endpoint, method, 'fail', 'Token refresh failed - Session expired');
          window.dispatchEvent(new CustomEvent('auth:logout'));
          throw new Error('Session expired. Please login again.');
        }
      } else {
        // Wait for ongoing refresh
        logger.log(endpoint, method, 'Waiting for ongoing token refresh');
        return new Promise((resolve, reject) => {
          subscribeTokenRefresh((newToken) => {
            if (newToken) {
              config.headers['Authorization'] = `Bearer ${newToken}`;
              config._isRetry = true;
              resolve(fetchApi(endpoint, config, method));
            } else {
              logger.auth(endpoint, method, 'fail', 'Token refresh failed after waiting');
              reject(new Error('Session expired. Please login again.'));
            }
          });
        });
      }
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const errorMsg = error.detail || error.message || `HTTP error! status: ${response.status}`;
      logger.error(endpoint, method, errorMsg, { status: response.status });
      throw new Error(errorMsg);
    }
    
    const data = await response.json();
    logger.success(endpoint, method, 'Response received', { dataKeys: Object.keys(data).join(', ') });
    return data;
  } catch (error) {
    logger.error(endpoint, method, error.message, error);
    throw error;
  }
}

/**
 * Authentication Service
 */
export const authService = {
  async login(username, password) {
    const endpoint = '/auth/login';
    const method = 'POST';
    
    logger.log(endpoint, method, 'Login attempt', { username });
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        tokenManager.setToken(data.token, data.expires_at);
        logger.auth(endpoint, method, 'pass', `Login successful for user: ${username}`);
      } else {
        logger.auth(endpoint, method, 'fail', `Login failed for user: ${username}`, data);
      }
      
      return { response, data };
    } catch (error) {
      logger.error(endpoint, method, `Login error for user: ${username}`, error);
      throw error;
    }
  },

  async logout() {
    const endpoint = '/auth/logout';
    const method = 'POST';
    
    logger.log(endpoint, method, 'Logout initiated');
    
    try {
      await fetchApi(endpoint, { method }, method);
      logger.success(endpoint, method, 'Logout successful');
    } catch (e) {
      logger.error(endpoint, method, 'Logout failed (continuing anyway)', e);
    }
    tokenManager.clearToken();
  },

  async verifyToken() {
    const endpoint = '/auth/verify';
    const method = 'GET';
    
    // If we have an access token in memory, verify it
    if (accessToken) {
      logger.log(endpoint, method, 'Token found in memory - verifying');
      
      try {
        const data = await fetchApi(endpoint, {}, method);
        if (data.valid) {
          logger.auth(endpoint, method, 'pass', 'Token verified');
          return { valid: true, ...data };
        }
      } catch (error) {
        logger.log(endpoint, method, 'Token verification failed, attempting refresh');
      }
    }
    
    // No token in memory, but refresh token cookie might exist
    // Attempt to refresh using the cookie
    logger.log(endpoint, method, 'No token in memory - attempting refresh from cookie');
    
    try {
      const newToken = await refreshAccessToken();
      if (newToken) {
        // Decode to get user info
        const payload = decodeJWT(newToken);
        logger.auth(endpoint, method, 'pass', 'Session restored via token refresh');
        return { 
          valid: true, 
          token: newToken,
          username: payload?.username,
          full_name: payload?.full_name
        };
      }
    } catch (error) {
      logger.log(endpoint, method, 'Token refresh failed');
    }
    
    logger.auth(endpoint, method, 'fail', 'Session not found - user must login');
    return { valid: false };
  },
};

/**
 * Asset Service
 */
export const assetService = {
  async getAssets() {
    return fetchApi('/assets', {}, 'GET');
  },

  async getAsset(assetId) {
    return fetchApi(`/assets/${assetId}`, {}, 'GET');
  },

  async createAsset(data) {
    return fetchApi('/assets', { 
      method: 'POST',
      body: JSON.stringify(data),
    }, 'POST');
  },

  async updateAsset(assetId, data) {
    return fetchApi(`/assets/${assetId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, 'PUT');
  },

  async deleteAsset(assetId) {
    return fetchApi(`/assets/${assetId}`, {
      method: 'DELETE',
    }, 'DELETE');
  },

  async bulkDeleteAssets(assetIds) {
    return fetchApi('/assets/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ asset_ids: assetIds }),
    }, 'POST');
  },

  async getAssetTypes() {
    return fetchApi('/assets/asset-types', {}, 'GET');
  },

  async getSpecifications(typeName) {
    if (typeName) {
      return fetchApi(`/assets/specifications/${typeName}`, {}, 'GET');
    }
    return fetchApi('/assets/specifications', {}, 'GET');
  },

  async getAssignmentHistory(assetId) {
    return fetchApi(`/assignment-history/${assetId}`, {}, 'GET');
  },

  async getAllAssignmentHistory() {
    return fetchApi('/assignment-history', {}, 'GET');
  },
};

/**
 * Employee Service
 */
export const employeeService = {
  async getEmployees() {
    return fetchApi('/employees', {}, 'GET');
  },

  async getEmployee(employeeId) {
    return fetchApi(`/employees/${employeeId}`, {}, 'GET');
  },
};

/**
 * Summary Service
 */
export const summaryService = {
  async getSummaryData() {
    return fetchApi('/summary', {}, 'GET');
  },

  async getHealth() {
    return fetchApi('/health', {}, 'GET');
  },
};

export default {
  auth: authService,
  asset: assetService,
  employee: employeeService,
  summary: summaryService,
  tokenManager,
  logger,
};