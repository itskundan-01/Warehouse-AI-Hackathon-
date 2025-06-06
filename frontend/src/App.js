import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/common/MainLayout';
import Dashboard from './pages/Dashboard';
import ContextualIntelligencePage from './pages/ContextualIntelligence';
import GunnyCounterPage from './pages/GunnyCounter';
import VehicleRecognitionPage from './pages/VehicleRecognition';
import FacialRecognitionPage from './pages/FacialRecognition';
import AdminPanelPage from './pages/AdminPanel';
import LoginPage from './pages/auth/Login';
import AuthLayout from './components/common/AuthLayout';
import AuthInitializer from './components/common/AuthInitializer';
import ProtectedRoute from './components/common/ProtectedRoute';

// Video Upload Pages
import GunnyCounterVideoPage from './pages/GunnyCounter/VideoUpload';
import VehicleRecognitionVideoPage from './pages/VehicleRecognition/VideoUpload';
import FacialRecognitionVideoPage from './pages/FacialRecognition/VideoUpload';
import ContextualIntelligenceVideoPage from './pages/ContextualIntelligence/VideoUpload';

function App() {
  return (
    <AuthInitializer>
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
          <Route path="gunny-counter/video" element={<GunnyCounterVideoPage />} />
          <Route path="vehicle-recognition" element={<VehicleRecognitionPage />} />
          <Route path="vehicle-recognition/video" element={<VehicleRecognitionVideoPage />} />
          <Route path="facial-recognition" element={<FacialRecognitionPage />} />
          <Route path="facial-recognition/video" element={<FacialRecognitionVideoPage />} />
          <Route path="contextual-intelligence" element={<ContextualIntelligencePage />} />
          <Route path="contextual-intelligence/video" element={<ContextualIntelligenceVideoPage />} />
          <Route path="admin" element={<AdminPanelPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </AuthInitializer>
  );
}

export default App;