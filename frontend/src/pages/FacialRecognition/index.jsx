import React, { useState } from 'react';
import { Box, Tab, Tabs, Typography, Paper, Grid, Container } from '@mui/material';
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
    <Container maxWidth="xl">
      <Paper elevation={3} sx={{ mt: 3, p: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Facial Recognition System
        </Typography>
        <Typography variant="body1" paragraph>
          Manage personnel, view access logs, and configure facial recognition settings.
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            aria-label="facial recognition tabs"
          >
            <Tab label="Dashboard" id="facial-tab-0" aria-controls="facial-tabpanel-0" />
            <Tab label="Personnel Management" id="facial-tab-1" aria-controls="facial-tabpanel-1" />
            <Tab label="Authorization Logs" id="facial-tab-2" aria-controls="facial-tabpanel-2" />
            <Tab label="Access Control" id="facial-tab-3" aria-controls="facial-tabpanel-3" />
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