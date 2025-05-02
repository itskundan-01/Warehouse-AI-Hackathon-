import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Card,
  CardMedia
} from '@mui/material';
import AddAPhotoIcon from '@mui/icons-material/AddAPhoto';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import RegistrationForm from './RegistrationForm';

/**
 * Face Registration Component for adding new personnel to the system
 */
const FaceRegistration = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleImageSelect = (imageData) => {
    setSelectedImage(imageData);
    setError('');
    setSuccess(false);
  };

  const handleRegister = async (formData) => {
    if (!selectedImage) {
      setError('Please capture or upload a face image first');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Simulate API call - in real app this would send data to the backend
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Simulate success
      setSuccess(true);
      setSelectedImage(null);
      
    } catch (err) {
      setError('Registration failed. Please try again.');
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setSelectedImage(null);
    setSuccess(false);
    setError('');
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
              Face Image
            </Typography>
            
            {selectedImage ? (
              <>
                <Card sx={{ width: '100%', mb: 2 }}>
                  <CardMedia
                    component="img"
                    image={selectedImage}
                    alt="Selected face"
                    sx={{ 
                      maxHeight: 300, 
                      objectFit: 'contain' 
                    }}
                  />
                </Card>
                <Button 
                  variant="outlined" 
                  onClick={handleCancel}
                  sx={{ mt: 1 }}
                >
                  Change Image
                </Button>
              </>
            ) : (
              <Box
                sx={{
                  width: '100%',
                  height: 250,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  border: '1px dashed #ccc',
                  borderRadius: 1
                }}
              >
                <AddAPhotoIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Button 
                  variant="contained"
                  onClick={() => handleImageSelect('https://i.pravatar.cc/300')} // For demo, use a placeholder image
                >
                  Capture Face Image
                </Button>
              </Box>
            )}
            
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2, textAlign: 'center' }}>
              Ensure the face is well-lit and directly facing the camera for best recognition results.
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <RegistrationForm 
            onSubmit={handleRegister} 
            loading={loading} 
            disabled={!selectedImage || loading}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default FaceRegistration;