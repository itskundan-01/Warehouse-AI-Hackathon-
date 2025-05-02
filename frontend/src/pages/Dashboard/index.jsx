import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box } from '@mui/material';
import StatsSummaryGrid from '../../components/dashboard/StatsSummaryGrid';
import RecentActivityList from '../../components/dashboard/RecentActivityList';
import GunnySummaryCard from '../../components/dashboard/GunnySummaryCard';
import VehicleSummaryCard from '../../components/dashboard/VehicleSummaryCard';
import FacialSummaryCard from '../../components/dashboard/FacialSummaryCard';
import ContextualSummaryCard from '../../components/dashboard/ContextualSummaryCard';
import WarehouseOverview from '../../components/dashboard/WarehouseOverview';
import AlertsSummary from '../../components/dashboard/AlertsSummary';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  
  // In a real application, this data would come from API calls
  const [stats, setStats] = useState({
    gunnyProcessed: '0',
    vehiclesLogged: '0',
    personnelActive: '0',
    alertsToday: '0'
  });
  
  const [moduleData, setModuleData] = useState({
    gunny: {
      totalBags: 2547,
      todayCount: 342,
      activeWarehouse: 'Chennai Central',
      trend: +12.5, // percentage change
    },
    vehicle: {
      totalToday: 38,
      authorized: 35,
      unauthorized: 3,
      pendingVerification: 1,
    },
    facial: {
      authorizedPersonnel: 126,
      presentToday: 42,
      unauthorized: 2,
      recentLogs: [
        { id: 1, name: 'Raj Patel', time: '10:45 AM', status: 'authorized' },
        { id: 2, name: 'Unknown Person', time: '11:20 AM', status: 'unauthorized' }
      ],
    },
    contextual: {
      activeCameras: 24,
      eventsToday: 17,
      openAlerts: 3,
    }
  });
  
  const [loading, setLoading] = useState(true);

  // Simulate fetching data
  useEffect(() => {
    const fetchDashboardData = async () => {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data - would be replaced with actual API calls
      setStats({
        gunnyProcessed: '1,234',
        vehiclesLogged: '38',
        personnelActive: '24',
        alertsToday: '5'
      });
      
      setLoading(false);
    };

    fetchDashboardData();
  }, []);

  const handleModuleClick = (module) => {
    navigate(`/${module}`);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        WarehouseVision AI Dashboard
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Warehouse monitoring overview for May 2, 2025
      </Typography>
      
      <Box mb={4}>
        {/* Stats Summary Cards */}
        <StatsSummaryGrid stats={stats} />
      </Box>
      
      <Grid container spacing={3}>
        {/* Module Summary Cards */}
        <Grid item xs={12} lg={8}>
          <Grid container spacing={3}>
            {/* Gunny Counter Summary */}
            <Grid item xs={12} sm={6}>
              <GunnySummaryCard 
                data={moduleData.gunny}
                onClick={() => handleModuleClick('gunny-counter')} 
              />
            </Grid>
            
            {/* Vehicle Recognition Summary */}
            <Grid item xs={12} sm={6}>
              <VehicleSummaryCard 
                data={moduleData.vehicle}
                onClick={() => handleModuleClick('vehicle-recognition')} 
              />
            </Grid>
            
            {/* Facial Recognition Summary */}
            <Grid item xs={12} sm={6}>
              <FacialSummaryCard 
                data={moduleData.facial}
                onClick={() => handleModuleClick('facial-recognition')} 
              />
            </Grid>
            
            {/* Contextual Intelligence Summary */}
            <Grid item xs={12} sm={6}>
              <ContextualSummaryCard 
                data={moduleData.contextual}
                onClick={() => handleModuleClick('contextual-intelligence')} 
              />
            </Grid>
          </Grid>
        </Grid>
        
        {/* Recent Activity List */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <RecentActivityList />
          </Paper>
        </Grid>
        
        {/* Warehouse Overview */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3 }}>
            <WarehouseOverview />
          </Paper>
        </Grid>
        
        {/* Alerts Summary */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <AlertsSummary />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;