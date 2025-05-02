import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../services/api/authService';

/**
 * Auth Slice for Redux
 *
 * Handles authentication-related state and actions.
 */

// Initial state
const initialState = {
  isAuthenticated: false,
  user: null,
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
      // Simple token existence check - in a real app, would verify token validity
      state.isAuthenticated = !!state.token;
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