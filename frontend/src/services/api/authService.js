import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Authentication API Service
 * Handles API calls related to user authentication
 */
const authService = {
  /**
   * Login user with username/password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise} - Authentication response
   */
  login: async (email, password) => {
    try {
      // For development/demo purposes - bypassing API call
      // In a real application, replace this with an actual API call
      if (email === 'admin@warehouse.com' && password === 'password123') {
        return {
          user: {
            id: '1',
            email: email,
            name: 'Admin User',
            role: 'admin'
          },
          token: 'demo-auth-token',
          authenticated: true
        };
      }

      // For fallback testing credentials
      if (email === 'test@example.com' && password === 'password') {
        return {
          user: {
            id: '2',
            email: email,
            name: 'Test User',
            role: 'user'
          },
          token: 'demo-auth-token',
          authenticated: true
        };
      }
      
      // If no matches, throw authentication error
      throw new Error('Invalid email or password');
    } catch (error) {
      // Format error message
      const errorMsg = error.response?.data?.message || 
        error.response?.data?.detail || 
        error.message ||
        'Authentication failed. Please check your credentials.';
      throw new Error(errorMsg);
    }
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      // Clear any session data
      return true;
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if API call fails
      return true;
    }
  }
};

export default authService;