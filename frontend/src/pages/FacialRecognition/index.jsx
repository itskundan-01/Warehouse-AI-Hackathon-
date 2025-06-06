import React, { useState } from 'react';
import { 
  Box, 
  Tab, 
  Tabs, 
  Typography, 
  Paper, 
  Grid, 
  Container,
  Avatar
} from '@mui/material';
import {
  Person as PersonIcon,
  Security as SecurityIcon,
  Assignment as LogsIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import FacialDashboard from '../../components/modules/facial/FacialDashboard';
import PersonnelManagement from './PersonnelManagement';
import AuthorizationLogs from './AuthorizationLogs';
import AccessControl from './AccessControl';

/**
 * TabPanel component for handling tab content display
 */
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`facial-tabpanel-${index}`}
      aria-labelledby={`facial-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

/**
 * Main FacialRecognition page component.
 * This page serves as the entry point for the facial recognition module
 * and provides access to all facial recognition features through tabs.
 */
const FacialRecognition = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
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
            <PersonIcon fontSize="inherit" />
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
              Facial Recognition System
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Intelligent personnel identification and access control
            </Typography>
          </Box>
        </Box>
      </Box>

      <Paper 
        className="modern-card glass-effect" 
        elevation={0} 
        sx={{ 
          p: 0,
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
            value={activeTab} 
            onChange={handleTabChange}
            aria-label="facial recognition tabs"
            textColor="primary"
            indicatorColor="primary"
            sx={{
              '& .MuiTab-root': {
                py: 3,
                fontSize: '1rem',
                fontWeight: 600,
                minHeight: 'auto',
                '&.Mui-selected': {
                  background: 'rgba(21, 101, 192, 0.1)',
                }
              }
            }}
          >
            <Tab 
              icon={<DashboardIcon />} 
              label="Dashboard" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab 
              icon={<PersonIcon />} 
              label="Personnel Management" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab 
              icon={<LogsIcon />} 
              label="Authorization Logs" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab 
              icon={<SecurityIcon />} 
              label="Access Control" 
              iconPosition="start"
              sx={{ gap: 1 }}
            />
          </Tabs>
        </Box>
        
        <TabPanel value={activeTab} index={0}>
          <FacialDashboard />
        </TabPanel>
        <TabPanel value={activeTab} index={1}>
          <PersonnelManagement />
        </TabPanel>
        <TabPanel value={activeTab} index={2}>
          <AuthorizationLogs />
        </TabPanel>
        <TabPanel value={activeTab} index={3}>
          <AccessControl />
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default FacialRecognition;