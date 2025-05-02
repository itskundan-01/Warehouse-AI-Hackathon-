// Main pages export file
// This file centralizes exports from all page components for easier imports

export { default as DashboardPage } from './Dashboard';
export { default as GunnyCounterPage } from './GunnyCounter';
export { default as VehicleRecognitionPage } from './VehicleRecognition';
export { default as FacialRecognitionPage } from './FacialRecognition';
export { default as ContextualIntelligencePage } from './ContextualIntelligence';
export { default as AuthPage } from './Auth';

// Export nested page components
export { default as LoginPage } from './Auth/Login';
export { default as RegisterPage } from './Auth/Register';
export { default as ForgotPasswordPage } from './Auth/ForgotPassword';