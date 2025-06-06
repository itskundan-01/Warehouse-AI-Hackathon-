import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { checkAuth } from '../../store/slices/authSlice';

/**
 * AuthInitializer component to restore authentication state on app startup
 */
const AuthInitializer = ({ children }) => {
  const dispatch = useDispatch();

  useEffect(() => {
    // Check for stored token and restore auth state
    dispatch(checkAuth());
  }, [dispatch]);

  return children;
};

export default AuthInitializer;
