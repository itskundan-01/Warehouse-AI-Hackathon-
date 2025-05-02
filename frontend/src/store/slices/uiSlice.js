import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  sidebarOpen: true,
  notifications: [],
  currentTheme: 'light',
  alerts: [],
  apiError: null,
  loading: {
    global: false,
    dashboard: false,
    facial: false,
    gunny: false,
    vehicle: false,
    context: false,
  }
};

export const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action) => {
      state.sidebarOpen = action.payload;
    },
    addNotification: (state, action) => {
      state.notifications.push(action.payload);
    },
    clearNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    setTheme: (state, action) => {
      state.currentTheme = action.payload;
    },
    addAlert: (state, action) => {
      state.alerts.push({
        id: new Date().getTime(),
        ...action.payload,
      });
    },
    removeAlert: (state, action) => {
      state.alerts = state.alerts.filter((alert) => alert.id !== action.payload);
    },
    setApiError: (state, action) => {
      state.apiError = action.payload;
      
      // Also add as an alert for visibility
      state.alerts.push({
        id: new Date().getTime(),
        type: 'error',
        message: action.payload.message,
        autoHide: false
      });
    },
    clearApiError: (state) => {
      state.apiError = null;
    },
    setLoading: (state, action) => {
      const { module, isLoading } = action.payload;
      if (state.loading.hasOwnProperty(module)) {
        state.loading[module] = isLoading;
      }
    }
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  addNotification,
  clearNotification,
  setTheme,
  addAlert,
  removeAlert,
  setLoading,
  setApiError,
  clearApiError
} = uiSlice.actions;

export default uiSlice.reducer;