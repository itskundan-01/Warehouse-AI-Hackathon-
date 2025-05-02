import axios from 'axios';
import API_CONFIG from '../../config/api.config';
import store from '../../store';
import { addAlert } from '../../store/slices/uiSlice';
import { logout } from '../../store/slices/authSlice';

/**
 * Create and configure Axios instance for API calls
 */
export const apiClient = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: API_CONFIG.defaultHeaders
});

/**
 * Helper function to create a mock response that mimics axios response structure
 * @param {Object} data - The mock data to return
 * @param {number} status - HTTP status code (default: 200)
 * @returns {Promise} - A promise that resolves with a mock axios response
 */
export const mockResponse = (data, status = 200) => {
  return new Promise((resolve) => {
    // Add a small delay to simulate network latency
    setTimeout(() => {
      resolve({
        data,
        status,
        statusText: status === 200 ? 'OK' : 'Error',
        headers: {},
        config: {}
      });
    }, 300);
  });
};

/**
 * Configure request interceptor to add auth token
 */
apiClient.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth?.token;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Configure response interceptor for global error handling
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Handle different error situations
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - user needs to login again
          store.dispatch(logout());
          store.dispatch(addAlert({
            type: 'error',
            message: 'Your session has expired. Please log in again.',
            autoHide: true
          }));
          break;
          
        case 403:
          // Forbidden - user doesn't have permission
          store.dispatch(addAlert({
            type: 'error',
            message: 'You don\'t have permission to perform this action.',
            autoHide: true
          }));
          break;
          
        case 404:
          // Not found
          console.warn('Resource not found:', error.config.url);
          break;
          
        case 500:
        case 502:
        case 503:
        case 504:
          // Server errors
          store.dispatch(addAlert({
            type: 'error',
            message: 'Server error. Please try again later.',
            autoHide: true
          }));
          break;
          
        default:
          // Other error codes
          if (data?.message) {
            store.dispatch(addAlert({
              type: 'error',
              message: data.message,
              autoHide: true
            }));
          }
      }
    } else if (error.request) {
      // The request was made but no response was received
      store.dispatch(addAlert({
        type: 'error',
        message: 'Network error. Please check your connection.',
        autoHide: true
      }));
    } else {
      // Something happened in setting up the request that triggered an Error
      store.dispatch(addAlert({
        type: 'error',
        message: error.message,
        autoHide: true
      }));
    }
    
    return Promise.reject(error);
  }
);

/**
 * Base Service class for API services
 * All specific API services should extend this class
 */
export default class BaseService {
  /**
   * @param {string} endpoint - Base endpoint for this service
   * @param {Object} mockData - Mock data for this service
   */
  constructor(endpoint, mockData = {}) {
    this.endpoint = endpoint;
    this.mockData = mockData;
  }

  /**
   * Get a list of resources
   * @param {Object} params - Optional query parameters
   * @returns {Promise} - API response
   */
  getAll(params = {}) {
    if (API_CONFIG.useMocks && this.mockData) {
      return mockResponse(this.mockData);
    }
    return apiClient.get(this.endpoint, { params });
  }

  /**
   * Get a specific resource by ID
   * @param {string|number} id - Resource ID
   * @returns {Promise} - API response
   */
  getById(id) {
    if (API_CONFIG.useMocks && this.mockData && this.mockData.data) {
      const item = this.mockData.data.find(i => i.id === id);
      return mockResponse(item || { error: 'Not found' });
    }
    return apiClient.get(`${this.endpoint}/${id}`);
  }

  /**
   * Create a new resource
   * @param {Object} data - Resource data
   * @returns {Promise} - API response
   */
  create(data) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        ...data,
        id: `mock-${Date.now()}`,
        created_at: new Date().toISOString()
      });
    }
    return apiClient.post(this.endpoint, data);
  }

  /**
   * Update an existing resource
   * @param {string|number} id - Resource ID
   * @param {Object} data - Updated resource data
   * @returns {Promise} - API response
   */
  update(id, data) {
    if (API_CONFIG.useMocks && this.mockData && this.mockData.data) {
      const item = this.mockData.data.find(i => i.id === id);
      if (!item) {
        return mockResponse({ error: 'Not found' }, 404);
      }
      
      return mockResponse({
        ...item,
        ...data,
        updated_at: new Date().toISOString()
      });
    }
    return apiClient.put(`${this.endpoint}/${id}`, data);
  }

  /**
   * Partially update an existing resource
   * @param {string|number} id - Resource ID
   * @param {Object} data - Partial resource data
   * @returns {Promise} - API response
   */
  patch(id, data) {
    if (API_CONFIG.useMocks && this.mockData && this.mockData.data) {
      const item = this.mockData.data.find(i => i.id === id);
      if (!item) {
        return mockResponse({ error: 'Not found' }, 404);
      }
      
      return mockResponse({
        ...item,
        ...data,
        updated_at: new Date().toISOString()
      });
    }
    return apiClient.patch(`${this.endpoint}/${id}`, data);
  }

  /**
   * Delete a resource
   * @param {string|number} id - Resource ID
   * @returns {Promise} - API response
   */
  delete(id) {
    if (API_CONFIG.useMocks) {
      return mockResponse({ success: true });
    }
    return apiClient.delete(`${this.endpoint}/${id}`);
  }
}