import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Tab,
  Tabs,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Assessment as AssessmentIcon,
  DirectionsCar as CarIcon,
  CreditCard as LicenseIcon
} from '@mui/icons-material';
import VideoUploadComponent from '../../components/VideoUpload/VideoUploadComponent';
import AnalysisResults from '../../components/VideoUpload/AnalysisResults';

const VehicleRecognitionVideoPage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingIds, setProcessingIds] = useState([]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleUploadComplete = (result) => {
    console.log('Upload completed:', result);
    setProcessingIds(prev => [...prev, result.processing_id]);
  };

  const handleAnalysisStart = (processingId) => {
    console.log('Analysis started:', processingId);
    pollForResults(processingId);
  };

  const pollForResults = async (processingId) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/vehicle/results/${processingId}`);
      const result = await response.json();
      
      if (result.success) {
        setAnalysisResults(prev => [result.results, ...prev]);
        setProcessingIds(prev => prev.filter(id => id !== processingId));
      }
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ mb: 4 }}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CarIcon color="primary" />
            Vehicle Recognition - Video Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Upload and analyze videos to detect vehicles and extract license plate information
          </Typography>
        </Box>

        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            label="Video Upload" 
            icon={<VideoIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Vehicle Detection" 
            icon={<AnalyticsIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="License Plates" 
            icon={<LicenseIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Reports" 
            icon={<AssessmentIcon />} 
            iconPosition="start"
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <VideoUploadComponent
            module="vehicle"
            onUploadComplete={handleUploadComplete}
            onAnalysisStart={handleAnalysisStart}
            acceptedFormats={['.mp4', '.avi', '.mov', '.mkv']}
            maxFileSize={200 * 1024 * 1024} // 200MB
          />
          
          {processingIds.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Processing Queue
                </Typography>
                <Grid container spacing={2}>
                  {processingIds.map((id) => (
                    <Grid item xs={12} sm={6} md={4} key={id}>
                      <Box 
                        sx={{ 
                          p: 2, 
                          border: 1, 
                          borderColor: 'grey.300', 
                          borderRadius: 1,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1
                        }}
                      >
                        <CircularProgress size={20} />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Processing ID:
                          </Typography>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {id}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <AnalysisResults 
            module="vehicle"
            results={analysisResults}
            loading={loading}
            processingIds={processingIds}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <AnalysisResults 
            module="vehicle"
            results={analysisResults}
            loading={loading}
            processingIds={processingIds}
            tabIndex={1} // Show Events tab by default for license plates
          />
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <AnalysisResults 
            module="vehicle"
            results={analysisResults}
            loading={loading}
            processingIds={processingIds}
            showReportsOnly={true}
          />
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default VehicleRecognitionVideoPage;
