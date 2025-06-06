import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../services/api/authService';

/**
 * Auth Slice for Redux
 *
 * Handles authentication-related state and actions.
 */

// Initial state
const initialState = {
  isAuthenticated: !!localStorage.getItem('token'), // Check token on init
  user: JSON.parse(localStorage.getItem('user')) || null, // Restore user data
  loading: false,
  error: null,
  token: localStorage.getItem('token') || null
};

// Async thunks for authentication actions
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      // Call the authentication API service
      const response = await authService.login(credentials.email, credentials.password);
      
      // Store token in localStorage if remember me is checked
      if (credentials.rememberMe && response.token) {
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user || { email: credentials.email }));
      }
      
      // Return user data and token
      return { 
        user: response.user || { email: credentials.email }, 
        token: response.token 
      };
    } catch (error) {
      return rejectWithValue(error.message || 'An error occurred during login');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    // Call logout API and clear token
    await authService.logout();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return null;
  }
);

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    checkAuth: (state) => {
      // Check if token exists and restore user data
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      if (token && userData) {
        state.isAuthenticated = true;
        state.token = token;
        try {
          state.user = JSON.parse(userData);
        } catch (e) {
          // If user data is corrupted, clear everything
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          state.isAuthenticated = false;
          state.token = null;
          state.user = null;
        }
      } else {
        state.isAuthenticated = false;
        state.token = null;
        state.user = null;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      // Login case handlers
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        // Store in localStorage
        if (action.payload.token) {
          localStorage.setItem('token', action.payload.token);
          localStorage.setItem('user', JSON.stringify(action.payload.user));
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Logout case handlers
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      });
  }
});

// Export actions and reducer
export const { clearError, checkAuth } = authSlice.actions;
export default authSlice.reducer;