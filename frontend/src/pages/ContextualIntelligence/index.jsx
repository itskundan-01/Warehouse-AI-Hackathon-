import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Divider,
  Grid,
  Paper,
  Typography,
  Tab,
  Tabs,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle
} from '@mui/material';
import {
  Search as SearchIcon,
  VideoLibrary as VideoIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Visibility as VisibilityIcon,
  PlayArrow as PlayArrowIcon,
  PauseCircle as PauseIcon,
  Save as SaveIcon,
  FilterList as FilterListIcon,
  VideoCall as VideoCallIcon,
  Tune as TuneIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Article as ArticleIcon
} from '@mui/icons-material';

import {
  fetchInsights,
  fetchPredictiveAnalytics,
  generateReport
} from '../../store/slices/contextSlice';
import contextualIntelligenceService from '../../services/api/contextualIntelligenceService';

// Tab panel component for tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`context-tabpanel-${index}`}
      aria-labelledby={`context-tab-${index}`}
      {...other}
      style={{ padding: '20px 0' }}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

const ContextualIntelligencePage = () => {
  const dispatch = useDispatch();
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedEventTypes, setSelectedEventTypes] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [videoSource, setVideoSource] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [openVideoDialog, setOpenVideoDialog] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days ago
    end: new Date().toISOString().split('T')[0] // today
  });

  // Get state from Redux
  const { insights, predictiveAnalytics, reportGeneration } = useSelector(state => state.context);

  // Load context data on component mount
  useEffect(() => {
    dispatch(fetchInsights());
    dispatch(fetchPredictiveAnalytics());
  }, [dispatch]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle search submission
  const handleSearch = () => {
    // Create search parameters
    const params = {
      keyword: searchQuery,
      location: selectedLocation || undefined,
      eventTypes: selectedEventTypes.length > 0 ? selectedEventTypes : undefined,
      startTime: dateRange.start ? new Date(dateRange.start).toISOString() : undefined,
      endTime: dateRange.end ? new Date(dateRange.end).toISOString() : undefined,
    };
    
    dispatch(fetchInsights(params));
  };

  // Handle video analysis
  const handleAnalyzeVideo = () => {
    if (!videoSource) return;
    
    setIsAnalyzing(true);
    
    // Simulate API call with a timeout
    setTimeout(() => {
      dispatch(fetchInsights());
      setIsAnalyzing(false);
    }, 3000);
  };

  // Handle report generation
  const handleGenerateReport = (reportType) => {
    dispatch(generateReport({
      reportType,
      timeRange: {
        start: dateRange.start ? new Date(dateRange.start).toISOString() : undefined,
        end: dateRange.end ? new Date(dateRange.end).toISOString() : undefined
      }
    }));
  };

  // Handle event selection and dialog
  const handleOpenEventDialog = (event) => {
    setSelectedEvent(event);
    setOpenVideoDialog(true);
  };

  // Filter insights based on search criteria (client-side filtering as backup)
  const filteredInsights = insights.list.filter(insight => {
    if (searchQuery && !insight.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (selectedLocation && insight.metadata.location !== selectedLocation && 
        insight.metadata.zone !== selectedLocation) {
      return false;
    }
    if (selectedEventTypes.length > 0 && 
        !selectedEventTypes.includes(insight.insight_type)) {
      return false;
    }
    return true;
  });

  // Get severity icon based on severity level
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <ErrorIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  // Mock locations for demo (would come from API in production)
  const locationOptions = [
    { value: 'warehouse_a', label: 'Warehouse A' },
    { value: 'warehouse_b', label: 'Warehouse B' },
    { value: 'loading_dock', label: 'Loading Dock' },
    { value: 'south_perimeter', label: 'South Perimeter' },
    { value: 'main_gate', label: 'Main Gate' },
    { value: 'zone_b', label: 'Zone B' }
  ];

  // Mock event types for demo (would come from API in production)
  const eventTypeOptions = [
    { value: 'anomaly', label: 'Anomaly' },
    { value: 'security', label: 'Security Event' },
    { value: 'optimization', label: 'Optimization' },
    { value: 'safety', label: 'Safety Event' },
    { value: 'access', label: 'Access Event' }
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Contextual Intelligence
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" paragraph>
          Analyze video feeds for patterns, anomalies, and contextual insights across the warehouse.
        </Typography>
      </Box>

      {/* Tabs for different sections */}
      <Paper sx={{ mb: 4 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab icon={<VideoIcon />} label="Video Analysis" />
          <Tab icon={<SearchIcon />} label="Search & Query" />
          <Tab icon={<TrendingUpIcon />} label="Predictive Analytics" />
          <Tab icon={<AssessmentIcon />} label="Reports" />
        </Tabs>
      </Paper>

      {/* Video Analysis tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Real-time Video Feed
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Box 
                sx={{ 
                  height: 400, 
                  bgcolor: '#000',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  mb: 2,
                  position: 'relative'
                }}
              >
                {isPlaying ? (
                  <Box sx={{ width: '100%', height: '100%' }}>
                    {/* In a real app, we'd display an actual video stream here */}
                    <Box 
                      sx={{ 
                        width: '100%', 
                        height: '100%', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        color: '#fff'
                      }}
                    >
                      <Typography variant="h6">
                        Simulated Video Feed - Camera {videoSource}
                      </Typography>
                    </Box>
                  </Box>
                ) : (
                  <VideoCallIcon sx={{ fontSize: 64, color: '#555' }} />
                )}

                {isAnalyzing && (
                  <Box 
                    sx={{ 
                      position: 'absolute', 
                      top: 0, 
                      left: 0, 
                      right: 0, 
                      bottom: 0, 
                      bgcolor: 'rgba(0,0,0,0.7)',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      color: '#fff'
                    }}
                  >
                    <CircularProgress color="primary" size={60} sx={{ mb: 2 }} />
                    <Typography variant="h6">
                      Analyzing Video
                    </Typography>
                    <Typography variant="body2" color="rgba(255,255,255,0.7)">
                      Processing frames for contextual insights...
                    </Typography>
                  </Box>
                )}
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel id="video-source-label">Video Source</InputLabel>
                    <Select
                      labelId="video-source-label"
                      value={videoSource}
                      onChange={(e) => setVideoSource(e.target.value)}
                      label="Video Source"
                      disabled={isPlaying || isAnalyzing}
                    >
                      <MenuItem value="">
                        <em>Select a camera</em>
                      </MenuItem>
                      <MenuItem value="CAM001">Camera 1 - Main Gate</MenuItem>
                      <MenuItem value="CAM002">Camera 2 - Loading Dock</MenuItem>
                      <MenuItem value="CAM003">Camera 3 - Warehouse A</MenuItem>
                      <MenuItem value="CAM004">Camera 4 - Warehouse B</MenuItem>
                      <MenuItem value="CAM005">Camera 5 - South Perimeter</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      color={isPlaying ? "error" : "primary"}
                      onClick={() => setIsPlaying(!isPlaying)}
                      startIcon={isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                      disabled={!videoSource || isAnalyzing}
                      fullWidth
                    >
                      {isPlaying ? 'Stop Stream' : 'Start Stream'}
                    </Button>
                    <Button
                      variant="contained"
                      color="secondary"
                      onClick={handleAnalyzeVideo}
                      startIcon={<TuneIcon />}
                      disabled={!videoSource || !isPlaying || isAnalyzing}
                      fullWidth
                    >
                      Analyze
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Recent Insights
              </Typography>
              <Divider sx={{ mb: 3 }} />

              {insights.loading ? (
                <CircularProgress sx={{ display: 'block', mx: 'auto', my: 4 }} />
              ) : insights.list.length === 0 ? (
                <Alert severity="info">
                  No insights available. Start a video stream and analyze it to generate insights.
                </Alert>
              ) : (
                <List>
                  {insights.list.slice(0, 5).map((insight) => (
                    <ListItem 
                      key={insight.id} 
                      sx={{ 
                        mb: 1, 
                        bgcolor: 'rgba(0,0,0,0.03)', 
                        borderRadius: 1
                      }}
                    >
                      <ListItemIcon>
                        {getSeverityIcon(insight.severity)}
                      </ListItemIcon>
                      <ListItemText
                        primary={insight.description}
                        secondary={new Date(insight.timestamp).toLocaleString()}
                      />
                      <ListItemSecondaryAction>
                        <IconButton 
                          edge="end" 
                          onClick={() => handleOpenEventDialog(insight)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Search & Query tab */}
      <TabPanel value={tabValue} index={1}>
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Search Events & Insights
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12}>
              <TextField
                label="Search"
                variant="outlined"
                fullWidth
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter keywords to search events and insights..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="location-filter-label">Location</InputLabel>
                <Select
                  labelId="location-filter-label"
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  label="Location"
                >
                  <MenuItem value="">All Locations</MenuItem>
                  {locationOptions.map(option => (
                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="event-type-filter-label">Event Type</InputLabel>
                <Select
                  labelId="event-type-filter-label"
                  multiple
                  value={selectedEventTypes}
                  onChange={(e) => setSelectedEventTypes(e.target.value)}
                  label="Event Type"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {eventTypeOptions.map(option => (
                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} md={2}>
              <TextField
                label="Start Date"
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid item xs={6} md={2}>
              <TextField
                label="End Date"
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SearchIcon />}
                  onClick={handleSearch}
                >
                  Search
                </Button>
              </Box>
            </Grid>
          </Grid>

          {insights.loading ? (
            <CircularProgress sx={{ display: 'block', mx: 'auto', my: 4 }} />
          ) : insights.error ? (
            <Alert severity="error">{insights.error}</Alert>
          ) : filteredInsights.length === 0 ? (
            <Alert severity="info">
              No results found for your search criteria.
            </Alert>
          ) : (
            <List>
              {filteredInsights.map((insight) => (
                <Paper
                  key={insight.id}
                  elevation={1}
                  sx={{ 
                    mb: 2, 
                    p: 2,
                    borderLeft: 4, 
                    borderColor: 
                      insight.severity === 'high' ? 'error.main' : 
                      insight.severity === 'medium' ? 'warning.main' : 'info.main'
                  }}
                >
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={9}>
                      <Typography variant="h6" gutterBottom>
                        {insight.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                        <Chip 
                          size="small" 
                          label={insight.insight_type} 
                          color="primary" 
                        />
                        <Chip 
                          size="small" 
                          label={`Confidence: ${Math.round(insight.confidence_score * 100)}%`} 
                          color="secondary" 
                        />
                        <Chip 
                          size="small" 
                          label={`Severity: ${insight.severity}`} 
                          color={
                            insight.severity === 'high' ? 'error' : 
                            insight.severity === 'medium' ? 'warning' : 'info'
                          }
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Detected:</strong> {new Date(insight.timestamp).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Location:</strong> {insight.metadata.location || insight.metadata.zone || 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={3} sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                      <Button
                        variant="outlined"
                        startIcon={<VisibilityIcon />}
                        onClick={() => handleOpenEventDialog(insight)}
                        fullWidth
                        sx={{ mb: 1 }}
                      >
                        View Details
                      </Button>
                      <Button
                        variant="outlined"
                        color="secondary"
                        startIcon={<PlayArrowIcon />}
                        fullWidth
                      >
                        Playback Video
                      </Button>
                    </Grid>
                  </Grid>
                </Paper>
              ))}
            </List>
          )}
        </Paper>
      </TabPanel>

      {/* Predictive Analytics tab */}
      <TabPanel value={tabValue} index={2}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Predictive Analytics
          </Typography>
          <Divider sx={{ mb: 3 }} />

          {predictiveAnalytics.loading ? (
            <CircularProgress sx={{ display: 'block', mx: 'auto', my: 4 }} />
          ) : predictiveAnalytics.error ? (
            <Alert severity="error">{predictiveAnalytics.error}</Alert>
          ) : (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Inventory Forecast
                    </Typography>
                    <Box sx={{ 
                      height: 300, 
                      bgcolor: '#f5f5f5', 
                      borderRadius: 1, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mb: 2 
                    }}>
                      <Typography variant="body1">
                        Inventory forecast chart would be displayed here
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" align="right">
                      Last updated: {predictiveAnalytics.last_updated ? 
                        new Date(predictiveAnalytics.last_updated).toLocaleString() : 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Security Risk Forecast
                    </Typography>
                    <Box sx={{ 
                      height: 300, 
                      bgcolor: '#f5f5f5', 
                      borderRadius: 1, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mb: 2 
                    }}>
                      <Typography variant="body1">
                        Security risk forecast chart would be displayed here
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        Model Accuracy: {predictiveAnalytics.model_accuracy ? 
                          `${Math.round(predictiveAnalytics.model_accuracy * 100)}%` : 'N/A'}
                      </Typography>
                      <Button size="small" endIcon={<TuneIcon />}>
                        Adjust Parameters
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Vehicle Traffic Forecast
                    </Typography>
                    <Box sx={{ 
                      height: 300, 
                      bgcolor: '#f5f5f5', 
                      borderRadius: 1, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mb: 2 
                    }}>
                      <Typography variant="body1">
                        Vehicle traffic forecast chart would be displayed here
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Button 
                        startIcon={<SaveIcon />}
                        size="small"
                      >
                        Export Data
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Paper>
      </TabPanel>

      {/* Reports tab */}
      <TabPanel value={tabValue} index={3}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Generate Reports
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Security Report
                  </Typography>
                  <Typography variant="body2" paragraph color="text.secondary">
                    Generate a comprehensive security report including unauthorized access attempts,
                    perimeter breaches, and suspicious activities during the selected time period.
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <TextField
                        label="Start Date"
                        type="date"
                        value={dateRange.start}
                        onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                        InputLabelProps={{ shrink: true }}
                        fullWidth
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="End Date"
                        type="date"
                        value={dateRange.end}
                        onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                        InputLabelProps={{ shrink: true }}
                        fullWidth
                        size="small"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<ArticleIcon />}
                    onClick={() => handleGenerateReport('security')}
                    disabled={reportGeneration.loading}
                  >
                    Generate Report
                  </Button>
                </Box>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Operational Report
                  </Typography>
                  <Typography variant="body2" paragraph color="text.secondary">
                    Generate an operational efficiency report including vehicle traffic analysis,
                    gunny bag handling statistics, and optimization recommendations.
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <TextField
                        label="Start Date"
                        type="date"
                        value={dateRange.start}
                        onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                        InputLabelProps={{ shrink: true }}
                        fullWidth
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="End Date"
                        type="date"
                        value={dateRange.end}
                        onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                        InputLabelProps={{ shrink: true }}
                        fullWidth
                        size="small"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2 }}>
                  <Button
                    variant="contained"
                    color="secondary"
                    startIcon={<ArticleIcon />}
                    onClick={() => handleGenerateReport('operational')}
                    disabled={reportGeneration.loading}
                  >
                    Generate Report
                  </Button>
                </Box>
              </Card>
            </Grid>

            {reportGeneration.loading && (
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
                  <CircularProgress size={24} sx={{ mr: 2 }} />
                  <Typography>Generating report...</Typography>
                </Box>
              </Grid>
            )}

            {reportGeneration.report && (
              <Grid item xs={12}>
                <Alert 
                  severity="success"
                  action={
                    <Button 
                      color="inherit" 
                      size="small"
                      href={reportGeneration.report.report_url}
                      target="_blank"
                    >
                      Download
                    </Button>
                  }
                >
                  Report {reportGeneration.report.report_id} has been generated successfully.
                </Alert>
              </Grid>
            )}

            {reportGeneration.error && (
              <Grid item xs={12}>
                <Alert severity="error">
                  {reportGeneration.error}
                </Alert>
              </Grid>
            )}
          </Grid>
        </Paper>
      </TabPanel>

      {/* Event Detail Dialog */}
      <Dialog 
        open={openVideoDialog} 
        onClose={() => setOpenVideoDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Event Details
        </DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {selectedEvent.description}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip 
                    label={`Type: ${selectedEvent.insight_type}`} 
                    color="primary" 
                    size="small"
                  />
                  <Chip 
                    label={`Severity: ${selectedEvent.severity}`} 
                    color={
                      selectedEvent.severity === 'high' ? 'error' : 
                      selectedEvent.severity === 'medium' ? 'warning' : 'info'
                    }
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ 
                  height: 300, 
                  bgcolor: '#000', 
                  display: 'flex', 
                  justifyContent: 'center',
                  alignItems: 'center',
                  mb: 2
                }}>
                  <Typography variant="body1" color="#fff">
                    Video playback would appear here
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Event Information
                </Typography>
                <Box component="dl" sx={{ 
                  display: 'grid', 
                  gridTemplateColumns: { sm: '1fr', md: '1fr 1fr' },
                  gap: 2
                }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography component="dt" variant="caption" color="text.secondary">
                      Timestamp
                    </Typography>
                    <Typography component="dd" variant="body2">
                      {new Date(selectedEvent.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography component="dt" variant="caption" color="text.secondary">
                      Location
                    </Typography>
                    <Typography component="dd" variant="body2">
                      {selectedEvent.metadata.location || selectedEvent.metadata.zone || 'N/A'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography component="dt" variant="caption" color="text.secondary">
                      Confidence Score
                    </Typography>
                    <Typography component="dd" variant="body2">
                      {Math.round(selectedEvent.confidence_score * 100)}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography component="dt" variant="caption" color="text.secondary">
                      Source Modules
                    </Typography>
                    <Typography component="dd" variant="body2">
                      {selectedEvent.source_modules?.join(', ') || 'N/A'}
                    </Typography>
                  </Box>
                </Box>
                {selectedEvent.metadata && Object.keys(selectedEvent.metadata).length > 0 && (
                  <>
                    <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                      Additional Information
                    </Typography>
                    <Box component="dl" sx={{ 
                      display: 'grid', 
                      gridTemplateColumns: { sm: '1fr', md: '1fr 1fr' },
                      gap: 2
                    }}>
                      {Object.entries(selectedEvent.metadata).map(([key, value]) => (
                        <Box key={key} sx={{ display: 'flex', flexDirection: 'column' }}>
                          <Typography component="dt" variant="caption" color="text.secondary">
                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Typography>
                          <Typography component="dd" variant="body2">
                            {typeof value === 'object' ? JSON.stringify(value) : value.toString()}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </>
                )}
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenVideoDialog(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => setOpenVideoDialog(false)}
            color="primary"
          >
            Take Action
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ContextualIntelligencePage;