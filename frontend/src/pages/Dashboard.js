import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  IconButton,
  Skeleton,
  Chip
} from '@mui/material';
import {
  Person as PersonIcon,
  LocalShipping as VehicleIcon,
  Inventory as GunnyIcon,
  Search as ContextIcon,
  ArrowForward as ArrowForwardIcon,
  Today as TodayIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';

// Mock data for dashboard (in a real app, this would come from Redux/API)
const mockData = {
  facialRecognition: {
    authorized: 24,
    unauthorized: 2,
    total: 26,
    recentEvents: [
      { id: 1, name: 'John Doe', time: '10:45 AM', authorized: true, location: 'Main Gate' },
      { id: 2, name: 'Unknown Person', time: '09:30 AM', authorized: false, location: 'Loading Area' },
      { id: 3, name: 'Jane Smith', time: '09:15 AM', authorized: true, location: 'Office Entrance' }
    ]
  },
  vehicleRecognition: {
    authorized: 18,
    unauthorized: 1,
    total: 19,
    recentEvents: [
      { id: 1, plate: 'KA-01-AB-1234', time: '11:20 AM', authorized: true, vehicleType: 'Truck' },
      { id: 2, plate: 'MH-04-XY-9876', time: '10:05 AM', authorized: true, vehicleType: 'Van' },
      { id: 3, plate: 'Unknown', time: '08:45 AM', authorized: false, vehicleType: 'Car' }
    ]
  },
  gunnyCounter: {
    todayCount: 580,
    weeklyAverage: 543,
    monthlyTotal: 12045,
    recentBatches: [
      { id: 1, count: 125, time: '11:00 AM', location: 'Loading Bay 1' },
      { id: 2, count: 95, time: '10:30 AM', location: 'Loading Bay 2' },
      { id: 3, count: 150, time: '09:45 AM', location: 'Loading Bay 1' }
    ]
  },
  systemHealth: {
    status: 'Healthy',
    uptime: '5 days, 7 hours',
    diskUsage: '43%',
    memoryUsage: '38%',
    cpuUsage: '26%',
    alerts: [
      { id: 1, message: 'CPU spike detected at 10:15 AM', severity: 'warning', resolved: true },
      { id: 2, message: 'Camera 3 disconnected at 08:30 AM', severity: 'error', resolved: false }
    ]
  }
};

const Dashboard = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  
  // In a real app, we would fetch data from Redux/API
  useEffect(() => {
    // Simulate API call
    const fetchDashboardData = async () => {
      try {
        // In a real app, this would be an API call or redux action
        // await dispatch(fetchDashboardStats());
        
        // For demo, use mock data with timeout to simulate loading
        setTimeout(() => {
          setDashboardData(mockData);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [dispatch]);

  // Navigation handlers
  const navigateToModule = (path) => {
    navigate(path);
  };
  
  // Render loading skeletons
  if (loading) {
    return (
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
          Dashboard
        </Typography>
        
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((item) => (
            <Grid item xs={12} md={6} lg={3} key={item}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Skeleton variant="text" width="60%" height={40} />
                <Skeleton variant="text" width="40%" height={30} sx={{ mb: 2 }} />
                <Skeleton variant="rectangular" height={120} />
              </Paper>
            </Grid>
          ))}
          
          {[1, 2].map((item) => (
            <Grid item xs={12} md={6} key={`large-${item}`}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Skeleton variant="text" width="40%" height={40} />
                <Skeleton variant="text" width="30%" height={30} sx={{ mb: 1 }} />
                <Skeleton variant="rectangular" height={200} />
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }
  
  return (
    <Box sx={{ py: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          <TodayIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </Typography>
      </Box>
      
      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Facial Recognition Stats */}
        <Grid item xs={12} md={6} lg={3}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative',
              overflow: 'hidden',
              '&:hover .module-action': {
                opacity: 1,
              }
            }}
            elevation={2}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ backgroundColor: 'primary.main', mr: 2 }}>
                <PersonIcon />
              </Avatar>
              <Typography variant="h6">Facial Recognition</Typography>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {dashboardData.facialRecognition.total}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Detections
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {dashboardData.facialRecognition.authorized}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Authorized
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error.main">
                  {dashboardData.facialRecognition.unauthorized}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Unauthorized
                </Typography>
              </Box>
            </Box>
            
            <Button 
              variant="text" 
              color="primary"
              className="module-action"
              onClick={() => navigateToModule('/facial-recognition')}
              sx={{ 
                mt: 'auto', 
                alignSelf: 'flex-end',
                opacity: 0,
                transition: 'opacity 0.2s'
              }}
              endIcon={<ArrowForwardIcon />}
            >
              View Details
            </Button>
          </Paper>
        </Grid>
        
        {/* Vehicle Recognition Stats */}
        <Grid item xs={12} md={6} lg={3}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative',
              overflow: 'hidden',
              '&:hover .module-action': {
                opacity: 1,
              }
            }}
            elevation={2}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ backgroundColor: 'secondary.main', mr: 2 }}>
                <VehicleIcon />
              </Avatar>
              <Typography variant="h6">Vehicle Recognition</Typography>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="secondary.main">
                  {dashboardData.vehicleRecognition.total}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Vehicles
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {dashboardData.vehicleRecognition.authorized}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Authorized
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error.main">
                  {dashboardData.vehicleRecognition.unauthorized}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Unauthorized
                </Typography>
              </Box>
            </Box>
            
            <Button 
              variant="text" 
              color="secondary"
              className="module-action"
              onClick={() => navigateToModule('/vehicle-recognition')}
              sx={{ 
                mt: 'auto', 
                alignSelf: 'flex-end',
                opacity: 0,
                transition: 'opacity 0.2s'
              }}
              endIcon={<ArrowForwardIcon />}
            >
              View Details
            </Button>
          </Paper>
        </Grid>
        
        {/* Gunny Counter Stats */}
        <Grid item xs={12} md={6} lg={3}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative',
              overflow: 'hidden',
              '&:hover .module-action': {
                opacity: 1,
              }
            }}
            elevation={2}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                <GunnyIcon />
              </Avatar>
              <Typography variant="h6">Gunny Counter</Typography>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {dashboardData.gunnyCounter.todayCount}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Today's Count
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {dashboardData.gunnyCounter.weeklyAverage}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Weekly Avg
                </Typography>
              </Box>
            </Box>
            
            <Button 
              variant="text" 
              color="warning"
              className="module-action"
              onClick={() => navigateToModule('/gunny-counter')}
              sx={{ 
                mt: 'auto', 
                alignSelf: 'flex-end',
                opacity: 0,
                transition: 'opacity 0.2s'
              }}
              endIcon={<ArrowForwardIcon />}
            >
              View Details
            </Button>
          </Paper>
        </Grid>
        
        {/* System Health Stats */}
        <Grid item xs={12} md={6} lg={3}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative',
              overflow: 'hidden',
            }}
            elevation={2}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                <ContextIcon />
              </Avatar>
              <Typography variant="h6">System Health</Typography>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2">Status:</Typography>
                <Chip 
                  label={dashboardData.systemHealth.status} 
                  color="success" 
                  size="small" 
                />
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2">Uptime:</Typography>
                <Typography variant="body2" fontWeight="medium">
                  {dashboardData.systemHealth.uptime}
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Resources:</Typography>
                <Typography variant="body2" fontWeight="medium">
                  CPU: {dashboardData.systemHealth.cpuUsage}
                </Typography>
              </Box>
            </Box>
            
            <Button 
              variant="text" 
              color="info"
              className="module-action"
              onClick={() => navigateToModule('/system-health')}
              sx={{ 
                mt: 'auto', 
                alignSelf: 'flex-end'
              }}
              endIcon={<ArrowForwardIcon />}
            >
              View Details
            </Button>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Recent Events & Alerts */}
      <Grid container spacing={3}>
        {/* Recent Personnel Detections */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }} elevation={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Recent Personnel Detections</Typography>
              <Button 
                size="small" 
                onClick={() => navigateToModule('/facial-recognition')}
                endIcon={<ArrowForwardIcon />}
              >
                View All
              </Button>
            </Box>
            
            <List>
              {dashboardData.facialRecognition.recentEvents.map((event) => (
                <React.Fragment key={event.id}>
                  <ListItem
                    secondaryAction={
                      <IconButton edge="end" aria-label="view">
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: event.authorized ? 'success.main' : 'error.main' }}>
                        <PersonIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="body1">
                          {event.name}
                          {!event.authorized && (
                            <Chip 
                              label="Unauthorized" 
                              color="error" 
                              size="small" 
                              sx={{ ml: 1 }} 
                            />
                          )}
                        </Typography>
                      }
                      secondary={
                        <React.Fragment>
                          <Typography component="span" variant="body2" color="text.primary">
                            {event.location}
                          </Typography>
                          {" — "}{event.time}
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                  <Divider variant="inset" component="li" />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
        
        {/* Recent Vehicle Detections */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }} elevation={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Recent Vehicle Detections</Typography>
              <Button 
                size="small" 
                onClick={() => navigateToModule('/vehicle-recognition')}
                endIcon={<ArrowForwardIcon />}
              >
                View All
              </Button>
            </Box>
            
            <List>
              {dashboardData.vehicleRecognition.recentEvents.map((event) => (
                <React.Fragment key={event.id}>
                  <ListItem
                    secondaryAction={
                      <IconButton edge="end" aria-label="view">
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: event.authorized ? 'success.main' : 'error.main' }}>
                        <VehicleIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="body1">
                          {event.plate}
                          {!event.authorized && (
                            <Chip 
                              label="Unauthorized" 
                              color="error" 
                              size="small" 
                              sx={{ ml: 1 }} 
                            />
                          )}
                        </Typography>
                      }
                      secondary={
                        <React.Fragment>
                          <Typography component="span" variant="body2" color="text.primary">
                            {event.vehicleType}
                          </Typography>
                          {" — "}{event.time}
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                  <Divider variant="inset" component="li" />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;