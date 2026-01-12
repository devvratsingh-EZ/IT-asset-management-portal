/**
 * API Service Layer
 * Handles all HTTP requests to the FastAPI backend
 * Currently returns mock data - will be connected to real API endpoints
 */

import { APP_CONFIG } from '../data/constants';

const API_BASE_URL = APP_CONFIG.apiBaseUrl;

/**
 * Generic fetch wrapper with error handling
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} Response data
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Authentication Service
 */
export const authService = {
  /**
   * Login user
   * @param {string} username 
   * @param {string} password 
   * @returns {Promise} User data and token
   */
  async login(username, password) {
    // TODO: Implement actual API call
    // return fetchApi('/auth/login', {
    //   method: 'POST',
    //   body: JSON.stringify({ username, password }),
    // });
    
    // Mock implementation
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // This will be replaced with actual API call
        resolve({ success: true, username });
      }, 800);
    });
  },

  /**
   * Logout user
   * @returns {Promise}
   */
  async logout() {
    // TODO: Implement actual API call
    // return fetchApi('/auth/logout', { method: 'POST' });
    return Promise.resolve({ success: true });
  },

  /**
   * Verify authentication token
   * @returns {Promise} User data if token is valid
   */
  async verifyToken() {
    // TODO: Implement actual API call
    // return fetchApi('/auth/verify');
    return Promise.resolve({ valid: false });
  },
};

/**
 * Asset Service
 */
export const assetService = {
  /**
   * Get asset by ID
   * @param {string} assetId 
   * @returns {Promise} Asset data
   */
  async getAsset(assetId) {
    // TODO: Implement actual API call
    // return fetchApi(`/assets/${assetId}`);
    return Promise.resolve(null);
  },

  /**
   * Update asset information
   * @param {string} assetId 
   * @param {object} data - Updated asset data
   * @returns {Promise} Updated asset
   */
  async updateAsset(assetId, data) {
    // TODO: Implement actual API call
    // return fetchApi(`/assets/${assetId}`, {
    //   method: 'PUT',
    //   body: JSON.stringify(data),
    // });
    return Promise.resolve({ success: true, ...data });
  },

  /**
   * Get asset assignment history
   * @param {string} assetId 
   * @returns {Promise} Assignment history array
   */
  async getAssignmentHistory(assetId) {
    // TODO: Implement actual API call
    // return fetchApi(`/assets/${assetId}/history`);
    return Promise.resolve([]);
  },

  /**
   * Upload asset image
   * @param {string} assetId 
   * @param {File} imageFile 
   * @returns {Promise} Upload result
   */
  async uploadImage(assetId, imageFile) {
    // TODO: Implement actual API call with FormData
    // const formData = new FormData();
    // formData.append('image', imageFile);
    // return fetchApi(`/assets/${assetId}/image`, {
    //   method: 'POST',
    //   headers: {}, // Let browser set content-type for FormData
    //   body: formData,
    // });
    return Promise.resolve({ success: true, filename: imageFile.name });
  },

  /**
   * Upload asset documents
   * @param {string} assetId 
   * @param {File[]} files 
   * @returns {Promise} Upload result
   */
  async uploadDocuments(assetId, files) {
    // TODO: Implement actual API call with FormData
    // const formData = new FormData();
    // files.forEach((file, index) => {
    //   formData.append(`document_${index}`, file);
    // });
    // return fetchApi(`/assets/${assetId}/documents`, {
    //   method: 'POST',
    //   headers: {},
    //   body: formData,
    // });
    return Promise.resolve({ 
      success: true, 
      uploaded: files.map(f => f.name) 
    });
  },
};

/**
 * Employee Service
 */
export const employeeService = {
  /**
   * Get all employees
   * @returns {Promise} Employees object
   */
  async getEmployees() {
    // TODO: Implement actual API call
    // return fetchApi('/employees');
    return Promise.resolve({});
  },

  /**
   * Get employee by ID
   * @param {string} employeeId 
   * @returns {Promise} Employee data
   */
  async getEmployee(employeeId) {
    // TODO: Implement actual API call
    // return fetchApi(`/employees/${employeeId}`);
    return Promise.resolve(null);
  },
};

export default {
  auth: authService,
  asset: assetService,
  employee: employeeService,
};
