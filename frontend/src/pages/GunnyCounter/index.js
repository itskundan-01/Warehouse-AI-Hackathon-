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
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip
} from '@mui/material';
import { 
  CloudUpload as CloudUploadIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  ViewList as ViewListIcon,
  FilterList as FilterListIcon,
  Download as DownloadIcon,
  VisibilityOutlined as ViewIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

import { fetchGunnyBagCounts, fetchGunnyAnalytics } from '../../store/slices/gunnySlice';
import { addAlert } from '../../store/slices/uiSlice';
import gunnyService from '../../services/api/gunnyService';

// Tab panel component for tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`gunny-tabpanel-${index}`}
      aria-labelledby={`gunny-tab-${index}`}
      {...other}
      style={{ padding: '20px 0' }}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

// Colors for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const GunnyCounterPage = () => {
  const dispatch = useDispatch();
  const [tabValue, setTabValue] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [location, setLocation] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [counting, setCounting] = useState(false);
  const [countResult, setCountResult] = useState(null);
  const [error, setError] = useState(null);
  
  // State for history tab
  const [historyFilters, setHistoryFilters] = useState({
    startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days ago
    endDate: new Date().toISOString().split('T')[0], // today
    location: '',
    page: 0,
    rowsPerPage: 10
  });
  const [historyData, setHistoryData] = useState({
    loading: false,
    error: null,
    data: [],
    total: 0
  });

  // Get state from Redux
  const { counts, analytics } = useSelector(state => state.gunny);
  const { apiError } = useSelector(state => state.ui);

  // Load counts and analytics on component mount
  useEffect(() => {
    dispatch(fetchGunnyBagCounts());
    dispatch(fetchGunnyAnalytics());
  }, [dispatch]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    // Load history data when switching to history tab
    if (newValue === 3 && historyData.data.length === 0 && !historyData.loading) {
      loadHistoricalData();
    }
  };

  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.match('image.*')) {
        setError("Please select an image file");
        return;
      }
      
      setSelectedFile(file);
      // Create a preview URL for the image
      const fileReader = new FileReader();
      fileReader.onload = () => {
        setPreviewUrl(fileReader.result);
      };
      fileReader.readAsDataURL(file);
      setError(null); // Clear any previous errors
    }
  };

  // Handle counting submission
  const handleCount = async () => {
    if (!selectedFile) {
      setError("Please select an image file");
      return;
    }
    if (!location) {
      setError("Please select a location");
      return;
    }

    setCounting(true);
    setError(null);
    
    try {
      const response = await gunnyService.countBags(selectedFile, location);
      setCountResult(response.data);
      
      // Show success notification
      dispatch(addAlert({
        type: 'success',
        message: `Successfully counted ${response.data.bag_count} gunny bags`,
        autoHide: true
      }));
      
      // Refresh the counts list after successful submission
      dispatch(fetchGunnyBagCounts());
      dispatch(fetchGunnyAnalytics());
    } catch (err) {
      console.error("Gunny count error:", err);
      setError(err.response?.data?.message || err.message || "Failed to process gunny bag count");
    } finally {
      setCounting(false);
    }
  };

  // Handle reset of form
  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setLocation('');
    setCountResult(null);
    setError(null);
  };

  // Handle filters change in history tab
  const handleHistoryFilterChange = (field, value) => {
    setHistoryFilters({
      ...historyFilters,
      [field]: value,
      page: field !== 'page' && field !== 'rowsPerPage' ? 0 : historyFilters.page // Reset page when filters change
    });
    
    // Load data with new filters if not changing page/rowsPerPage (those have their own handlers)
    if (field !== 'page' && field !== 'rowsPerPage') {
      setTimeout(() => loadHistoricalData({
        ...historyFilters,
        [field]: value,
        page: 0
      }), 0);
    }
  };

  // Handle pagination change
  const handleChangePage = (event, newPage) => {
    handleHistoryFilterChange('page', newPage);
    loadHistoricalData({
      ...historyFilters,
      page: newPage
    });
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    handleHistoryFilterChange('rowsPerPage', newRowsPerPage);
    handleHistoryFilterChange('page', 0);
    loadHistoricalData({
      ...historyFilters,
      rowsPerPage: newRowsPerPage,
      page: 0
    });
  };

  // Load historical data from API with current filters
  const loadHistoricalData = async (filters = historyFilters) => {
    setHistoryData({
      ...historyData,
      loading: true,
      error: null
    });
    
    try {
      const response = await gunnyService.getCounts({
        location: filters.location || undefined,
        startDate: filters.startDate,
        endDate: filters.endDate,
        page: filters.page + 1, // API uses 1-based pagination
        limit: filters.rowsPerPage
      });
      
      setHistoryData({
        loading: false,
        error: null,
        data: response.data.data || [],
        total: response.data.total || 0
      });
    } catch (err) {
      console.error("Failed to load historical data:", err);
      setHistoryData({
        ...historyData,
        loading: false,
        error: err.message || "Failed to load historical data"
      });
    }
  };

  // Export historical data as CSV
  const handleExportCSV = () => {
    // Generate CSV content
    const headers = ['ID', 'Count', 'Location', 'Timestamp', 'Confidence Score'];
    
    const csvContent = [
      headers.join(','),
      ...historyData.data.map(row => [
        row.id,
        row.count,
        row.location,
        new Date(row.timestamp).toLocaleString(),
        row.confidence_score
      ].join(','))
    ].join('\n');
    
    // Create a blob and download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `gunny_counts_export_${new Date().toISOString().slice(0, 10)}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Location options for form selects
  const locationOptions = [
    { value: 'warehouse_a', label: 'Warehouse A' },
    { value: 'warehouse_b', label: 'Warehouse B' },
    { value: 'loading_dock', label: 'Loading Dock' },
    { value: 'storage_area', label: 'Storage Area' }
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gunny Bag Counter
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" paragraph>
          Upload images to count gunny bags, view historical counts, and analyze trends over time.
        </Typography>
      </Box>

      {/* Display API errors if any */}
      {apiError && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {apiError.message}
        </Alert>
      )}

      {/* Tabs for different sections */}
      <Paper sx={{ mb: 4 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab icon={<CloudUploadIcon />} label="Count Bags" />
          <Tab icon={<ViewListIcon />} label="Recent Counts" />
          <Tab icon={<AnalyticsIcon />} label="Analytics" />
          <Tab icon={<HistoryIcon />} label="History" />
        </Tabs>
      </Paper>

      {/* Count Bags tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Upload Image
              </Typography>
              <Divider sx={{ mb: 3 }} />

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {countResult && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  <Typography variant="body1" fontWeight="bold">
                    Counted {countResult.bag_count} gunny bags
                  </Typography>
                  <Typography variant="body2">
                    Confidence: {Math.round(countResult.confidence_score * 100)}%
                  </Typography>
                  {countResult.image_url && (
                    <Box sx={{ mt: 1 }}>
                      <Button 
                        size="small" 
                        variant="outlined" 
                        startIcon={<ViewIcon />}
                        href={countResult.image_url} 
                        target="_blank"
                      >
                        View Processed Image
                      </Button>
                    </Box>
                  )}
                </Alert>
              )}

              <Box sx={{ mb: 3 }}>
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="location-label">Location</InputLabel>
                  <Select
                    labelId="location-label"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    label="Location"
                  >
                    <MenuItem value="">
                      <em>Select a location</em>
                    </MenuItem>
                    {locationOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Button
                  variant="outlined"
                  component="label"
                  fullWidth
                  startIcon={<CloudUploadIcon />}
                  sx={{ mb: 2 }}
                >
                  Select Image
                  <input
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={handleFileChange}
                  />
                </Button>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedFile ? `Selected file: ${selectedFile.name}` : 'No file selected'}
                </Typography>

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleCount}
                    disabled={!selectedFile || !location || counting}
                    startIcon={counting ? <CircularProgress size={20} color="inherit" /> : null}
                    fullWidth
                  >
                    {counting ? 'Processing...' : 'Count Gunny Bags'}
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={handleReset}
                    disabled={counting}
                    fullWidth
                  >
                    Reset
                  </Button>
                </Box>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                Image Preview
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Box 
                sx={{ 
                  flex: 1, 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  backgroundColor: '#f5f5f5',
                  borderRadius: 1,
                  overflow: 'hidden'
                }}
              >
                {previewUrl ? (
                  <img 
                    src={previewUrl} 
                    alt="Selected file preview" 
                    style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} 
                  />
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No image selected for preview
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Recent Counts tab */}
      <TabPanel value={tabValue} index={1}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Counts
          </Typography>
          <Divider sx={{ mb: 3 }} />

          {counts.loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : counts.error ? (
            <Alert severity="error">{counts.error}</Alert>
          ) : counts.list.length === 0 ? (
            <Typography variant="body1">No recent counts found.</Typography>
          ) : (
            <Grid container spacing={3}>
              {counts.list.slice(0, 6).map(count => (
                <Grid item xs={12} sm={6} md={4} key={count.id}>
                  <Card sx={{ height: '100%', transition: 'all 0.2s ease', '&:hover': { transform: 'translateY(-5px)', boxShadow: 3 } }}>
                    {count.processed_image_url && (
                      <Box sx={{ position: 'relative' }}>
                        <img 
                          src={count.processed_image_url} 
                          alt={`Gunny count at ${count.location}`}
                          style={{ width: '100%', height: '140px', objectFit: 'cover' }}
                        />
                        <Box 
                          sx={{ 
                            position: 'absolute', 
                            bottom: 0, 
                            right: 0, 
                            bgcolor: 'rgba(0,0,0,0.6)', 
                            color: 'white', 
                            p: 1,
                            borderTopLeftRadius: 4
                          }}
                        >
                          <Typography variant="h6" component="span">
                            {count.count} bags
                          </Typography>
                        </Box>
                      </Box>
                    )}
                    <CardContent>
                      {!count.processed_image_url && (
                        <Typography variant="h5" component="div">
                          {count.count} bags
                        </Typography>
                      )}
                      <Typography color="text.secondary">
                        {locationOptions.find(loc => loc.value === count.location)?.label || count.location}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1.5 }} color="text.secondary">
                        {new Date(count.timestamp).toLocaleString()}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Chip
                          label={`${Math.round(count.confidence_score * 100)}% confidence`}
                          color={
                            count.confidence_score > 0.9 ? 'success' :
                            count.confidence_score > 0.7 ? 'primary' : 'warning'
                          }
                          size="small"
                        />
                        <Button 
                          size="small" 
                          endIcon={<ViewIcon />}
                          onClick={() => {
                            // In a real application, would navigate to detailed view
                            console.log('View details for', count.id);
                          }}
                        >
                          Details
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
          
          {counts.list.length > 0 && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button 
                variant="outlined" 
                endIcon={<HistoryIcon />}
                onClick={() => setTabValue(3)} // Switch to History tab
              >
                View All History
              </Button>
            </Box>
          )}
        </Paper>
      </TabPanel>

      {/* Analytics tab */}
      <TabPanel value={tabValue} index={2}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Analytics
          </Typography>
          <Divider sx={{ mb: 3 }} />

          {analytics.loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : analytics.error ? (
            <Alert severity="error">{analytics.error}</Alert>
          ) : (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Total Gunny Bags
                    </Typography>
                    <Typography variant="h3" color="primary">
                      {analytics.total_count || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Average Confidence
                    </Typography>
                    <Typography variant="h3" color="secondary">
                      {analytics.average_confidence 
                        ? `${Math.round(analytics.average_confidence * 100)}%` 
                        : 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Daily Counts
                    </Typography>
                    <Box sx={{ height: 300, mt: 2 }}>
                      {analytics.daily_counts ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={analytics.daily_counts}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line 
                              type="monotone" 
                              dataKey="count" 
                              stroke="#8884d8" 
                              activeDot={{ r: 8 }} 
                              name="Bags Counted"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      ) : (
                        <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Typography variant="body1" color="text.secondary">
                            No daily count data available
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Location Distribution
                    </Typography>
                    <Box sx={{ height: 300, mt: 2 }}>
                      {analytics.location_distribution ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={analytics.location_distribution}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                              outerRadius={80}
                              fill="#8884d8"
                              dataKey="count"
                              nameKey="location"
                            >
                              {analytics.location_distribution.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip formatter={(value) => [`${value} bags`, 'Count']} />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      ) : (
                        <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Typography variant="body1" color="text.secondary">
                            No location distribution data available
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Paper>
      </TabPanel>

      {/* History tab */}
      <TabPanel value={tabValue} index={3}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Historical Data
          </Typography>
          <Divider sx={{ mb: 3 }} />
          
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Start Date"
                  type="date"
                  value={historyFilters.startDate}
                  onChange={(e) => handleHistoryFilterChange('startDate', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="End Date"
                  type="date"
                  value={historyFilters.endDate}
                  onChange={(e) => handleHistoryFilterChange('endDate', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel id="location-filter-label">Location</InputLabel>
                  <Select
                    labelId="location-filter-label"
                    label="Location"
                    value={historyFilters.location}
                    onChange={(e) => handleHistoryFilterChange('location', e.target.value)}
                  >
                    <MenuItem value="">All Locations</MenuItem>
                    {locationOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
          
          {historyData.error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {historyData.error}
            </Alert>
          )}
          
          {historyData.loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                  disabled={historyData.data.length === 0}
                  sx={{ mr: 2 }}
                >
                  Export CSV
                </Button>
                <Button 
                  variant="outlined"
                  startIcon={<FilterListIcon />}
                  onClick={() => loadHistoricalData()}
                >
                  Apply Filters
                </Button>
              </Box>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Count</TableCell>
                      <TableCell>Location</TableCell>
                      <TableCell>Date & Time</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {historyData.data.length > 0 ? (
                      historyData.data.map((row) => (
                        <TableRow key={row.id}>
                          <TableCell>
                            <Typography variant="body1" fontWeight="medium">
                              {row.count} bags
                            </Typography>
                          </TableCell>
                          <TableCell>{
                            locationOptions.find(loc => loc.value === row.location)?.label || row.location
                          }</TableCell>
                          <TableCell>{new Date(row.timestamp).toLocaleString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={`${Math.round(row.confidence_score * 100)}%`}
                              color={
                                row.confidence_score > 0.9 ? 'success' :
                                row.confidence_score > 0.7 ? 'primary' : 'warning'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Button 
                              size="small" 
                              variant="text"
                              endIcon={<ViewIcon />}
                              onClick={() => {
                                // In a real application, would navigate to detailed view
                                console.log('View details for', row.id);
                              }}
                            >
                              Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                            No records found matching your filters
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={historyData.total}
                rowsPerPage={historyFilters.rowsPerPage}
                page={historyFilters.page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </>
          )}
        </Paper>
      </TabPanel>
    </Container>
  );
};

export default GunnyCounterPage;