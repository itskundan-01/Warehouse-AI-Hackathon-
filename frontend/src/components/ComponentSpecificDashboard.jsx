import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Person as PersonIcon,
  DirectionsCar as CarIcon,
  Inventory as InventoryIcon,
  Psychology as BrainIcon,
  CloudUpload as UploadIcon,
  PlayArrow as ProcessIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Visibility as ViewIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';

const ComponentSpecificDashboard = () => {
  // State management
  const [selectedComponent, setSelectedComponent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  
  // Refs
  const fileInputRef = useRef(null);
  const wsRef = useRef(null);

  // Component definitions
  const components = {
    face_recognition: {
      name: 'Face Recognition',
      icon: <PersonIcon />,
      description: 'Identify and recognize faces in images and videos',
      color: '#2196F3',
      acceptedTypes: 'image/*,video/*',
      file: 'apscscl_simple_facial_recognition.py'
    },
    license_plate: {
      name: 'License Plate Detection',
      icon: <CarIcon />,
      description: 'Detect and read license plates using Gemini OCR',
      color: '#4CAF50',
      acceptedTypes: 'image/*,video/*',
      file: 'gemini.py'
    },
    gunny_bag_counter: {
      name: 'Gunny Bag Counter',
      icon: <InventoryIcon />,
      description: 'Count and analyze gunny bags with visual output',
      color: '#FF9800',
      acceptedTypes: 'image/*,video/*',
      file: 'gunny_bag_line_counter_local.py'
    },
    contextual_intelligence: {
      name: 'Contextual Intelligence',
      icon: <BrainIcon />,
      description: 'Advanced warehouse scene analysis and insights',
      color: '#9C27B0',
      acceptedTypes: 'image/*,video/*',
      file: 'standalone_contextual_test.py'
    }
  };

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket('ws://localhost:8000/ws/realtime');
        
        wsRef.current.onopen = () => {
          setIsConnected(true);
          console.log('🔗 WebSocket connected');
        };
        
        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message:', data);
          
          if (data.type === 'component_result') {
            setResult(data.data);
            setProcessing(false);
          }
        };
        
        wsRef.current.onclose = () => {
          setIsConnected(false);
          console.log('🔌 WebSocket disconnected');
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
        
        wsRef.current.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          setIsConnected(false);
        };
        
      } catch (error) {
        console.error('❌ WebSocket connection error:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Fetch system status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/status');
        const data = await response.json();
        setSystemStatus(data);
      } catch (error) {
        console.error('❌ Status fetch error:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);
    }
  };

  // Handle component selection
  const handleComponentSelect = (event) => {
    const component = event.target.value;
    setSelectedComponent(component);
    setResult(null);
    setError(null);
    
    // Clear file selection when component changes
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setSelectedFile(null);
  };

  // Process file with selected component
  const processFile = async () => {
    if (!selectedComponent || !selectedFile) {
      setError('Please select both a component and a file');
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`http://localhost:8000/api/process/${selectedComponent}`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Processing failed');
      }
    } catch (error) {
      console.error('❌ Processing error:', error);
      setError('Network error or server not responding');
    } finally {
      setProcessing(false);
    }
  };

  // Render result based on component type
  const renderResult = () => {
    if (!result || !result.success) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="body2">
            {result?.error || error || 'Processing failed'}
          </Typography>
        </Alert>
      );
    }

    // Defensive: If result.component is not defined or not in components, show error
    if (!result.component || !components[result.component]) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="body2">
            Invalid or missing component in result. Please check backend response.
          </Typography>
        </Alert>
      );
    }

    const component = components[result.component];
    
    return (
      <Card sx={{ mt: 2 }}>
        <CardHeader
          avatar={<Avatar sx={{ bgcolor: component.color }}>{component.icon}</Avatar>}
          title={`${component.name} Results`}
          subheader={`Processed in ${result.processing_time?.toFixed(2)}s`}
        />
        <CardContent>
          {/* Display output image if available */}
          {result.output_image && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Visual Output:
              </Typography>
              <img
                src={`data:image/jpeg;base64,${result.output_image}`}
                alt="Processing result"
                style={{ maxWidth: '100%', height: 'auto', borderRadius: '8px' }}
              />
            </Box>
          )}
          
          {/* Component-specific results */}
          {result.component === 'face_recognition' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Face Recognition Results:
              </Typography>
              
              {/* Video-specific results */}
              {result.data.total_frames && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Video Analysis: {result.data.processed_frames} frames processed from {result.data.total_frames} total frames
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Duration: {result.data.video_duration?.toFixed(1)}s
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total face detections: {result.data.total_face_detections || 0}
                  </Typography>
                </Box>
              )}
              
              {/* Image-specific results */}
              {!result.data.total_frames && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Faces detected: {result.data.face_count || 0}
                </Typography>
              )}
              
              {/* Unique people (video) or detected faces (image) */}
              {result.data.unique_people && result.data.unique_people.length > 0 && (
                <List>
                  {result.data.unique_people.map((person, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <PersonIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={person.person_id || 'Unknown'}
                        secondary={`Role: ${person.role || 'Unknown'} | Confidence: ${(person.max_confidence * 100).toFixed(1)}% | Appearances: ${person.appearances || 1}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              {result.data.faces_detected && result.data.faces_detected.length > 0 && (
                <List>
                  {result.data.faces_detected.map((face, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <PersonIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={face.person_id || 'Unknown'}
                        secondary={`Confidence: ${(face.confidence * 100).toFixed(1)}%`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          )}
          
          {result.component === 'license_plate' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                License Plate Detection Results:
              </Typography>
              
              {/* Video-specific results */}
              {result.data.total_frames && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Video Analysis: {result.data.processed_frames} frames processed from {result.data.total_frames} total frames
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Duration: {result.data.video_duration?.toFixed(1)}s
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total plate detections: {result.data.total_plate_detections || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Processing method: {result.data.processing_method || 'unknown'}
                  </Typography>
                </Box>
              )}
              
              {/* Image-specific results */}
              {!result.data.total_frames && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Plates detected: {result.data.plates_count || result.data.plate_count || 0}
                </Typography>
              )}
              
              {/* Processing method info */}
              {result.data.method && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Processing method: {result.data.method}
                </Typography>
              )}
              
              {/* Unique plates (video) or detected plates (image) */}
              {result.data.unique_plates && result.data.unique_plates.length > 0 && (
                <List>
                  {result.data.unique_plates.map((plate, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CarIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={plate.text || 'No text detected'}
                        secondary={`Vehicle: ${plate.vehicle_type || 'Unknown'} | Confidence: ${(plate.max_confidence * 100).toFixed(1)}% | Appearances: ${plate.appearances || 1}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              {result.data.plates_detected && result.data.plates_detected.length > 0 && (
                <List>
                  {result.data.plates_detected.map((plate, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CarIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={plate.plate_number || plate.text || 'No text detected'}
                        secondary={`Vehicle: ${plate.vehicle_type || 'Unknown'} | Confidence: ${(plate.confidence * 100).toFixed(1)}% | Status: ${plate.status || 'N/A'}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          )}
          
          {result.component === 'gunny_bag_counter' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Gunny Bag Counter Results:
              </Typography>
              
              {/* Video-specific results */}
              {result.data.total_frames && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Video Analysis: {result.data.processed_frames} frames processed from {result.data.total_frames} total frames
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Duration: {result.data.video_duration?.toFixed(1)}s
                  </Typography>
                  {result.data.bag_count_stats && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        Average bags per frame: {result.data.bag_count_stats.average_bags}
                      </Typography>
                      <Typography variant="body2">
                        Maximum bags detected: {result.data.bag_count_stats.maximum_bags}
                      </Typography>
                      <Typography variant="body2">
                        Minimum bags detected: {result.data.bag_count_stats.minimum_bags}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
              
              {/* Image-specific results */}
              {!result.data.total_frames && !result.data.frames_processed && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Bags counted: {result.data.bag_count || result.data.total_bags_in || 0}
                </Typography>
              )}
              
              {/* Real gunny bag counter results */}
              {result.data.total_bags_in !== undefined && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Bags IN: {result.data.total_bags_in}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Bags OUT: {result.data.total_bags_out}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Net count: {result.data.net_count}
                  </Typography>
                  {result.data.frames_processed && (
                    <Typography variant="body2" color="text.secondary">
                      Frames processed: {result.data.frames_processed}
                    </Typography>
                  )}
                </Box>
              )}
              
              {result.data.bags_detected && result.data.bags_detected.length > 0 && (
                <List>
                  {result.data.bags_detected.map((bag, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <InventoryIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={bag.bag_id || `Bag ${index + 1}`}
                        secondary={`Confidence: ${(bag.confidence * 100).toFixed(1)}%`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          )}
          
          {result.component === 'contextual_intelligence' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Contextual Intelligence Results:
              </Typography>
              
              {/* Video-specific results */}
              {result.data.video_analysis && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Video Analysis: {result.data.video_analysis.total_analyses} frames analyzed
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Events detected: {result.data.video_analysis.total_events || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Objects detected: {result.data.video_analysis.total_objects || 0}
                  </Typography>
                </Box>
              )}
              
              {result.data.insights && result.data.insights.length > 0 && (
                <List>
                  {result.data.insights.map((insight, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <BrainIcon />
                      </ListItemIcon>
                      <ListItemText primary={insight} />
                    </ListItem>
                  ))}
                </List>
              )}
              
              {result.data.recommendations && result.data.recommendations.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Recommendations:
                  </Typography>
                  {result.data.recommendations.map((rec, index) => (
                    <Chip key={index} label={rec} sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              )}
              
              {result.data.events_detected && result.data.events_detected.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Events Detected:
                  </Typography>
                  <List>
                    {result.data.events_detected.slice(0, 5).map((event, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={event.description || event.type}
                          secondary={`Severity: ${event.severity} | Confidence: ${(event.confidence * 100).toFixed(1)}%`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
          
          {/* Raw data (collapsible) */}
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Raw data: {JSON.stringify(result.data, null, 2)}
          </Typography>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        🎯 Component-Specific AI Processing
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Select a specific AI component and upload files for targeted processing
      </Typography>

      {/* Connection Status */}
      <Alert severity={isConnected ? "success" : "warning"} sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isConnected ? <SuccessIcon /> : <ErrorIcon />}
          <Typography>
            {isConnected ? 'Connected to backend' : 'Backend connection lost'}
          </Typography>
        </Box>
      </Alert>

      <Grid container spacing={3}>
        {/* Component Selection */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="1. Select AI Component"
              subheader="Choose which AI system to use for processing"
            />
            <CardContent>
              <FormControl fullWidth>
                <InputLabel>AI Component</InputLabel>
                <Select
                  value={selectedComponent}
                  onChange={handleComponentSelect}
                  label="AI Component"
                >
                  {Object.entries(components).map(([key, component]) => (
                    <MenuItem key={key} value={key}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {component.icon}
                        <Box>
                          <Typography variant="body1">{component.name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {component.description}
                          </Typography>
                        </Box>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedComponent && (
                <Box sx={{ mt: 2 }}>
                  <Chip
                    icon={components[selectedComponent].icon}
                    label={`Processing file: ${components[selectedComponent].file}`}
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* File Upload */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="2. Upload File"
              subheader="Select a file to process with the chosen component"
            />
            <CardContent>
              <input
                ref={fileInputRef}
                type="file"
                accept={selectedComponent ? components[selectedComponent].acceptedTypes : "*"}
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              
              <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={() => fileInputRef.current?.click()}
                disabled={!selectedComponent}
                fullWidth
                sx={{ mb: 2 }}
              >
                Choose File
              </Button>

              {selectedFile && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Selected: {selectedFile.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                </Box>
              )}

              <Button
                variant="contained"
                startIcon={processing ? <CircularProgress size={20} /> : <ProcessIcon />}
                onClick={processFile}
                disabled={!selectedComponent || !selectedFile || processing}
                fullWidth
              >
                {processing ? 'Processing...' : 'Process File'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="System Status"
              subheader="Component availability and system health"
            />
            <CardContent>
              {systemStatus && (
                <Grid container spacing={2}>
                  {Object.entries(systemStatus.components || {}).map(([key, component]) => (
                    <Grid item xs={12} sm={6} md={3} key={key}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {components[key]?.icon}
                        <Box>
                          <Typography variant="body2">
                            {components[key]?.name || key}
                          </Typography>
                          <Chip
                            size="small"
                            label={component.available ? 'Available' : 'Not Available'}
                            color={component.available ? 'success' : 'error'}
                          />
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Display */}
        <Grid item xs={12}>
          <Box>
            {result || error ? renderResult() : null}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComponentSpecificDashboard;
