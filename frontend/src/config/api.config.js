/**
 * API Configuration
 * 
 * This file contains environment-specific API settings
 * allowing the frontend to connect to different backend environments
 * and to use mock data during development
 */

// Determine the environment
const ENV = process.env.REACT_APP_ENV || 'development';

// Base API URL by environment
const API_BASE_URLS = {
  development: 'http://localhost:8000/api/v1',
  testing: 'http://test-api.warehouse-vision.com/api/v1',
  staging: 'https://staging-api.warehouse-vision.com/api/v1',
  production: 'https://api.warehouse-vision.com/api/v1'
};

// API configuration
const API_CONFIG = {
  // Current environment
  env: ENV,
  
  // Whether to use mock data (only in development)
  useMocks: ENV === 'development' && (process.env.REACT_APP_USE_MOCKS === 'true' || true),
  
  // Base URL for API calls
  baseURL: API_BASE_URLS[ENV] || API_BASE_URLS.development,
  
  // API endpoints
  endpoints: {
    // Authentication endpoints
    auth: {
      login: '/auth/login',
      logout: '/auth/logout',
      refresh: '/auth/refresh',
      register: '/auth/register',
      forgotPassword: '/auth/forgot-password',
      resetPassword: '/auth/reset-password',
      verify: '/auth/verify'
    },
    
    // User management endpoints
    users: {
      base: '/users',
      current: '/users/me',
      byId: (id) => `/users/${id}`
    },
    
    // Gunny bag counter endpoints
    gunny: {
      counts: '/gunny/counts',
      count: '/gunny/count',
      countById: (id) => `/gunny/counts/${id}`,
      latest: (location) => `/gunny/counts/latest?location=${encodeURIComponent(location)}`,
      analytics: '/gunny/analytics'
    },
    
    // Vehicle recognition endpoints
    vehicle: {
      vehicles: '/vehicles',
      vehicleById: (id) => `/vehicles/${id}`,
      detect: '/vehicles/detect',
      entries: (vehicleId) => `/vehicles/${vehicleId}/entries`,
      authorize: (vehicleId) => `/vehicles/${vehicleId}/authorize`,
      unauthorized: '/vehicles/unauthorized',
      analytics: '/vehicles/analytics'
    },
    
    // Facial recognition endpoints
    facial: {
      persons: '/persons',
      personById: (id) => `/persons/${id}`,
      recognize: '/persons/recognize',
      register: '/persons/register',
      access: {
        logs: '/access/logs',
        grant: '/access/grant',
        revoke: '/access/revoke'
      }
    },
    
    // Contextual intelligence endpoints
    contextual: {
      search: '/context/search',
      upload: '/context/upload',
      results: '/context/results',
      resultById: (id) => `/context/results/${id}`,
      analytics: '/context/analytics'
    }
  },
  
  // Request timeout in milliseconds
  timeout: 30000,
  
  // Default headers to include with all requests
  defaultHeaders: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

export default API_CONFIG;