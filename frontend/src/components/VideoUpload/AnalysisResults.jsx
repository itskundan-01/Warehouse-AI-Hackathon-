import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Button,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Videocam as VideocamIcon,
  Event as EventIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const TabPanel = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ width: '100%' }}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const AnalysisResults = ({ 
  analysisId, 
  moduleType, 
  onRefresh,
  initialResults = null 
}) => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(initialResults);
  const [tabValue, setTabValue] = useState(0);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Simulate fetching analysis results
  const fetchResults = async () => {
    setLoading(true);
    try {
      // Simulate API call based on module type
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResults = generateMockResults(moduleType);
      setResults(mockResults);
    } catch (error) {
      console.error('Failed to fetch results:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (analysisId && !initialResults) {
      fetchResults();
    }
  }, [analysisId, initialResults]);

  // Generate mock results based on module type
  const generateMockResults = (moduleType) => {
    const baseResult = {
      id: analysisId,
      status: 'completed',
      processingTime: '00:02:34',
      confidence: 0.92,
      timestamp: new Date().toLocaleString(),
    };

    switch (moduleType) {
      case 'gunny-counter':
        return {
          ...baseResult,
          totalCount: 247,
          accuracy: 98.5,
          volumeEstimate: '61.75 m³',
          detections: [
            { timestamp: '00:00:15', count: 12, confidence: 0.95 },
            { timestamp: '00:01:32', count: 34, confidence: 0.89 },
            { timestamp: '00:02:18', count: 28, confidence: 0.97 }
          ],
          events: [
            { time: '00:00:45', type: 'High Activity', description: 'Multiple bags detected in loading area' },
            { time: '00:01:55', type: 'Quality Check', description: 'Bag stacking pattern verified' }
          ]
        };

      case 'vehicle-recognition':
        return {
          ...baseResult,
          vehiclesDetected: 8,
          licensePlates: [
            { plate: 'KA-01-AB-1234', confidence: 0.98, authorized: true, timestamp: '00:00:23' },
            { plate: 'MH-02-CD-5678', confidence: 0.85, authorized: false, timestamp: '00:01:45' },
            { plate: 'TN-03-EF-9012', confidence: 0.92, authorized: true, timestamp: '00:02:15' }
          ],
          events: [
            { time: '00:01:45', type: 'Unauthorized Vehicle', description: 'Vehicle MH-02-CD-5678 not in authorized list' },
            { time: '00:02:30', type: 'Exit Event', description: 'Vehicle KA-01-AB-1234 exiting premises' }
          ]
        };

      case 'facial-recognition':
        return {
          ...baseResult,
          personsDetected: 15,
          authorized: 12,
          unauthorized: 3,
          recognitions: [
            { name: 'John Doe', confidence: 0.96, authorized: true, timestamp: '00:00:12' },
            { name: 'Unknown Person', confidence: 0.78, authorized: false, timestamp: '00:01:20' },
            { name: 'Jane Smith', confidence: 0.94, authorized: true, timestamp: '00:02:05' }
          ],
          events: [
            { time: '00:01:20', type: 'Unauthorized Access', description: 'Unknown person detected at entrance' },
            { time: '00:02:45', type: 'Staff Movement', description: 'Authorized personnel in restricted area' }
          ]
        };

      case 'contextual-intelligence':
        return {
          ...baseResult,
          eventsDetected: 23,
          anomalies: 2,
          insights: [
            { category: 'Activity', description: 'High traffic detected during loading hours', confidence: 0.89 },
            { category: 'Security', description: 'Unusual movement pattern detected', confidence: 0.76 },
            { category: 'Operations', description: 'Efficient workflow maintained', confidence: 0.94 }
          ],
          events: [
            { time: '00:00:30', type: 'Activity Spike', description: 'Increased personnel movement detected' },
            { time: '00:01:15', type: 'Anomaly', description: 'Unusual object placement pattern' },
            { time: '00:02:00', type: 'Normal Operation', description: 'Standard warehouse operations resumed' }
          ]
        };

      default:
        return baseResult;
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleEventDetails = (event) => {
    setSelectedEvent(event);
    setDetailsOpen(true);
  };

  const handleDownloadReport = () => {
    // Simulate report download
    console.log('Downloading analysis report...');
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <VideocamIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Processing Video Analysis...</Typography>
          </Box>
          <LinearProgress variant="indeterminate" sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            This may take a few minutes depending on video length and analysis complexity.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!results) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No analysis results available yet. Upload a video to get started.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Results Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h5" gutterBottom>
                Analysis Results
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analysis ID: {results.id} | Completed: {results.timestamp}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={onRefresh || fetchResults}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                size="small"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadReport}
              >
                Download Report
              </Button>
            </Box>
          </Box>

          {/* Status Chips */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              icon={<CheckCircleIcon />}
              label={`Status: ${results.status.toUpperCase()}`}
              color="success"
              variant="outlined"
            />
            <Chip
              label={`Confidence: ${(results.confidence * 100).toFixed(1)}%`}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`Processing Time: ${results.processingTime}`}
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Results Tabs */}
      <Card>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<AssessmentIcon />} label="Summary" />
          <Tab icon={<EventIcon />} label="Events" />
          <Tab icon={<TimelineIcon />} label="Timeline" />
        </Tabs>

        {/* Summary Tab */}
        <TabPanel value={tabValue} index={0}>
          {renderSummaryContent(results, moduleType)}
        </TabPanel>

        {/* Events Tab */}
        <TabPanel value={tabValue} index={1}>
          <List>
            {results.events?.map((event, index) => (
              <React.Fragment key={index}>
                <ListItem 
                  button 
                  onClick={() => handleEventDetails(event)}
                >
                  <ListItemIcon>
                    {event.type.includes('Unauthorized') || event.type.includes('Anomaly') ? 
                      <ErrorIcon color="error" /> : 
                      <InfoIcon color="primary" />
                    }
                  </ListItemIcon>
                  <ListItemText
                    primary={event.type}
                    secondary={`${event.time} - ${event.description}`}
                  />
                </ListItem>
                {index < results.events.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </TabPanel>

        {/* Timeline Tab */}
        <TabPanel value={tabValue} index={2}>
          {renderTimelineContent(results, moduleType)}
        </TabPanel>
      </Card>

      {/* Event Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedEvent?.type}</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            <strong>Time:</strong> {selectedEvent?.time}
          </Typography>
          <Typography variant="body1" gutterBottom>
            <strong>Description:</strong> {selectedEvent?.description}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Additional details and context would be displayed here in a real implementation.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Helper function to render module-specific summary content
const renderSummaryContent = (results, moduleType) => {
  switch (moduleType) {
    case 'gunny-counter':
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="primary">{results.totalCount}</Typography>
            <Typography variant="body2">Total Bags Counted</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="success.main">{results.accuracy}%</Typography>
            <Typography variant="body2">Detection Accuracy</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="info.main">{results.volumeEstimate}</Typography>
            <Typography variant="body2">Estimated Volume</Typography>
          </Grid>
        </Grid>
      );

    case 'vehicle-recognition':
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="primary">{results.vehiclesDetected}</Typography>
            <Typography variant="body2">Vehicles Detected</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="success.main">
              {results.licensePlates?.filter(p => p.authorized).length}
            </Typography>
            <Typography variant="body2">Authorized Vehicles</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="error.main">
              {results.licensePlates?.filter(p => !p.authorized).length}
            </Typography>
            <Typography variant="body2">Unauthorized Vehicles</Typography>
          </Grid>
        </Grid>
      );

    case 'facial-recognition':
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="primary">{results.personsDetected}</Typography>
            <Typography variant="body2">Persons Detected</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="success.main">{results.authorized}</Typography>
            <Typography variant="body2">Authorized Personnel</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="error.main">{results.unauthorized}</Typography>
            <Typography variant="body2">Unauthorized Persons</Typography>
          </Grid>
        </Grid>
      );

    case 'contextual-intelligence':
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="primary">{results.eventsDetected}</Typography>
            <Typography variant="body2">Events Detected</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="warning.main">{results.anomalies}</Typography>
            <Typography variant="body2">Anomalies Found</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" color="success.main">
              {results.insights?.length || 0}
            </Typography>
            <Typography variant="body2">Insights Generated</Typography>
          </Grid>
        </Grid>
      );

    default:
      return (
        <Typography variant="body1">
          Analysis completed successfully. Detailed results will be displayed here.
        </Typography>
      );
  }
};

// Helper function to render timeline content
const renderTimelineContent = (results, moduleType) => {
  const timelineData = results.detections || results.licensePlates || results.recognitions || [];
  
  if (timelineData.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No timeline data available for this analysis.
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Timestamp</TableCell>
            <TableCell>Details</TableCell>
            <TableCell>Confidence</TableCell>
            <TableCell>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {timelineData.map((item, index) => (
            <TableRow key={index}>
              <TableCell>{item.timestamp}</TableCell>
              <TableCell>
                {item.count ? `Count: ${item.count}` : 
                 item.plate ? `Plate: ${item.plate}` :
                 item.name ? `Person: ${item.name}` : 
                 'Event detected'}
              </TableCell>
              <TableCell>
                <Chip 
                  label={`${(item.confidence * 100).toFixed(1)}%`}
                  size="small"
                  color={item.confidence > 0.9 ? 'success' : item.confidence > 0.7 ? 'warning' : 'error'}
                />
              </TableCell>
              <TableCell>
                {item.authorized !== undefined ? (
                  <Chip 
                    label={item.authorized ? 'Authorized' : 'Unauthorized'}
                    size="small"
                    color={item.authorized ? 'success' : 'error'}
                  />
                ) : (
                  <Chip label="Detected" size="small" color="primary" />
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default AnalysisResults;
