import FacialDashboard from './FacialDashboard';

// Import and re-export all components
export { default as FaceCapture } from './FaceCapture';
export { default as FaceRecognition } from './FaceRecognition';
export { default as FaceRegistration } from './FaceRegistration';
export { default as UserAuth } from './UserAuth';

// Export the main dashboard as default
export default FacialDashboard;