import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Dialog,
  DialogContent,
  DialogTitle,
  DialogActions,
  Tooltip,
  LinearProgress,
  Badge,
  Avatar,
  Divider,
  Paper
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  DirectionsCar as CarIcon,
  TextFields as PlateIcon,
  Speed as SpeedIcon,
  Timer as TimerIcon
} from '@mui/icons-material';

import ModernFileUpload from '../common/ModernFileUpload';
import plateDetectionService from '../../services/api/plateDetectionService';

/**
 * Comprehensive Plate Detection Component
 * Handles file upload, processing, and results display
 */
const PlateDetection = () => {
  // State management
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // History and statistics
  const [history, setHistory] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Dialog states
  const [previewDialog, setPreviewDialog] = useState(false);
  const [historyDialog, setHistoryDialog] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);

  // Load initial data
  useEffect(() => {
    loadStatistics();
    loadHistory();
  }, []);

  // Load statistics
  const loadStatistics = async () => {
    try {
      const stats = await plateDetectionService.getStatistics();
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };

  // Load detection history
  const loadHistory = async () => {
    try {
      const historyData = await plateDetectionService.getHistory();
      setHistory(historyData);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  // Handle file selection
  const handleFileSelect = (file, fileError) => {
    if (fileError) {
      setError(fileError);
      return;
    }

    setSelectedFile(file);
    setError(null);
    setDetectionResult(null);

    // Create preview for image/video
    if (file) {
      const fileReader = new FileReader();
      fileReader.onload = () => {
        setPreviewUrl(fileReader.result);
      };
      fileReader.readAsDataURL(file);
    } else {
      setPreviewUrl(null);
    }
  };

  // Handle detection processing
  const handleDetect = async () => {
    if (!selectedFile) {
      setError('Please select a file to process');
      return;
    }

    setProcessing(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const result = await plateDetectionService.detectPlates(selectedFile);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setDetectionResult(result);
      
      // Refresh statistics and history
      await loadStatistics();
      await loadHistory();
      
    } catch (err) {
      setError(err.message || 'Failed to process plate detection');
    } finally {
      setProcessing(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  // Handle file reset
  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setDetectionResult(null);
    setError(null);
    setUploadProgress(0);
  };

  // Format confidence percentage
  const formatConfidence = (confidence) => {
    return `${Math.round(confidence * 100)}%`;
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format processing time
  const formatProcessingTime = (seconds) => {
    return `${seconds.toFixed(2)}s`;
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Vehicle Plate Detection
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload images or videos to detect and extract vehicle license plates using AI
        </Typography>
      </Box>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                    <CloudUploadIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6">{statistics.total_detections}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Detections
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                    <CheckCircleIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6">{statistics.successful_detections}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Successful
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                    <SpeedIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6">
                      {formatProcessingTime(statistics.average_processing_time)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Time
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                    <PlateIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6">{statistics.unique_plates}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Unique Plates
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Grid container spacing={3}>
        {/* File Upload Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload File
              </Typography>
              
              <ModernFileUpload
                onFileSelect={handleFileSelect}
                accept="image/*,video/*"
                maxSize={50 * 1024 * 1024} // 50MB
                title="Select Image or Video"
                description="Drag and drop an image or video file, or click to browse"
                loading={processing}
                error={error}
                preview={previewUrl}
              />
              
              {uploadProgress > 0 && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                  <Typography variant="caption" color="text.secondary">
                    Processing: {uploadProgress}%
                  </Typography>
                </Box>
              )}
              
              {selectedFile && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button
                      variant="contained"
                      onClick={handleDetect}
                      disabled={processing}
                      startIcon={processing ? <CircularProgress size={20} /> : <AnalyticsIcon />}
                    >
                      {processing ? 'Processing...' : 'Detect Plates'}
                    </Button>
                    
                    <Button
                      variant="outlined"
                      onClick={handleReset}
                      disabled={processing}
                    >
                      Reset
                    </Button>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detection Results
              </Typography>
              
              {detectionResult ? (
                <Box>
                  {/* File Information */}
                  <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      File Information
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Type: {detectionResult.file_type}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Size: {formatFileSize(detectionResult.file_size)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="caption" color="text.secondary">
                          Processing Time: {formatProcessingTime(detectionResult.processing_time)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>

                  {/* Detection Results */}
                  {detectionResult.vehicles && detectionResult.vehicles.length > 0 ? (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Detected Vehicles & Plates
                      </Typography>
                      
                      {detectionResult.vehicles.map((vehicle, index) => (
                        <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid', borderColor: 'divider' }}>
                          <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                            <Chip
                              icon={<CarIcon />}
                              label={`Vehicle ${index + 1}`}
                              color="primary"
                              size="small"
                            />
                            <Chip
                              label={formatConfidence(vehicle.confidence)}
                              color={getConfidenceColor(vehicle.confidence)}
                              size="small"
                            />
                          </Box>
                          
                          {vehicle.plates && vehicle.plates.length > 0 ? (
                            vehicle.plates.map((plate, plateIndex) => (
                              <Box key={plateIndex} sx={{ mt: 1 }}>
                                <Box display="flex" alignItems="center" justifyContent="space-between">
                                  <Typography variant="h6" component="span">
                                    {plate.text || 'No text detected'}
                                  </Typography>
                                  <Chip
                                    label={formatConfidence(plate.confidence)}
                                    color={getConfidenceColor(plate.confidence)}
                                    size="small"
                                  />
                                </Box>
                                <Typography variant="caption" color="text.secondary">
                                  Plate Detection Confidence: {formatConfidence(plate.detection_confidence)}
                                </Typography>
                              </Box>
                            ))
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              No license plates detected
                            </Typography>
                          )}
                        </Paper>
                      ))}
                    </Box>
                  ) : (
                    <Alert severity="info">
                      No vehicles detected in the uploaded file
                    </Alert>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Upload a file and click "Detect Plates" to see results
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<HistoryIcon />}
          onClick={() => setHistoryDialog(true)}
        >
          View History
        </Button>
        
        {detectionResult && (
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => {
              const dataStr = JSON.stringify(detectionResult, null, 2);
              const dataBlob = new Blob([dataStr], { type: 'application/json' });
              const url = URL.createObjectURL(dataBlob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `plate_detection_${Date.now()}.json`;
              link.click();
            }}
          >
            Download Results
          </Button>
        )}
      </Box>

      {/* History Dialog */}
      <Dialog
        open={historyDialog}
        onClose={() => setHistoryDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Detection History
          <IconButton
            onClick={() => setHistoryDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>File Type</TableCell>
                  <TableCell>Vehicles</TableCell>
                  <TableCell>Plates Found</TableCell>
                  <TableCell>Processing Time</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {history
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((record) => (
                    <TableRow key={record._id}>
                      <TableCell>
                        {new Date(record.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Chip label={record.file_type} size="small" />
                      </TableCell>
                      <TableCell>{record.vehicles?.length || 0}</TableCell>
                      <TableCell>
                        {record.vehicles?.reduce((total, vehicle) => 
                          total + (vehicle.plates?.length || 0), 0) || 0}
                      </TableCell>
                      <TableCell>
                        {formatProcessingTime(record.processing_time)}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedRecord(record);
                              setPreviewDialog(true);
                            }}
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            component="div"
            count={history.length}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </DialogContent>
      </Dialog>

      {/* Record Preview Dialog */}
      <Dialog
        open={previewDialog}
        onClose={() => setPreviewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Detection Details
          <IconButton
            onClick={() => setPreviewDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedRecord && (
            <Box>
              <Typography variant="h6" gutterBottom>
                File: {selectedRecord.filename}
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Type:</strong> {selectedRecord.file_type}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Size:</strong> {formatFileSize(selectedRecord.file_size)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Date:</strong> {new Date(selectedRecord.created_at).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Processing:</strong> {formatProcessingTime(selectedRecord.processing_time)}
                  </Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {selectedRecord.vehicles && selectedRecord.vehicles.length > 0 ? (
                selectedRecord.vehicles.map((vehicle, index) => (
                  <Paper key={index} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Vehicle {index + 1} (Confidence: {formatConfidence(vehicle.confidence)})
                    </Typography>
                    
                    {vehicle.plates?.map((plate, plateIndex) => (
                      <Box key={plateIndex} sx={{ ml: 2, mt: 1 }}>
                        <Typography variant="body1">
                          <strong>Plate Text:</strong> {plate.text || 'Not detected'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          OCR Confidence: {formatConfidence(plate.confidence)} | 
                          Detection Confidence: {formatConfidence(plate.detection_confidence)}
                        </Typography>
                      </Box>
                    ))}
                  </Paper>
                ))
              ) : (
                <Alert severity="info">No vehicles detected in this file</Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PlateDetection;
