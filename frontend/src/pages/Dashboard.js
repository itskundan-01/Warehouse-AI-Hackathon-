import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
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
  Chip,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Person as PersonIcon,
  LocalShipping as VehicleIcon,
  Inventory as GunnyIcon,
  Search as ContextIcon,
  ArrowForward as ArrowForwardIcon,
  Today as TodayIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  InsertChart as ChartIcon,
} from '@mui/icons-material';
import Chart from 'react-apexcharts';

// Mock data for dashboard (in a real app, this would come from Redux/API)
const mockData = {
  facialRecognition: {
    authorized: 24,
    unauthorized: 2,
    total: 26,
    accuracy: 97.5,
    recentEvents: [
      { id: 1, name: 'John Doe', time: '10:45 AM', authorized: true, location: 'Main Gate' },
      { id: 2, name: 'Unknown Person', time: '09:30 AM', authorized: false, location: 'Loading Area' },
      { id: 3, name: 'Jane Smith', time: '09:15 AM', authorized: true, location: 'Office Entrance' }
    ],
    alerts: [
      { id: 1, severity: 'error', message: 'Unauthorized access attempt at Loading Area', time: '09:30 AM' }
    ]
  },
  vehicleRecognition: {
    authorized: 18,
    unauthorized: 1,
    total: 19,
    accuracy: 98.2,
    recentEvents: [
      { id: 1, plate: 'KA-01-AB-1234', time: '11:20 AM', authorized: true, vehicleType: 'Truck' },
      { id: 2, plate: 'MH-04-XY-9876', time: '10:05 AM', authorized: true, vehicleType: 'Van' },
      { id: 3, plate: 'Unknown', time: '08:45 AM', authorized: false, vehicleType: 'Car' }
    ],
    alerts: [
      { id: 1, severity: 'warning', message: 'Unregistered vehicle detected at Gate 2', time: '08:45 AM' }
    ]
  },
  gunnyCounter: {
    todayCount: 580,
    weeklyAverage: 543,
    monthlyTotal: 12045,
    accuracy: 99.1,
    volumetricAnalysis: {
      totalVolume: '145.5 m³',
      averageBagSize: '0.25 m³',
      variancePercentage: 3.2
    },
    recentBatches: [
      { id: 1, count: 125, time: '11:00 AM', location: 'Loading Bay 1' },
      { id: 2, count: 95, time: '10:30 AM', location: 'Loading Bay 2' },
      { id: 3, count: 150, time: '09:45 AM', location: 'Loading Bay 1' }
    ],
    dailyCounts: [510, 495, 550, 580, 620, 540, 580]
  },
  contextIntelligence: {
    eventsDetected: 15,
    queriesProcessed: 28,
    anomaliesDetected: 2,
    accuracy: 94.8,
    recentQueries: [
      { id: 1, query: "Show unauthorized access events from yesterday", time: "09:15 AM", status: "completed" },
      { id: 2, query: "Count vehicles that stayed more than 2 hours", time: "08:30 AM", status: "completed" }
    ],
    recentEvents: [
      { id: 1, event: "Worker without safety helmet detected", time: "10:20 AM", location: "Storage Area B" },
      { id: 2, event: "Unusual movement near restricted zone", time: "09:45 AM", location: "Server Room" }
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
  },
  warehouseMetrics: {
    activeCameras: 24,
    totalWarehouses: 3,
    activeAlerts: 2,
    stockAccuracy: 97.8
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
  
  // Gunny bag count chart options
  const gunnyCountChartOptions = {
    chart: {
      type: 'area',
      height: 160,
      sparkline: {
        enabled: true
      },
      toolbar: {
        show: false
      }
    },
    stroke: {
      curve: 'smooth',
      width: 2
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.7,
        opacityTo: 0.3
      }
    },
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today'],
    yaxis: {
      min: 0
    },
    colors: ['#FF9800']
  };

  // Accuracy comparison chart options
  const accuracyChartOptions = {
    chart: {
      type: 'bar',
      height: 250,
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
        borderRadius: 4
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    xaxis: {
      categories: ['Facial Rec.', 'Vehicle Rec.', 'Gunny Counter', 'Context Intel.'],
    },
    yaxis: {
      min: 80,
      max: 100,
      title: {
        text: 'Accuracy (%)'
      }
    },
    fill: {
      opacity: 1
    },
    tooltip: {
      y: {
        formatter: function (val) {
          return val + "%"
        }
      }
    },
    colors: ['#3f51b5']
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

      {/* Active Alerts */}
      {(dashboardData.facialRecognition.alerts.length > 0 || 
         dashboardData.vehicleRecognition.alerts.length > 0) && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            <WarningIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1, color: 'warning.main' }} />
            Active Alerts
          </Typography>
          <Grid container spacing={2}>
            {dashboardData.facialRecognition.alerts.map(alert => (
              <Grid item xs={12} md={6} key={`facial-alert-${alert.id}`}>
                <Alert 
                  severity={alert.severity}
                  action={
                    <Button 
                      color="inherit" 
                      size="small"
                      onClick={() => navigateToModule('/facial-recognition')}
                    >
                      VIEW
                    </Button>
                  }
                >
                  <AlertTitle>Facial Recognition Alert</AlertTitle>
                  {alert.message} — <strong>{alert.time}</strong>
                </Alert>
              </Grid>
            ))}
            {dashboardData.vehicleRecognition.alerts.map(alert => (
              <Grid item xs={12} md={6} key={`vehicle-alert-${alert.id}`}>
                <Alert 
                  severity={alert.severity}
                  action={
                    <Button 
                      color="inherit" 
                      size="small"
                      onClick={() => navigateToModule('/vehicle-recognition')}
                    >
                      VIEW
                    </Button>
                  }
                >
                  <AlertTitle>Vehicle Recognition Alert</AlertTitle>
                  {alert.message} — <strong>{alert.time}</strong>
                </Alert>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Warehouse Overview Card */}
      <Card sx={{ mb: 4, borderRadius: 2 }} elevation={2}>
        <CardHeader title="Warehouse Network Overview" />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary.main">
                  {dashboardData.warehouseMetrics.totalWarehouses}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Monitored Warehouses
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="secondary.main">
                  {dashboardData.warehouseMetrics.activeCameras}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Cameras
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="error.main">
                  {dashboardData.warehouseMetrics.activeAlerts}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Alerts
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {dashboardData.warehouseMetrics.stockAccuracy}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Stock Accuracy
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
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

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2">Accuracy:</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {dashboardData.facialRecognition.accuracy}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={dashboardData.facialRecognition.accuracy} 
                color="primary"
                sx={{ height: 8, borderRadius: 4 }}
              />
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

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2">OCR Accuracy:</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {dashboardData.vehicleRecognition.accuracy}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={dashboardData.vehicleRecognition.accuracy} 
                color="secondary"
                sx={{ height: 8, borderRadius: 4 }}
              />
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
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
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
                  {dashboardData.gunnyCounter.monthlyTotal.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Monthly Total
                </Typography>
              </Box>
            </Box>

            {/* Area chart for gunny counts */}
            <Box sx={{ my: 1 }}>
              <Chart 
                options={gunnyCountChartOptions}
                series={[{
                  name: 'Daily Count',
                  data: dashboardData.gunnyCounter.dailyCounts
                }]}
                type="area"
                height={90}
              />
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
        
        {/* Contextual Intelligence Stats */}
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
              <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                <ContextIcon />
              </Avatar>
              <Typography variant="h6">Contextual Intelligence</Typography>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {dashboardData.contextIntelligence.eventsDetected}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Events Detected
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error.main">
                  {dashboardData.contextIntelligence.anomaliesDetected}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Anomalies
                </Typography>
              </Box>
            </Box>

            <Box sx={{ mb: 2, mt: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2">Query Processing:</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {dashboardData.contextIntelligence.accuracy}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={dashboardData.contextIntelligence.accuracy} 
                color="info"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            
            <Button 
              variant="text" 
              color="info"
              className="module-action"
              onClick={() => navigateToModule('/contextual-intelligence')}
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
      </Grid>

      {/* Accuracy Comparison Chart */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }} elevation={2}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <ChartIcon sx={{ color: 'primary.main', mr: 1 }} />
              <Typography variant="h6">
                Module Performance Comparison
              </Typography>
            </Box>
            <Chart 
              options={accuracyChartOptions}
              series={[{
                name: 'Accuracy',
                data: [
                  dashboardData.facialRecognition.accuracy,
                  dashboardData.vehicleRecognition.accuracy,
                  dashboardData.gunnyCounter.accuracy,
                  dashboardData.contextIntelligence.accuracy
                ]
              }]}
              type="bar"
              height={300}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }} elevation={2}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              System Status
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} fontSize="small" />
                <Typography variant="body1">
                  System Status: <strong>{dashboardData.systemHealth.status}</strong>
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <InfoIcon sx={{ color: 'info.main', mr: 1 }} fontSize="small" />
                <Typography variant="body1">
                  Uptime: <strong>{dashboardData.systemHealth.uptime}</strong>
                </Typography>
              </Box>
            </Box>
            
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Resource Utilization</Typography>
            
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">CPU</Typography>
                <Typography variant="body2">{dashboardData.systemHealth.cpuUsage}</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={parseInt(dashboardData.systemHealth.cpuUsage)} 
                color="primary"
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
            
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">Memory</Typography>
                <Typography variant="body2">{dashboardData.systemHealth.memoryUsage}</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={parseInt(dashboardData.systemHealth.memoryUsage)} 
                color="secondary"
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
            
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">Disk</Typography>
                <Typography variant="body2">{dashboardData.systemHealth.diskUsage}</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={parseInt(dashboardData.systemHealth.diskUsage)} 
                color="warning"
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
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