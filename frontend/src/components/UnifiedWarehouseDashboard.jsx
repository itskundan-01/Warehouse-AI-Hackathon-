import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  Chip,
  LinearProgress,
  Alert,
  Badge,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  VideoCall as VideoIcon,
  StopCircle as StopIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  DirectionsCar as CarIcon,
  Inventory as InventoryIcon,
  Psychology as BrainIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  CloudUpload as UploadIcon,
  Visibility as ViewIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { unifiedWarehouseService } from '../services/api/unifiedWarehouseService';

const UnifiedWarehouseDashboard = () => {
  // State management
  const [isConnected, setIsConnected] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [recentDetections, setRecentDetections] = useState([]);
  const [realTimeDetection, setRealTimeDetection] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingResults, setProcessingResults] = useState(null);
  const [showResultsDialog, setShowResultsDialog] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);

  // Refs
  const fileInputRef = useRef(null);
  const resultImageRef = useRef(null);

  // Module statistics
  const [moduleStats, setModuleStats] = useState({
    face: { detections: 0, lastUpdate: null },
    plate: { detections: 0, lastUpdate: null },
    gunny: { detections: 0, lastUpdate: null },
    contextual: { detections: 0, lastUpdate: null }
  });

  // Initialize service
  useEffect(() => {
    const initializeService = async () => {
      try {
        unifiedWarehouseService.initialize();
        
        // Subscribe to events
        unifiedWarehouseService.subscribe('connected', () => {
          setIsConnected(true);
          loadSystemStatus();
          loadRecentDetections();
        });

        unifiedWarehouseService.subscribe('detection', handleNewDetection);
        unifiedWarehouseService.subscribe('error', handleError);

        // Load initial data
        await loadSystemStatus();
        await loadRecentDetections();
      } catch (error) {
        console.error('Service initialization failed:', error);
      }
    };

    initializeService();

    return () => {
      unifiedWarehouseService.disconnect();
    };
  }, []);

  // Handle new real-time detection
  const handleNewDetection = useCallback((detection) => {
    setRealTimeDetection(detection);
    
    // Update recent detections
    setRecentDetections(prev => [detection, ...prev.slice(0, 19)]);
    
    // Update module statistics
    setModuleStats(prev => ({
      ...prev,
      [detection.module]: {
        detections: prev[detection.module].detections + 1,
        lastUpdate: new Date().toISOString()
      }
    }));

    // Auto-hide real-time detection after 5 seconds
    setTimeout(() => {
      setRealTimeDetection(null);
    }, 5000);
  }, []);

  // Handle errors
  const handleError = useCallback((error) => {
    console.error('Unified service error:', error);
  }, []);

  // Load system status
  const loadSystemStatus = async () => {
    try {
      const status = await unifiedWarehouseService.getSystemStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  // Load recent detections
  const loadRecentDetections = async () => {
    try {
      const response = await unifiedWarehouseService.getRecentDetections();
      setRecentDetections(response.detections || []);
    } catch (error) {
      console.error('Failed to load recent detections:', error);
    }
  };

  // Handle file upload
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // Process uploaded file
  const processFile = async (modules = ['face', 'plate', 'gunny', 'contextual']) => {
    if (!selectedFile) return;

    setIsProcessing(true);
    try {
      const result = await unifiedWarehouseService.processFile(
        selectedFile,
        modules,
        'default'
      );
      
      setProcessingResults(result);
      setShowResultsDialog(true);
    } catch (error) {
      console.error('File processing failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Start/stop camera
  const toggleCamera = () => {
    if (cameraActive) {
      unifiedWarehouseService.stopCameraStream();
      setCameraActive(false);
    } else {
      unifiedWarehouseService.startCameraStream();
      setCameraActive(true);
    }
  };

  // Module icons
  const getModuleIcon = (module) => {
    switch (module) {
      case 'face': return <PersonIcon />;
      case 'plate': return <CarIcon />;
      case 'gunny': return <InventoryIcon />;
      case 'contextual': return <BrainIcon />;
      default: return <SecurityIcon />;
    }
  };

  // Module colors
  const getModuleColor = (module) => {
    switch (module) {
      case 'face': return 'primary';
      case 'plate': return 'secondary';
      case 'gunny': return 'success';
      case 'contextual': return 'warning';
      default: return 'default';
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
          🏭 Unified Warehouse AI Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Real-time AI monitoring with facial recognition, license plate detection, gunny bag counting, and contextual intelligence
        </Typography>
      </Box>

      {/* System Status Bar */}
      <Paper sx={{ p: 2, mb: 3, bgcolor: isConnected ? 'success.light' : 'error.light' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              icon={isConnected ? <CheckIcon /> : <ErrorIcon />}
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              variant="filled"
            />
            {systemStatus && (
              <Typography variant="body2">
                Modules: {Object.values(systemStatus.modules).filter(Boolean).length}/4 Active
              </Typography>
            )}
          </Box>
          <Box>
            <IconButton onClick={loadSystemStatus} size="small">
              <RefreshIcon />
            </IconButton>
            <Button
              variant={cameraActive ? "contained" : "outlined"}
              color={cameraActive ? "error" : "primary"}
              startIcon={cameraActive ? <StopIcon /> : <VideoIcon />}
              onClick={toggleCamera}
              sx={{ ml: 1 }}
            >
              {cameraActive ? 'Stop Camera' : 'Start Camera'}
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Real-time Detection Alert */}
      {realTimeDetection && (
        <Alert
          severity="info"
          sx={{ mb: 3 }}
          icon={getModuleIcon(realTimeDetection.module)}
        >
          <Typography variant="h6">
            New {realTimeDetection.module} detection!
          </Typography>
          <Typography variant="body2">
            Confidence: {(realTimeDetection.data.confidence * 100).toFixed(1)}% 
            at {formatTimestamp(realTimeDetection.timestamp)}
          </Typography>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Module Statistics Cards */}
        <Grid item xs={12} lg={8}>
          <Grid container spacing={2}>
            {Object.entries(moduleStats).map(([module, stats]) => (
              <Grid item xs={6} md={3} key={module}>
                <Card sx={{ height: '100%' }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Avatar
                      sx={{
                        bgcolor: `${getModuleColor(module)}.main`,
                        mx: 'auto',
                        mb: 1
                      }}
                    >
                      {getModuleIcon(module)}
                    </Avatar>
                    <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                      {module}
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {stats.detections}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {stats.lastUpdate ? `Last: ${formatTimestamp(stats.lastUpdate)}` : 'No activity'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* File Upload Section */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardHeader
              title="Process Media"
              avatar={<UploadIcon />}
            />
            <CardContent>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept="image/*,video/*"
                style={{ display: 'none' }}
              />
              <Button
                variant="outlined"
                fullWidth
                onClick={() => fileInputRef.current?.click()}
                sx={{ mb: 2 }}
                startIcon={<UploadIcon />}
              >
                Choose File
              </Button>
              
              {selectedFile && (
                <>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Selected: {selectedFile.name}
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => processFile(['face', 'plate', 'gunny', 'contextual'])}
                      disabled={isProcessing}
                    >
                      Process All Modules
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => processFile(['face'])}
                      disabled={isProcessing}
                      size="small"
                    >
                      Face Only
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => processFile(['plate'])}
                      disabled={isProcessing}
                      size="small"
                    >
                      Plate Only
                    </Button>
                  </Box>
                </>
              )}
              
              {isProcessing && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="caption" sx={{ mt: 1 }}>
                    Processing...
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Detections */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Recent Detections"
              avatar={<TimelineIcon />}
              action={
                <Button onClick={loadRecentDetections} startIcon={<RefreshIcon />}>
                  Refresh
                </Button>
              }
            />
            <CardContent>
              <Tabs value={activeTab} onChange={(e, val) => setActiveTab(val)}>
                <Tab label="All" />
                <Tab label="Face Recognition" />
                <Tab label="License Plates" />
                <Tab label="Gunny Bags" />
                <Tab label="Contextual" />
              </Tabs>
              
              <Box sx={{ mt: 2, maxHeight: 400, overflow: 'auto' }}>
                <List>
                  {recentDetections
                    .filter(detection => 
                      activeTab === 0 || 
                      (activeTab === 1 && detection.module === 'face') ||
                      (activeTab === 2 && detection.module === 'plate') ||
                      (activeTab === 3 && detection.module === 'gunny') ||
                      (activeTab === 4 && detection.module === 'contextual')
                    )
                    .slice(0, 10)
                    .map((detection, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemIcon>
                            <Avatar
                              size="small"
                              sx={{ bgcolor: `${getModuleColor(detection.module)}.main` }}
                            >
                              {getModuleIcon(detection.module)}
                            </Avatar>
                          </ListItemIcon>
                          <ListItemText
                            primary={`${detection.module} Detection`}
                            secondary={
                              <>
                                <Typography variant="caption" display="block">
                                  {formatTimestamp(detection.timestamp)} • 
                                  Confidence: {(detection.confidence * 100).toFixed(1)}%
                                </Typography>
                                <Typography variant="body2">
                                  {JSON.stringify(detection.data).substring(0, 100)}...
                                </Typography>
                              </>
                            }
                          />
                          {detection.frame_data && (
                            <IconButton
                              size="small"
                              onClick={() => {
                                setProcessingResults({ frame_data: detection.frame_data });
                                setShowResultsDialog(true);
                              }}
                            >
                              <ViewIcon />
                            </IconButton>
                          )}
                        </ListItem>
                        {index < recentDetections.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                </List>
                
                {recentDetections.length === 0 && (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ textAlign: 'center', py: 4 }}
                  >
                    No recent detections
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Results Dialog */}
      <Dialog
        open={showResultsDialog}
        onClose={() => setShowResultsDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Processing Results</DialogTitle>
        <DialogContent>
          {processingResults?.frame_data && (
            <Box sx={{ textAlign: 'center', mb: 2 }}>
              <img
                ref={resultImageRef}
                src={`data:image/jpeg;base64,${processingResults.frame_data}`}
                alt="Processing Result"
                style={{ maxWidth: '100%', height: 'auto' }}
              />
            </Box>
          )}
          
          {processingResults && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Detection Summary
              </Typography>
              <pre style={{ 
                background: '#f5f5f5', 
                padding: '16px', 
                borderRadius: '4px',
                overflow: 'auto',
                maxHeight: '300px'
              }}>
                {JSON.stringify(processingResults, null, 2)}
              </pre>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default UnifiedWarehouseDashboard;
