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
  DialogTitle,
  Avatar
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
  Article as ArticleIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon
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
  const [searchLoading, setSearchLoading] = useState(false);
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

  // Replace this line in useEffect or wherever mock data is set:
  // dispatch(fetchInsights());
  // With the following mock data for demo:

  const demoMockInsights = [
    {
      id: 'evt1',
      description: '🔥 Fire detected near Loading Dock',
      insight_type: 'safety',
      severity: 'high',
      confidence_score: 0.97,
      timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
      metadata: { location: 'Loading Dock', camera: 'CAM002', zone: 'Zone B' },
      source_modules: ['YOLOv8', 'FireNet']
    },
    {
      id: 'evt2',
      description: '🚫 Unauthorized person entered Warehouse A',
      insight_type: 'security',
      severity: 'high',
      confidence_score: 0.92,
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      metadata: { location: 'Warehouse A', camera: 'CAM003', zone: 'Zone A' },
      source_modules: ['ArcFace', 'DeepSort']
    },
    {
      id: 'evt3',
      description: '🧑‍🔧 Worker handling gunny bags in Storage Area',
      insight_type: 'operation',
      severity: 'low',
      confidence_score: 0.85,
      timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
      metadata: { location: 'Storage Area', camera: 'CAM004', zone: 'Zone C' },
      source_modules: ['YOLOv8', 'SAM']
    },
    {
      id: 'evt4',
      description: '🚚 Vehicle entered Main Gate (AP16AB1234)',
      insight_type: 'vehicle',
      severity: 'medium',
      confidence_score: 0.88,
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      metadata: { location: 'Main Gate', camera: 'CAM001', plate: 'AP16AB1234' },
      source_modules: ['PaddleOCR', 'YOLOv8']
    },
    {
      id: 'evt5',
      description: '📦 Gunny bags stacked in Zone B',
      insight_type: 'operation',
      severity: 'low',
      confidence_score: 0.81,
      timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
      metadata: { location: 'Zone B', camera: 'CAM005' },
      source_modules: ['YOLOv8', 'SAM']
    }
  ];

  const demoMockAnalytics = {
    loading: false,
    error: null,
    last_updated: new Date().toISOString(),
    model_accuracy: 0.93,
    // Add more realistic analytics data as needed
  };

  // In useEffect, set these mocks to Redux or local state for demo
  useEffect(() => {
    // For demo, set mock data directly
    dispatch({ type: 'context/fetchInsights/fulfilled', payload: { list: demoMockInsights, loading: false, error: null } });
    dispatch({ type: 'context/fetchPredictiveAnalytics/fulfilled', payload: demoMockAnalytics });
  }, [dispatch]);

  // Add at the top of the component, after demoMockInsights definition:
  const demoEventPool = [
    {
      id: 'evt6',
      description: '🚨 Suspicious movement detected near South Perimeter',
      insight_type: 'anomaly',
      severity: 'medium',
      confidence_score: 0.78,
      timestamp: new Date().toISOString(),
      metadata: { location: 'South Perimeter', camera: 'CAM005' },
      source_modules: ['YOLOv8']
    },
    {
      id: 'evt7',
      description: '🧯 Fire extinguisher used in Zone C',
      insight_type: 'safety',
      severity: 'medium',
      confidence_score: 0.82,
      timestamp: new Date().toISOString(),
      metadata: { location: 'Zone C', camera: 'CAM004' },
      source_modules: ['FireNet']
    },
    {
      id: 'evt8',
      description: '🔑 Access granted to Supervisor (ID: SUP123)',
      insight_type: 'access',
      severity: 'low',
      confidence_score: 0.99,
      timestamp: new Date().toISOString(),
      metadata: { location: 'Warehouse B', camera: 'CAM003' },
      source_modules: ['ArcFace']
    }
    // Add more as needed
  ];

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle search submission
  const handleSearch = () => {
    setSearchLoading(true);
    
    // Create search parameters
    const params = {
      keyword: searchQuery,
      location: selectedLocation || undefined,
      eventTypes: selectedEventTypes.length > 0 ? selectedEventTypes : undefined,
      startTime: dateRange.start ? new Date(dateRange.start).toISOString() : undefined,
      endTime: dateRange.end ? new Date(dateRange.end).toISOString() : undefined,
    };
    
    dispatch(fetchInsights(params)).finally(() => {
      setSearchLoading(false);
    });
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
  const filteredInsights = (insights.list || []).filter(insight => {
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

  // Add a helper to get event type icon/label
  const getEventTypeIcon = (type) => {
    switch (type) {
      case 'safety': return '🔥';
      case 'security': return '🚫';
      case 'operation': return '🧑‍🔧';
      case 'vehicle': return '🚚';
      case 'anomaly': return '🚨';
      case 'access': return '🔑';
      default: return 'ℹ️';
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

  // In useEffect, add a timer to simulate live event feed updates
  useEffect(() => {
    // For demo, set mock data directly
    dispatch({ type: 'context/fetchInsights/fulfilled', payload: { list: demoMockInsights, loading: false, error: null } });
    dispatch({ type: 'context/fetchPredictiveAnalytics/fulfilled', payload: demoMockAnalytics });

    // Simulate live event feed updates
    const interval = setInterval(() => {
      // Pick a random event from the pool, update timestamp and id
      const randomIdx = Math.floor(Math.random() * demoEventPool.length);
      const newEvent = {
        ...demoEventPool[randomIdx],
        id: `evt${Math.floor(Math.random() * 10000)}`,
        timestamp: new Date().toISOString()
      };
      dispatch({
        type: 'context/fetchInsights/fulfilled',
        payload: prev => ({
          ...prev,
          list: [newEvent, ...prev.list].slice(0, 20), // keep only latest 20
          loading: false,
          error: null
        })
      });
    }, 10000); // every 10 seconds
    return () => clearInterval(interval);
  }, [dispatch]);

  // Add a simple chatbot for event queries in the Search & Query tab. This will be a floating chat widget or a section at the bottom of the Search & Query tab, with canned responses for demo. The chatbot will respond to user queries about events, e.g., 'Show me all fire events', 'Who entered Warehouse A yesterday?', etc.
  const demoChatbotResponses = [
    {
      question: /fire|burn|smoke/i,
      answer: 'There was a fire detected near the Loading Dock at 14:32 today. No injuries reported. Event ID: evt1.'
    },
    {
      question: /unauthorized|intruder|entry/i,
      answer: 'An unauthorized person entered Warehouse A at 14:27. Security was notified. Event ID: evt2.'
    },
    {
      question: /vehicle|truck|ap16ab1234/i,
      answer: 'Vehicle AP16AB1234 entered Main Gate at 14:15. Event ID: evt4.'
    },
    {
      question: /gunny|bags|stacked/i,
      answer: 'Gunny bags were stacked in Zone B at 14:00. Event ID: evt5.'
    },
    {
      question: /.*/,
      answer: 'Sorry, I could not find a relevant event. Please try a different query.'
    }
  ];

  // Add chatbot state:
  const [chatMessages, setChatMessages] = useState([
    { sender: 'bot', text: 'Hi! Ask me about recent events, e.g., "Show me all fire events".' }
  ]);
  const [chatInput, setChatInput] = useState('');

  const handleChatSend = () => {
    if (!chatInput.trim()) return;
    setChatMessages(msgs => [...msgs, { sender: 'user', text: chatInput }]);
    // Find canned response
    const found = demoChatbotResponses.find(r => r.question.test(chatInput));
    setTimeout(() => {
      setChatMessages(msgs => [...msgs, { sender: 'bot', text: found.answer }]);
    }, 800);
    setChatInput('');
  };

  return (
    <Container maxWidth="xl" className="fade-in">
      {/* Modern Header Section */}
      <Box className="modern-header" sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar 
            sx={{ 
              width: 60, 
              height: 60, 
              mr: 3,
              bgcolor: 'primary.main',
              fontSize: '1.5rem'
            }}
          >
            <PsychologyIcon fontSize="inherit" />
          </Avatar>
          <Box>
            <Typography 
              variant="h3" 
              component="h1" 
              sx={{ 
                fontWeight: 700,
                color: 'primary.main',
                mb: 1
              }}
            >
              Contextual Intelligence
            </Typography>
            <Typography variant="h6" color="text.secondary">
              AI-powered video analysis and intelligent pattern recognition
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Tabs for different sections */}
      <Paper 
        className="modern-card glass-effect" 
        elevation={0} 
        sx={{ 
          mb: 4,
          borderRadius: 3,
          overflow: 'hidden'
        }}
      >
        <Box sx={{ 
          borderBottom: 1, 
          borderColor: 'divider',
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)'
        }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
            sx={{
              '& .MuiTab-root': {
                py: 3,
                fontSize: '1rem',
                fontWeight: 600,
                minHeight: 'auto',
                '&.Mui-selected': {
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                }
              }
            }}
          >
            <Tab 
              icon={<VideoIcon />} 
              label="Video Analysis" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab 
              icon={<SearchIcon />} 
              label="Search & Query" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab 
              icon={<TrendingUpIcon />} 
              label="Predictive Analytics" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab 
              icon={<AssessmentIcon />} 
              label="Reports" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
          </Tabs>
        </Box>
      </Paper>

      {/* Video Analysis tab */}
        <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper 
              className="modern-card glass-effect" 
              elevation={0}
              sx={{ 
                p: 3, 
                height: '100%',
                borderRadius: 3,
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                }
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ 
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                Real-time Video Feed
              </Typography>
              <Divider sx={{ mb: 3, opacity: 0.6 }} />

              <Box 
                sx={{ 
                  height: 400, 
                  background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  mb: 2,
                  position: 'relative',
                  borderRadius: 2,
                  overflow: 'hidden',
                  border: '2px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.1)'
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
                    <InputLabel id="video-source-label" sx={{ color: 'primary.main' }}>
                      Video Source
                    </InputLabel>
                    <Select
                      labelId="video-source-label"
                      value={videoSource}
                      onChange={(e) => setVideoSource(e.target.value)}
                      label="Video Source"
                      disabled={isPlaying || isAnalyzing}
                      sx={{
                        borderRadius: 2,
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                          background: 'rgba(255, 255, 255, 0.8)',
                          backdropFilter: 'blur(10px)',
                          '&:hover': {
                            background: 'rgba(255, 255, 255, 0.9)',
                          },
                          '&.Mui-focused': {
                            background: 'rgba(255, 255, 255, 0.95)',
                          }
                        }
                      }}
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
                      sx={{
                        borderRadius: 2,
                        py: 1.5,
                        fontWeight: 600,
                        textTransform: 'none',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        transition: 'all 0.3s ease-in-out',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
                        },
                        '&:disabled': {
                          opacity: 0.6
                        }
                      }}
                    >
                      {isPlaying ? 'Stop Stream' : 'Start Stream'}
                    </Button>
                    <Button
                      variant="contained"
                      color="secondary"
                      onClick={handleAnalyzeVideo}
                      startIcon={<AnalyticsIcon />}
                      disabled={!isPlaying || isAnalyzing}
                      fullWidth
                      sx={{
                        borderRadius: 2,
                        py: 1.5,
                        fontWeight: 600,
                        textTransform: 'none',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        transition: 'all 0.3s ease-in-out',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
                        },
                        '&:disabled': {
                          opacity: 0.6
                        }
                      }}
                    >
                      Analyze
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper 
              className="modern-card glass-effect" 
              elevation={0}
              sx={{ 
                p: 3, 
                height: '100%',
                borderRadius: 3,
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                }
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ 
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                Recent Insights
              </Typography>
              <Divider sx={{ mb: 3, opacity: 0.6 }} />

              {insights.loading ? (
                <CircularProgress sx={{ display: 'block', mx: 'auto', my: 4 }} />
              ) : (insights.list || []).length === 0 ? (
                <Alert severity="info">
                  No insights available. Start a video stream and analyze it to generate insights.
                </Alert>
              ) : (
                <List>
                  {(insights.list || []).slice(0, 5).map((insight) => (
                    <ListItem 
                      key={insight.id} 
                      sx={{ 
                        mb: 2, 
                        background: 'rgba(255, 255, 255, 0.7)',
                        backdropFilter: 'blur(5px)',
                        borderRadius: 2,
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        transition: 'all 0.3s ease-in-out',
                        '&:hover': {
                          background: 'rgba(255, 255, 255, 0.9)',
                          transform: 'translateX(4px)',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                        }
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
        <Paper 
          className="modern-card glass-effect" 
          elevation={0}
          sx={{ 
            p: 3, 
            mb: 4,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease-in-out'
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ 
            fontWeight: 600,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Search Events & Insights
          </Typography>
          <Divider sx={{ mb: 3, opacity: 0.6 }} />

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12}>
              <TextField
                label="Search"
                variant="outlined"
                fullWidth
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search events, people, objects, activities..."
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleSearch} disabled={searchLoading}>
                        {searchLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    background: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(10px)',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      background: 'rgba(255, 255, 255, 0.9)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    },
                    '&.Mui-focused': {
                      background: 'rgba(255, 255, 255, 0.95)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: 'primary.main',
                    fontWeight: 500
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="location-filter-label" sx={{ color: 'primary.main', fontWeight: 500 }}>
                  Location
                </InputLabel>
                <Select
                  labelId="location-filter-label"
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  label="Location"
                  sx={{
                    borderRadius: 2,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      background: 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      '&:hover': {
                        background: 'rgba(255, 255, 255, 0.9)',
                      },
                      '&.Mui-focused': {
                        background: 'rgba(255, 255, 255, 0.95)',
                      }
                    }
                  }}
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
                <InputLabel id="event-type-filter-label" sx={{ color: 'primary.main', fontWeight: 500 }}>
                  Event Type
                </InputLabel>
                <Select
                  labelId="event-type-filter-label"
                  multiple
                  value={selectedEventTypes}
                  onChange={(e) => setSelectedEventTypes(e.target.value)}
                  label="Event Type"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip 
                          key={value} 
                          label={value} 
                          size="small" 
                          sx={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            color: 'white',
                            fontWeight: 500
                          }}
                        />
                      ))}
                    </Box>
                  )}
                  sx={{
                    borderRadius: 2,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      background: 'rgba(255, 255, 255, 0.8)',
                      backdropFilter: 'blur(10px)',
                      '&:hover': {
                        background: 'rgba(255, 255, 255, 0.9)',
                      },
                      '&.Mui-focused': {
                        background: 'rgba(255, 255, 255, 0.95)',
                      }
                    }
                  }}
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
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    background: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(10px)',
                    '&:hover': {
                      background: 'rgba(255, 255, 255, 0.9)',
                    },
                    '&.Mui-focused': {
                      background: 'rgba(255, 255, 255, 0.95)',
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: 'primary.main',
                    fontWeight: 500
                  }
                }}
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
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    background: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(10px)',
                    '&:hover': {
                      background: 'rgba(255, 255, 255, 0.9)',
                    },
                    '&.Mui-focused': {
                      background: 'rgba(255, 255, 255, 0.95)',
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: 'primary.main',
                    fontWeight: 500
                  }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SearchIcon />}
                  onClick={handleSearch}
                  sx={{
                    borderRadius: 3,
                    py: 1.5,
                    px: 4,
                    fontWeight: 600,
                    textTransform: 'none',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 24px rgba(102, 126, 234, 0.6)',
                      background: 'linear-gradient(135deg, #5a67d8 0%, #667eea 100%)',
                    }
                  }}
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
                        {getEventTypeIcon(insight.insight_type)} {insight.description}
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

        {/* Chatbot section */}
        <Box sx={{ mt: 4, p: 2, borderRadius: 2, background: 'rgba(245,245,255,0.8)', boxShadow: '0 2px 8px rgba(102,126,234,0.08)' }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
            💬 Event Chatbot (Demo)
          </Typography>
          <Box sx={{ maxHeight: 180, overflowY: 'auto', mb: 1 }}>
            {chatMessages.map((msg, idx) => (
              <Box key={idx} sx={{ display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start', mb: 0.5 }}>
                <Box sx={{
                  bgcolor: msg.sender === 'user' ? 'primary.light' : 'grey.200',
                  color: msg.sender === 'user' ? 'white' : 'text.primary',
                  px: 2, py: 1, borderRadius: 2, maxWidth: '70%',
                }}>
                  {msg.text}
                </Box>
              </Box>
            ))}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="Ask about events..."
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleChatSend(); }}
            />
            <Button variant="contained" onClick={handleChatSend} disabled={!chatInput.trim()}>
              Send
            </Button>
          </Box>
        </Box>
      </TabPanel>

      {/* Predictive Analytics tab */}
      <TabPanel value={tabValue} index={2}>
        <Paper 
          className="modern-card glass-effect" 
          elevation={0}
          sx={{ 
            p: 3,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease-in-out'
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ 
            fontWeight: 600,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Predictive Analytics
          </Typography>
          <Divider sx={{ mb: 3, opacity: 0.6 }} />

          {predictiveAnalytics.loading ? (
            <CircularProgress sx={{ display: 'block', mx: 'auto', my: 4 }} />
          ) : predictiveAnalytics.error ? (
            <Alert severity="error">{predictiveAnalytics.error}</Alert>
          ) : (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card 
                  className="modern-card glass-effect"
                  elevation={0}
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    background: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(10px)',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                    }
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ 
                      fontWeight: 600,
                      color: 'primary.main'
                    }}>
                      Inventory Forecast
                    </Typography>
                    <Box sx={{ 
                      height: 300, 
                      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                      borderRadius: 2, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mb: 2,
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      boxShadow: 'inset 0 0 20px rgba(0,0,0,0.05)'
                    }}>
                      <Typography variant="body1" sx={{ 
                        color: 'text.secondary',
                        fontWeight: 500
                      }}>
                        📊 Inventory forecast chart would be displayed here
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
                <Card 
                  className="modern-card glass-effect"
                  elevation={0}
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    background: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(10px)',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                    }
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ 
                      fontWeight: 600,
                      color: 'primary.main'
                    }}>
                      Security Risk Forecast
                    </Typography>
                    <Box sx={{ 
                      height: 300, 
                      background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                      borderRadius: 2, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mb: 2,
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      boxShadow: 'inset 0 0 20px rgba(0,0,0,0.05)'
                    }}>
                      <Typography variant="body1" sx={{ 
                        color: 'text.secondary',
                        fontWeight: 500
                      }}>
                        🔒 Security risk forecast chart would be displayed here
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        Model Accuracy: {predictiveAnalytics.model_accuracy ? 
                          `${Math.round(predictiveAnalytics.model_accuracy * 100)}%` : 'N/A'}
                      </Typography>
                      <Button 
                        size="small" 
                        endIcon={<TuneIcon />}
                        sx={{
                          borderRadius: 2,
                          textTransform: 'none',
                          fontWeight: 500,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a67d8 0%, #667eea 100%)',
                            transform: 'translateY(-1px)',
                            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
                          }
                        }}
                      >
                        Adjust Parameters
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card 
                  className="modern-card glass-effect"
                  elevation={0}
                  sx={{ 
                    borderRadius: 3,
                    background: 'rgba(255, 255, 255, 0.8)',
                    backdropFilter: 'blur(10px)',
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                    }
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ 
                      fontWeight: 600,
                      color: 'primary.main'
                    }}>
                      Vehicle Traffic Forecast
                    </Typography>
                    <Box sx={{ 
                      height: 300, 
                      background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                      borderRadius: 2, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mb: 2,
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      boxShadow: 'inset 0 0 20px rgba(0,0,0,0.05)'
                    }}>
                      <Typography variant="body1" sx={{ 
                        color: 'text.secondary',
                        fontWeight: 500
                      }}>
                        🚛 Vehicle traffic forecast chart would be displayed here
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Button 
                        startIcon={<SaveIcon />}
                        size="small"
                        sx={{
                          borderRadius: 2,
                          textTransform: 'none',
                          fontWeight: 500,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          px: 3,
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a67d8 0%, #667eea 100%)',
                            transform: 'translateY(-1px)',
                            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
                          }
                        }}
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
        <Paper 
          className="modern-card glass-effect" 
          elevation={0}
          sx={{ 
            p: 3,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease-in-out'
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ 
            fontWeight: 600,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Generate Reports
          </Typography>
          <Divider sx={{ mb: 3, opacity: 0.6 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card 
                className="modern-card glass-effect"
                elevation={0}
                sx={{
                  borderRadius: 3,
                  background: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(10px)',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ 
                    fontWeight: 600,
                    color: 'primary.main',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}>
                    🔐 Security Report
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
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            background: 'rgba(255, 255, 255, 0.8)',
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                              background: 'rgba(255, 255, 255, 0.9)',
                            },
                            '&.Mui-focused': {
                              background: 'rgba(255, 255, 255, 0.95)',
                            }
                          }
                        }}
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
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            background: 'rgba(255, 255, 255, 0.8)',
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                              background: 'rgba(255, 255, 255, 0.9)',
                            },
                            '&.Mui-focused': {
                              background: 'rgba(255, 255, 255, 0.95)',
                            }
                          }
                        }}
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
                    sx={{
                      borderRadius: 2,
                      py: 1.5,
                      px: 3,
                      fontWeight: 600,
                      textTransform: 'none',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 24px rgba(102, 126, 234, 0.6)',
                        background: 'linear-gradient(135deg, #5a67d8 0%, #667eea 100%)',
                      }
                    }}
                  >
                    Generate Report
                  </Button>
                </Box>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card 
                className="modern-card glass-effect"
                elevation={0}
                sx={{
                  borderRadius: 3,
                  background: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(10px)',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 40px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ 
                    fontWeight: 600,
                    color: 'secondary.main',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                  }}>
                    📊 Operational Report
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
                    sx={{
                      borderRadius: 2,
                      py: 1.5,
                      px: 3,
                      fontWeight: 600,
                      textTransform: 'none',
                      background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                      boxShadow: '0 4px 12px rgba(245, 87, 108, 0.4)',
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 24px rgba(245, 87, 108, 0.6)',
                        background: 'linear-gradient(135deg, #f5576c 0%, #f093fb 100%)',
                      }
                    }}
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
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }
        }}
      >
        <DialogTitle sx={{ 
          fontWeight: 600,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🔍 Event Details
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
                  background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
                  borderRadius: 2,
                  display: 'flex', 
                  justifyContent: 'center',
                  alignItems: 'center',
                  mb: 2,
                  border: '2px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.1)'
                }}>
                  <Typography variant="body1" sx={{ 
                    color: '#fff',
                    fontWeight: 500
                  }}>
                    🎥 Video playback would appear here
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
        <DialogActions sx={{ p: 3, background: 'rgba(255, 255, 255, 0.5)' }}>
          <Button 
            onClick={() => setOpenVideoDialog(false)}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 500,
              px: 3,
              color: 'text.secondary',
              '&:hover': {
                background: 'rgba(0, 0, 0, 0.04)',
              }
            }}
          >
            Close
          </Button>
          <Button 
            variant="contained" 
            onClick={() => setOpenVideoDialog(false)}
            sx={{
              borderRadius: 2,
              py: 1,
              px: 3,
              fontWeight: 600,
              textTransform: 'none',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
              transition: 'all 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-1px)',
                boxShadow: '0 6px 20px rgba(102, 126, 234, 0.6)',
                background: 'linear-gradient(135deg, #5a67d8 0%, #667eea 100%)',
              }
            }}
          >
            Take Action
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ContextualIntelligencePage;