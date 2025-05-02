// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import uiReducer from './slices/uiSlice';
import contextReducer from './slices/contextSlice';
import facialReducer from './slices/facialSlice';
import gunnyReducer from './slices/gunnySlice';
import vehicleReducer from './slices/vehicleSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    ui: uiReducer,
    context: contextReducer,
    facial: facialReducer,
    gunny: gunnyReducer,
    vehicle: vehicleReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export default store;