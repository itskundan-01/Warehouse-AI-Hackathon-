import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/common/MainLayout';
import Dashboard from './pages/Dashboard';
import ContextualIntelligencePage from './pages/ContextualIntelligence';
import GunnyCounterPage from './pages/GunnyCounter';
import VehicleRecognitionPage from './pages/VehicleRecognition';
import FacialRecognitionPage from './pages/FacialRecognition';
import LoginPage from './pages/auth/Login';
import AuthLayout from './components/common/AuthLayout';
import ProtectedRoute from './components/common/ProtectedRoute';

function App() {
  return (
    <Routes>
      {/* Auth routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Protected application routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="gunny-counter" element={<GunnyCounterPage />} />
        <Route path="vehicle-recognition" element={<VehicleRecognitionPage />} />
        <Route path="facial-recognition" element={<FacialRecognitionPage />} />
        <Route path="contextual-intelligence" element={<ContextualIntelligencePage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}

export default App;