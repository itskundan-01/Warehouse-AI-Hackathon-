import React, { useRef, useEffect, useState } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import CloseIcon from '@mui/icons-material/Close';

/**
 * Face Capture Controls Component
 * Provides camera interface for capturing face images
 */
const FaceCaptureControls = ({ onCapture, onCancel }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Start camera stream when component mounts
    const startCamera = async () => {
      setIsLoading(true);
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: 'user' }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          setStream(mediaStream);
          setError(null);
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
        setError('Could not access camera. Please ensure you have granted camera permissions.');
      } finally {
        setIsLoading(false);
      }
    };

    startCamera();

    // Clean up function to stop camera when component unmounts
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleCapture = () => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current video frame to canvas
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64 image
    const imageData = canvas.toDataURL('image/jpeg');
    
    // Send image back to parent component
    onCapture(imageData);
    
    // Stop camera stream
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  return (
    <Box sx={{ width: '100%', textAlign: 'center' }}>
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box sx={{ p: 2, color: 'error.main' }}>
          {error}
        </Box>
      ) : (
        <>
          <Box sx={{ position: 'relative', mb: 2 }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{ width: '100%', maxHeight: '300px', borderRadius: '8px' }}
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<CloseIcon />}
              onClick={onCancel}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PhotoCameraIcon />}
              onClick={handleCapture}
            >
              Capture
            </Button>
          </Box>
        </>
      )}
    </Box>
  );
};

export default FaceCaptureControls;