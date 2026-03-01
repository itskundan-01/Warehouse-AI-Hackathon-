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
      // Make API call to backend for authentication
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      });

      // Store authentication token
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
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