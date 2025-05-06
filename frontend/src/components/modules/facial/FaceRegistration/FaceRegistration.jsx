import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Alert
} from '@mui/material';
import RegistrationForm from './RegistrationForm';
import FaceCapture from '../FaceCapture/FaceCapture';
import facialService from '../../../../services/api/facialService';

/**
 * Face Registration Component for adding new personnel to the system
 */
const FaceRegistration = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleImageCapture = (imageData) => {
    // Extract base64 data (remove prefix like "data:image/jpeg;base64,")
    const base64Data = imageData.split(',')[1];
    setCapturedImage(base64Data);
    setError('');
    setSuccess(false);
  };

  const handleRegister = async (formData) => {
    if (!capturedImage) {
      setError('Please capture a face image first');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Prepare data for API call
      const registrationData = {
        employee_id: formData.employeeId,
        name: formData.name,
        department: formData.department,
        access_level: parseInt(formData.accessLevel, 10),
        face_image_base64: capturedImage
      };
      
      // Call the API service
      await facialService.registerPersonnel(registrationData);
      
      // Handle success
      setSuccess(true);
      setCapturedImage(null);
      
    } catch (err) {
      setError(`Registration failed: ${err.message || 'Unknown error'}`);
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCaptureComplete = (base64Image) => {
    // Extract base64 data without the prefix
    const base64Data = base64Image.split(',')[1];
    setCapturedImage(base64Data);
    setError('');
    setSuccess(false);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Personnel Registration
      </Typography>
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Registration successful! Personnel has been added to the system.
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: '100%'
            }}
          >
            <Typography variant="subtitle1" gutterBottom>
              Capture Face Image
            </Typography>
            
            <Box sx={{ width: '100%', mb: 2 }}>
              {/* Use the FaceCapture component with a callback */}
              <FaceCapture 
                onImageCapture={handleCaptureComplete}
                showPreview={true}
                inlineDisplay={true}
              />
            </Box>
            
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2, textAlign: 'center' }}>
              Ensure the face is well-lit and directly facing the camera for best recognition results.
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <RegistrationForm 
            onSubmit={handleRegister} 
            loading={loading} 
            disabled={!capturedImage || loading}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default FaceRegistration;