import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import FaceCapture from '../FaceCapture/FaceCapture';
import facialService from '../../../../services/api/facialService';

/**
 * Face Verification Component
 * Allows users to verify their identity using facial recognition
 */
const FaceVerification = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleCaptureComplete = (base64Image) => {
    // Extract base64 data without the prefix
    const base64Data = base64Image.split(',')[1];
    setCapturedImage(base64Data);
    setError('');
    setResult(null);
  };

  const handleVerify = async () => {
    if (!capturedImage) {
      setError('Please capture a face image first');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Prepare data for authentication API call
      const authData = {
        face_image_base64: capturedImage,
        location: 'Verification Station', // This could be dynamic based on location
        camera_id: 'web-client-cam'       // This could be dynamic based on device
      };
      
      // Call the API service
      const response = await facialService.authenticateFace(authData);
      setResult(response);
    } catch (err) {
      setError(`Verification failed: ${err.message || 'Unknown error'}`);
      console.error('Verification error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCapturedImage(null);
    setResult(null);
    setError('');
  };

  const renderVerificationResult = () => {
    if (!result) return null;

    const isAuthenticated = result.authenticated;
    
    return (
      <Card 
        sx={{ 
          mt: 3, 
          bgcolor: isAuthenticated ? 'success.light' : 'error.light',
          color: 'white'
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {isAuthenticated ? 
              <CheckCircleOutlineIcon sx={{ fontSize: 40, mr: 2 }} /> : 
              <CancelOutlinedIcon sx={{ fontSize: 40, mr: 2 }} />
            }
            <Typography variant="h6">
              {isAuthenticated ? 'Authentication Successful' : 'Authentication Failed'}
            </Typography>
          </Box>
          
          {isAuthenticated ? (
            <Box>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Name:</strong> {result.name}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>ID:</strong> {result.personnel_id}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Access Level:</strong> {result.access_level}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
              </Typography>
            </Box>
          ) : (
            <Typography variant="body1">
              {result.message || 'No matching identity found'}
            </Typography>
          )}
          
          <Button 
            variant="contained" 
            sx={{ mt: 2, bgcolor: 'white', color: 'text.primary' }}
            onClick={handleReset}
          >
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Face Verification
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={result ? 6 : 12}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <Typography variant="subtitle1" gutterBottom>
              Verify Your Identity
            </Typography>
            
            {!capturedImage ? (
              <Box sx={{ width: '100%', mb: 2 }}>
                <FaceCapture 
                  onImageCapture={handleCaptureComplete}
                  showPreview={true}
                  inlineDisplay={true}
                />
              </Box>
            ) : loading ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="body1">Verifying identity...</Typography>
              </Box>
            ) : !result ? (
              <Box sx={{ width: '100%', textAlign: 'center' }}>
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
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <img 
                  src={`data:image/jpeg;base64,${capturedImage}`} 
                  alt="Captured face" 
                  style={{ 
                    maxWidth: '100%', 
                    maxHeight: 200,
                    borderRadius: 4
                  }} 
                />
              </Box>
            )}
            
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2, textAlign: 'center' }}>
              Look directly at the camera with neutral expression for best results.
            </Typography>
          </Paper>
        </Grid>
        
        {result && (
          <Grid item xs={12} md={6}>
            {renderVerificationResult()}
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default FaceVerification;