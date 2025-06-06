import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Card,
  CardContent,
  IconButton,
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  VideoFile as VideoIcon,
  PlayArrow as PlayIcon,
  Delete as DeleteIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';

const VideoUploadComponent = ({ 
  module, 
  onUploadComplete, 
  onAnalysisStart,
  acceptedFormats = ['.mp4', '.avi', '.mov', '.mkv'],
  maxFileSize = 100 * 1024 * 1024 // 100MB
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [location, setLocation] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const locations = [
    'Warehouse-A',
    'Warehouse-B',
    'Loading-Dock-1',
    'Loading-Dock-2',
    'Storage-Area-1',
    'Storage-Area-2',
    'Security-Gate',
    'Parking-Area'
  ];

  const moduleEndpoints = {
    gunny: '/api/v1/gunny/process-video',
    vehicle: '/api/v1/vehicle/process-video', 
    facial: '/api/v1/facial/process-video',
    contextual: '/api/v1/contextual/process-video'
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!acceptedFormats.includes(fileExtension)) {
      setError(`Unsupported file format. Please upload: ${acceptedFormats.join(', ')}`);
      return;
    }

    // Validate file size
    if (file.size > maxFileSize) {
      setError(`File too large. Maximum size: ${Math.round(maxFileSize / (1024 * 1024))}MB`);
      return;
    }

    setSelectedFile(file);
    setError('');
    setSuccess('');
    setAnalysisResults(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const event = { target: { files } };
      handleFileSelect(event);
    }
  };

  const uploadVideo = async () => {
    if (!selectedFile || !location) {
      setError('Please select a video file and location');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError('');

    try {
      const formData = new FormData();
      formData.append('video', selectedFile);
      formData.append('location', location);

      const endpoint = moduleEndpoints[module];
      if (!endpoint) {
        throw new Error('Invalid module specified');
      }

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 10;
        });
      }, 200);

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (result.success) {
        setSuccess(`Video uploaded successfully! Processing ID: ${result.processing_id}`);
        setAnalysisResults(result);
        
        if (onUploadComplete) {
          onUploadComplete(result);
        }
        
        if (onAnalysisStart) {
          onAnalysisStart(result.processing_id);
        }
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setError('');
    setSuccess('');
    setAnalysisResults(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getModuleTitle = () => {
    const titles = {
      gunny: 'Gunny Bag Counter',
      vehicle: 'Vehicle Recognition',
      facial: 'Facial Recognition',
      contextual: 'Contextual Intelligence'
    };
    return titles[module] || 'Video Analysis';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AnalyticsIcon color="primary" />
          {getModuleTitle()} - Video Upload
        </Typography>
        
        <Divider sx={{ mb: 3 }} />

        {/* Location Selection */}
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Select Location</InputLabel>
          <Select
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            label="Select Location"
          >
            {locations.map((loc) => (
              <MenuItem key={loc} value={loc}>
                {loc}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* File Upload Area */}
        <Box
          sx={{
            border: '2px dashed',
            borderColor: selectedFile ? 'success.main' : 'grey.300',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            bgcolor: selectedFile ? 'success.50' : 'grey.50',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'primary.50'
            }
          }}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedFormats.join(',')}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          
          {selectedFile ? (
            <Box>
              <VideoIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {selectedFile.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Size: {formatFileSize(selectedFile.size)}
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
                <Chip 
                  label="Video Selected" 
                  color="success" 
                  variant="outlined"
                />
                <IconButton onClick={(e) => { e.stopPropagation(); clearSelection(); }}>
                  <DeleteIcon />
                </IconButton>
              </Box>
            </Box>
          ) : (
            <Box>
              <UploadIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Click to upload or drag & drop
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Supported formats: {acceptedFormats.join(', ')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Maximum size: {Math.round(maxFileSize / (1024 * 1024))}MB
              </Typography>
            </Box>
          )}
        </Box>

        {/* Error/Success Messages */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mt: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Upload Progress */}
        {uploading && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Uploading... {Math.round(uploadProgress)}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        )}

        {/* Upload Button */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            onClick={uploadVideo}
            disabled={!selectedFile || !location || uploading}
            startIcon={<PlayIcon />}
            size="large"
          >
            {uploading ? 'Processing...' : 'Start Analysis'}
          </Button>
          
          {selectedFile && (
            <Button
              variant="outlined"
              onClick={clearSelection}
              disabled={uploading}
              startIcon={<DeleteIcon />}
            >
              Clear
            </Button>
          )}
        </Box>

        {/* Analysis Results */}
        {analysisResults && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis Started
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Processing ID:
                  </Typography>
                  <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                    {analysisResults.processing_id}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Location:
                  </Typography>
                  <Typography variant="body1">
                    {analysisResults.location}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Status:
                  </Typography>
                  <Chip 
                    label="Processing" 
                    color="info" 
                    variant="outlined"
                    size="small"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Video Preview (if supported) */}
        {selectedFile && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Video Preview
            </Typography>
            <video
              ref={videoRef}
              controls
              style={{ width: '100%', maxHeight: '400px', borderRadius: '8px' }}
              src={URL.createObjectURL(selectedFile)}
            />
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default VideoUploadComponent;
