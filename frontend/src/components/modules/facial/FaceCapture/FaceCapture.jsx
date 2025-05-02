import React, { useState } from 'react';
import { Box, Typography, Button, Paper, CircularProgress } from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import FaceCaptureControls from './FaceCaptureControls';

/**
 * Face Capture Component
 * Allows users to capture faces using a camera or upload images
 */
const FaceCapture = () => {
  const [capturing, setCapturing] = useState(false);
  const [imgSrc, setImgSrc] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleStartCapture = () => {
    setCapturing(true);
  };

  const handleStopCapture = () => {
    setCapturing(false);
  };

  const handleImageCapture = (imageSrc) => {
    setImgSrc(imageSrc);
    setCapturing(false);
  };

  const handleSubmit = async () => {
    if (!imgSrc) return;
    
    setLoading(true);
    // In a real implementation, you would send the image to your API
    setTimeout(() => {
      setLoading(false);
      setImgSrc(null);
      // Show success notification in a real app
    }, 1500);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Face Capture
      </Typography>
      
      <Paper 
        elevation={3} 
        sx={{ 
          p: 3, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          mb: 3
        }}
      >
        {!capturing && !imgSrc ? (
          <Box 
            sx={{ 
              width: '100%', 
              height: 300, 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              border: '1px dashed #ccc',
              borderRadius: 1
            }}
          >
            <Button
              variant="contained"
              color="primary"
              startIcon={<CameraAltIcon />}
              onClick={handleStartCapture}
            >
              Start Camera
            </Button>
          </Box>
        ) : imgSrc ? (
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <img 
              src={imgSrc} 
              alt="Captured face" 
              style={{ 
                maxWidth: '100%', 
                maxHeight: 300,
                borderRadius: 4
              }} 
            />
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="outlined" 
                onClick={() => setImgSrc(null)} 
                sx={{ mr: 1 }}
              >
                Retake
              </Button>
              <Button 
                variant="contained" 
                color="success" 
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Submit'}
              </Button>
            </Box>
          </Box>
        ) : (
          <FaceCaptureControls 
            onCapture={handleImageCapture} 
            onCancel={handleStopCapture} 
          />
        )}
      </Paper>
      
      <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
        Note: For demonstration purposes only. In a production environment, 
        captured face images would be securely processed and verified against 
        the facial recognition database.
      </Typography>
    </Box>
  );
};

export default FaceCapture;