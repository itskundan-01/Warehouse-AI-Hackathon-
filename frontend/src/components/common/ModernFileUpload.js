import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  IconButton,
  Fade,
  Zoom,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  Image as ImageIcon,
  VideoFile as VideoIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';

/**
 * Enhanced File Upload Component with modern styling
 */
const ModernFileUpload = ({
  onFileSelect,
  accept = "image/*",
  maxSize = 10 * 1024 * 1024, // 10MB default
  title = "Upload File",
  description = "Drag and drop a file here, or click to select",
  loading = false,
  error = null,
  preview = null,
  disabled = false,
  className = "",
  sx = {},
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  // Handle file selection
  const handleFileSelect = (file) => {
    if (!file) return;

    // Validate file size
    if (file.size > maxSize) {
      onFileSelect(null, `File size must be less than ${Math.round(maxSize / 1024 / 1024)}MB`);
      return;
    }

    // Validate file type
    if (accept && !accept.includes(file.type) && !accept.includes(file.name.split('.').pop())) {
      onFileSelect(null, "File type not supported");
      return;
    }

    onFileSelect(file, null);
  };

  // Handle drag events
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // Handle click to select file
  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Handle file input change
  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // Get file icon based on type
  const getFileIcon = (fileType) => {
    if (fileType?.startsWith('image/')) return <ImageIcon sx={{ fontSize: 48 }} />;
    if (fileType?.startsWith('video/')) return <VideoIcon sx={{ fontSize: 48 }} />;
    return <FileIcon sx={{ fontSize: 48 }} />;
  };

  return (
    <Box className={className} sx={sx}>
      <Box
        className={`upload-area ${dragOver ? 'dragover' : ''} ${disabled ? 'disabled' : ''}`}
        sx={{
          border: '2px dashed',
          borderColor: dragOver ? 'primary.main' : 'grey.300',
          borderRadius: 3,
          p: 4,
          textAlign: 'center',
          cursor: disabled ? 'not-allowed' : 'pointer',
          background: dragOver 
            ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
            : 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s ease',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': !disabled && {
            borderColor: 'primary.main',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
          },
          ...(disabled && {
            opacity: 0.6,
            background: 'rgba(0, 0, 0, 0.05)',
          }),
        }}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
          disabled={disabled}
        />

        {/* Loading overlay */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(255, 255, 255, 0.9)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1,
            }}
          >
            <CircularProgress size={40} sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Processing...
            </Typography>
          </Box>
        )}

        {/* Preview or upload UI */}
        {preview ? (
          <Zoom in={!!preview}>
            <Box>
              {typeof preview === 'string' ? (
                <Box
                  component="img"
                  src={preview}
                  alt="Preview"
                  sx={{
                    maxWidth: '100%',
                    maxHeight: 200,
                    borderRadius: 2,
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                    mb: 2,
                  }}
                />
              ) : (
                <Box sx={{ mb: 2 }}>
                  {getFileIcon(preview.type)}
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {preview.name}
                  </Typography>
                </Box>
              )}
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<DeleteIcon />}
                onClick={(e) => {
                  e.stopPropagation();
                  onFileSelect(null, null);
                }}
                sx={{ mt: 1 }}
              >
                Remove
              </Button>
            </Box>
          </Zoom>
        ) : (
          <Fade in={!preview}>
            <Box>
              <CloudUploadIcon 
                sx={{ 
                  fontSize: 64, 
                  color: 'primary.main', 
                  mb: 2,
                  opacity: dragOver ? 1 : 0.7,
                  transform: dragOver ? 'scale(1.1)' : 'scale(1)',
                  transition: 'all 0.3s ease',
                }} 
              />
              <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                {title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {description}
              </Typography>
              <Button
                variant="contained"
                className="modern-button"
                startIcon={<CloudUploadIcon />}
                disabled={disabled}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                  },
                }}
              >
                Choose File
              </Button>
            </Box>
          </Fade>
        )}
      </Box>

      {/* Error message */}
      {error && (
        <Alert 
          severity="error" 
          className="modern-alert error-shake" 
          sx={{ mt: 2 }}
        >
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ModernFileUpload;
