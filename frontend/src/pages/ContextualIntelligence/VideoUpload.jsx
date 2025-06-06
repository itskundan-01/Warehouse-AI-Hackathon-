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
  Avatar,
  TextField,
  Button,
  Divider
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Assessment as AssessmentIcon,
  Psychology as BrainIcon,
  Event as EventIcon,
  Search as SearchIcon,
  QueryStats as QueryIcon
} from '@mui/icons-material';
import VideoUploadComponent from '../../components/VideoUpload/VideoUploadComponent';
import AnalysisResults from '../../components/VideoUpload/AnalysisResults';

const ContextualIntelligenceVideoPage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingIds, setProcessingIds] = useState([]);
  const [query, setQuery] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [queryLoading, setQueryLoading] = useState(false);

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
      const response = await fetch(`http://localhost:8000/api/contextual/results/${processingId}`);
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

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    setQueryLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/contextual/query?query=${encodeURIComponent(query)}`);
      const result = await response.json();
      setQueryResults(result);
    } catch (error) {
      console.error('Error processing query:', error);
    } finally {
      setQueryLoading(false);
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
            <BrainIcon color="primary" />
            Contextual Intelligence - Video Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Upload and analyze videos for contextual understanding, event detection, and intelligent querying
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
            label="Analysis Results" 
            icon={<AnalyticsIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Event Detection" 
            icon={<EventIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Query System" 
            icon={<QueryIcon />} 
            iconPosition="start"
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <VideoUploadComponent
            module="contextual"
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
            module="contextual"
            results={analysisResults}
            loading={loading}
            processingIds={processingIds}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <AnalysisResults 
            module="contextual"
            results={analysisResults}
            loading={loading}
            processingIds={processingIds}
            tabIndex={1} // Show Events tab by default
          />
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Natural Language Query System
          </Typography>
          
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="body1" gutterBottom>
                Ask questions about your video analysis in natural language:
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <TextField
                  fullWidth
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., How many people were detected? When was motion detected?"
                  variant="outlined"
                  onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                />
                <Button
                  variant="contained"
                  onClick={handleQuery}
                  disabled={!query.trim() || queryLoading}
                  startIcon={queryLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                >
                  Query
                </Button>
              </Box>
            </CardContent>
          </Card>

          {queryResults && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Query Results
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Query: "{queryResults.query}"
                </Typography>
                
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {queryResults.message}
                </Typography>

                {queryResults.processed_query && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Processed Query:
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                      {JSON.stringify(queryResults.processed_query, null, 2)}
                    </Typography>
                  </Box>
                )}

                {queryResults.results && queryResults.results.length > 0 && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Found {queryResults.results_count} results:
                    </Typography>
                    <List>
                      {queryResults.results.slice(0, 3).map((result, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={result.type || 'Event'}
                            secondary={result.description || result.message}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              <strong>Example queries:</strong>
            </Typography>
            <Box sx={{ mt: 1 }}>
              {[
                "How much motion was detected in the video?",
                "What objects were found?",
                "Show me any security events",
                "When did people appear in the video?",
                "What was the lighting like?"
              ].map((example, index) => (
                <Chip
                  key={index}
                  label={example}
                  onClick={() => setQuery(example)}
                  sx={{ m: 0.5 }}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default ContextualIntelligenceVideoPage;
