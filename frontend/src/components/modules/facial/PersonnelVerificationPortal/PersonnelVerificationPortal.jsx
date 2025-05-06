import React, { useState } from 'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import FaceCapture from '../FaceCapture/FaceCapture';
import RegistrationForm from '../FaceRegistration/RegistrationForm';
import facialService from '../../../../services/api/facialService';

/**
 * Personnel Verification Portal
 * A complete workflow for verifying if a person is registered,
 * and registering them if they are not.
 */
const PersonnelVerificationPortal = () => {
  // State management
  const [activeStep, setActiveStep] = useState(0);
  const [capturedImage, setCapturedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [registrationResult, setRegistrationResult] = useState(null);
  const [error, setError] = useState('');

  // Steps in the verification/registration process
  const steps = ['Capture Face', 'Verify Identity', 'Registration (if needed)'];

  /**
   * Handle image capture from FaceCapture component
   */
  const handleCaptureComplete = (base64Image) => {
    // Extract base64 data without the prefix
    const base64Data = base64Image.split(',')[1];
    setCapturedImage(base64Data);
    setError('');
    setActiveStep(1); // Move to verification step
  };

  /**
   * Verify if person is registered in the system
   */
  const handleVerify = async () => {
    if (!capturedImage) {
      setError('Please capture a face image first');
      setActiveStep(0); // Go back to capture step
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Prepare data for authentication API call
      const authData = {
        face_image_base64: capturedImage,
        location: 'Verification Portal',
        camera_id: 'web-client-cam'
      };
      
      // Call the API service
      const response = await facialService.authenticateFace(authData);
      setVerificationResult(response);
      
      // If not authenticated, move to registration step
      if (!response.authenticated) {
        setActiveStep(2);
      }
    } catch (err) {
      setError(`Verification failed: ${err.message || 'Unknown error'}`);
      console.error('Verification error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle registration of new personnel
   */
  const handleRegister = async (formData) => {
    if (!capturedImage) {
      setError('Please capture a face image first');
      setActiveStep(0);
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Prepare data for registration API call
      const registrationData = {
        employee_id: formData.employeeId,
        name: formData.name,
        department: formData.department,
        access_level: parseInt(formData.accessLevel, 10),
        face_image_base64: capturedImage
      };
      
      // Call the API service
      const response = await facialService.registerPersonnel(registrationData);
      setRegistrationResult(response);
      
      // Verify the newly registered person
      await handleVerify();
    } catch (err) {
      setError(`Registration failed: ${err.message || 'Unknown error'}`);
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset the entire process
   */
  const handleReset = () => {
    setCapturedImage(null);
    setVerificationResult(null);
    setRegistrationResult(null);
    setError('');
    setActiveStep(0);
  };

  /**
   * Render the verification result card
   */
  const renderVerificationResult = () => {
    if (!verificationResult) return null;

    const isAuthenticated = verificationResult.authenticated;
    
    return (
      <Card 
        sx={{ 
          mt: 3, 
          bgcolor: isAuthenticated ? 'success.light' : 'error.light',
          color: 'white'
        }}
      >
        <CardContent>
          {isAuthenticated ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Authentication Successful
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Name:</strong> {verificationResult.name}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>ID:</strong> {verificationResult.personnel_id}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Access Level:</strong> {verificationResult.access_level}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Confidence:</strong> {(verificationResult.confidence * 100).toFixed(1)}%
              </Typography>
            </Box>
          ) : (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Authentication Failed
              </Typography>
              <Typography variant="body1">
                {verificationResult.message || 'No matching identity found'}
              </Typography>
              <Typography variant="body2" sx={{ mt: 2 }}>
                If you are a new employee, please complete the registration form.
              </Typography>
            </Box>
          )}
          
          <Button 
            variant="contained" 
            sx={{ mt: 2, bgcolor: 'white', color: 'text.primary' }}
            onClick={handleReset}
          >
            Start Over
          </Button>
        </CardContent>
      </Card>
    );
  };

  /**
   * Render the appropriate step content
   */
  const getStepContent = (step) => {
    switch (step) {
      case 0: // Face Capture
        return (
          <Box sx={{ width: '100%', mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom align="center">
              Please look at the camera and capture a clear image of your face
            </Typography>
            <FaceCapture 
              onImageCapture={handleCaptureComplete}
              showPreview={true}
              inlineDisplay={true}
            />
          </Box>
        );
      case 1: // Verification
        return (
          <Box sx={{ width: '100%', textAlign: 'center', py: 2 }}>
            {loading ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="body1">Verifying identity...</Typography>
              </Box>
            ) : (
              <>
                <img 
                  src={`data:image/jpeg;base64,${capturedImage}`} 
                  alt="Captured face" 
                  style={{ 
                    maxWidth: '100%', 
                    maxHeight: 300,
                    borderRadius: 4,
                    marginBottom: 16
                  }} 
                />
                <Box sx={{ mt: 2 }}>
                  <Button 
                    variant="outlined" 
                    onClick={handleReset} 
                    sx={{ mr: 1 }}
                  >
                    Retake
                  </Button>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={handleVerify}
                  >
                    Verify Identity
                  </Button>
                </Box>
                {verificationResult && renderVerificationResult()}
              </>
            )}
          </Box>
        );
      case 2: // Registration
        return (
          <Box sx={{ width: '100%', py: 2 }}>
            <Typography variant="subtitle1" gutterBottom align="center">
              Person not recognized. Please complete the registration form.
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <img 
                src={`data:image/jpeg;base64,${capturedImage}`} 
                alt="Captured face" 
                style={{ 
                  maxWidth: '200px',
                  borderRadius: 4
                }} 
              />
            </Box>
            
            <Divider sx={{ mb: 3 }} />
            
            <RegistrationForm 
              onSubmit={handleRegister} 
              loading={loading} 
              disabled={loading}
            />
            
            {registrationResult && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Registration successful! Verifying your identity...
              </Alert>
            )}
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Personnel Verification Portal
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => {
          return (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          );
        })}
      </Stepper>
      
      <Paper elevation={3} sx={{ p: 3 }}>
        {getStepContent(activeStep)}
      </Paper>
    </Box>
  );
};

export default PersonnelVerificationPortal;