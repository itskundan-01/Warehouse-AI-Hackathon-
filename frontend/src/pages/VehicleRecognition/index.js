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
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  ViewList as ViewListIcon,
  Visibility as VisibilityIcon,
  Check as CheckIcon,
  Block as BlockIcon,
  LocalShipping as VehicleIcon,
  TextFields as PlateIcon
} from '@mui/icons-material';

import {
  fetchVehicleRecords,
  fetchVehicleAnalytics,
  fetchUnauthorizedVehicles
} from '../../store/slices/vehicleSlice';
import vehicleService from '../../services/api/vehicleService';
import PlateDetection from '../../components/modules/PlateDetection';

// Tab panel component for tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`vehicle-tabpanel-${index}`}
      aria-labelledby={`vehicle-tab-${index}`}
      {...other}
      style={{ padding: '20px 0' }}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

const VehicleRecognitionPage = () => {
  const dispatch = useDispatch();
  const [tabValue, setTabValue] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [location, setLocation] = useState('');
  const [entryType, setEntryType] = useState('ENTRY');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [showAuthorizedOnly, setShowAuthorizedOnly] = useState(false);

  // Get state from Redux
  const { records, analytics, unauthorizedVehicles } = useSelector(state => state.vehicle);

  // Load vehicle data on component mount
  useEffect(() => {
    dispatch(fetchVehicleRecords());
    dispatch(fetchVehicleAnalytics());
    dispatch(fetchUnauthorizedVehicles());
  }, [dispatch]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
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

  // Handle detection submission
  const handleDetect = async () => {
    if (!selectedFile) {
      setError("Please select an image file");
      return;
    }
    if (!location) {
      setError("Please select a location");
      return;
    }

    setProcessing(true);
    setError(null);
    
    try {
      const response = await vehicleService.detectVehicle(selectedFile, location, entryType);
      setDetectionResult(response.data);
      // Refresh the vehicle lists after successful detection
      dispatch(fetchVehicleRecords());
      dispatch(fetchVehicleAnalytics());
      if (!response.data.is_authorized) {
        dispatch(fetchUnauthorizedVehicles());
      }
    } catch (err) {
      setError(err.message || "Failed to process vehicle detection");
    } finally {
      setProcessing(false);
    }
  };

  // Handle reset of form
  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setLocation('');
    setEntryType('ENTRY');
    setDetectionResult(null);
    setError(null);
  };

  // Handle authorization toggle
  const handleAuthorizeVehicle = async (vehicleId, authorize) => {
    try {
      await vehicleService.updateAuthorization(vehicleId, authorize);
      // Refresh the lists after successful update
      dispatch(fetchVehicleRecords());
      dispatch(fetchUnauthorizedVehicles());
      // Show success message
      alert(`Vehicle ${authorize ? 'authorized' : 'unauthorized'} successfully`);
    } catch (err) {
      console.error("Failed to update authorization:", err);
      alert("Failed to update authorization status");
    }
  };

  // Handle page change
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Filter shown vehicles by authorization status
  const filteredVehicles = showAuthorizedOnly 
    ? records.list.filter(vehicle => vehicle.is_authorized)
    : records.list;

  // Mock locations for demo (would come from API in production)
  const locationOptions = [
    { value: 'main_gate', label: 'Main Gate' },
    { value: 'side_gate', label: 'Side Gate' },
    { value: 'loading_bay', label: 'Loading Bay' },
    { value: 'parking_area', label: 'Parking Area' }
  ];

  return (
    <Container maxWidth="lg" className="fade-in">
      {/* Header Section */}
      <Box sx={{ 
        mb: 4,
        p: 4,
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%)',
        borderRadius: 3,
        backdropFilter: 'blur(15px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar sx={{ 
            bgcolor: 'transparent',
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            width: 56,
            height: 56
          }}>
            <VehicleIcon sx={{ fontSize: 28 }} />
          </Avatar>
          <Box>
            <Typography variant="h3" component="h1" sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1
            }}>
              Vehicle Recognition
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Smart vehicle tracking and authentication system
            </Typography>
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1.1rem' }}>
          Track and authenticate vehicles entering and exiting the warehouse premises using advanced license plate recognition and security protocols.
        </Typography>
      </Box>

      {/* Tabs for different sections */}
      <Paper className="modern-card" sx={{ mb: 4, overflow: 'hidden' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              py: 2,
              fontSize: '1rem',
              fontWeight: 600,
              '&.Mui-selected': {
                background: 'linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%)',
              }
            }
          }}
        >
          <Tab 
            icon={<CloudUploadIcon />} 
            label="Detect Vehicle" 
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab 
            icon={<PlateIcon />} 
            label="Plate Detection" 
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab 
            icon={<ViewListIcon />} 
            label="Vehicle Records" 
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab 
            icon={<BlockIcon />} 
            label="Unauthorized" 
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab 
            icon={<AnalyticsIcon />} 
            label="Analytics" 
            iconPosition="start"
            sx={{ gap: 1 }}
          />
        </Tabs>
      </Paper>

      {/* Detect Vehicle tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Paper className="modern-form" sx={{ height: '100%' }}>
              <Typography variant="h5" gutterBottom sx={{ 
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 3
              }}>
                <CloudUploadIcon color="primary" />
                Upload Vehicle Image
              </Typography>
              <Divider sx={{ mb: 3 }} />

              {error && (
                <Alert severity="error" className="modern-alert" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {detectionResult && (
                <Alert 
                  severity={detectionResult.is_authorized ? "success" : "warning"} 
                  className="modern-alert" 
                  sx={{ mb: 3 }}
                  icon={detectionResult.is_authorized ? <CheckIcon /> : <BlockIcon />}
                >
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {detectionResult.is_authorized 
                      ? `✅ Authorized vehicle detected: ${detectionResult.license_plate}` 
                      : `⚠️ Unauthorized vehicle detected: ${detectionResult.license_plate}`}
                  </Typography>
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

                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="entry-type-label">Entry Type</InputLabel>
                  <Select
                    labelId="entry-type-label"
                    value={entryType}
                    onChange={(e) => setEntryType(e.target.value)}
                    label="Entry Type"
                  >
                    <MenuItem value="ENTRY">Entry</MenuItem>
                    <MenuItem value="EXIT">Exit</MenuItem>
                  </Select>
                </FormControl>

                <Button
                  variant="outlined"
                  component="label"
                  fullWidth
                  startIcon={<CloudUploadIcon />}
                  sx={{ mb: 2 }}
                >
                  Select Vehicle Image
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
                    onClick={handleDetect}
                    disabled={!selectedFile || !location || processing}
                    startIcon={processing ? <CircularProgress size={20} color="inherit" /> : null}
                    fullWidth
                  >
                    {processing ? 'Processing...' : 'Detect Vehicle'}
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={handleReset}
                    disabled={processing}
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
                    alt="Selected vehicle preview" 
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

      {/* Plate Detection tab */}
      <TabPanel value={tabValue} index={1}>
        <PlateDetection />
      </TabPanel>

      {/* Vehicle Records tab */}
      <TabPanel value={tabValue} index={2}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              Vehicle Records
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={showAuthorizedOnly}
                  onChange={(e) => setShowAuthorizedOnly(e.target.checked)}
                  color="primary"
                />
              }
              label="Show Authorized Only"
            />
          </Box>
          <Divider sx={{ mb: 3 }} />

          {records.loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : records.error ? (
            <Alert severity="error">{records.error}</Alert>
          ) : filteredVehicles.length === 0 ? (
            <Typography variant="body1">No vehicle records found.</Typography>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>License Plate</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Last Seen</TableCell>
                      <TableCell>Location</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredVehicles
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((vehicle) => (
                        <TableRow key={vehicle.id}>
                          <TableCell>{vehicle.vehicle_number}</TableCell>
                          <TableCell>{vehicle.vehicle_type}</TableCell>
                          <TableCell>{new Date(vehicle.timestamp).toLocaleString()}</TableCell>
                          <TableCell>{vehicle.location}</TableCell>
                          <TableCell>
                            <Chip 
                              label={vehicle.is_authorized ? "Authorized" : "Unauthorized"} 
                              color={vehicle.is_authorized ? "success" : "error"} 
                              size="small" 
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton 
                              color="primary" 
                              size="small"
                              title="View Details"
                            >
                              <VisibilityIcon />
                            </IconButton>
                            {vehicle.is_authorized ? (
                              <IconButton 
                                color="error" 
                                size="small"
                                title="Revoke Authorization"
                                onClick={() => handleAuthorizeVehicle(vehicle.id, false)}
                              >
                                <BlockIcon />
                              </IconButton>
                            ) : (
                              <IconButton 
                                color="success" 
                                size="small"
                                title="Authorize Vehicle"
                                onClick={() => handleAuthorizeVehicle(vehicle.id, true)}
                              >
                                <CheckIcon />
                              </IconButton>
                            )}
                          </TableCell>
                        </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25]}
                component="div"
                count={filteredVehicles.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </>
          )}
        </Paper>
      </TabPanel>

      {/* Unauthorized Vehicles tab */}
      <TabPanel value={tabValue} index={3}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Unauthorized Vehicles
          </Typography>
          <Divider sx={{ mb: 3 }} />

          {unauthorizedVehicles.loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : unauthorizedVehicles.error ? (
            <Alert severity="error">{unauthorizedVehicles.error}</Alert>
          ) : unauthorizedVehicles.list.length === 0 ? (
            <Alert severity="info">No unauthorized vehicles detected.</Alert>
          ) : (
            <Grid container spacing={3}>
              {unauthorizedVehicles.list.map(vehicle => (
                <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
                  <Card sx={{ height: '100%' }}>
                    <Box 
                      sx={{ 
                        height: 140, 
                        backgroundColor: '#f5f5f5', 
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center'
                      }}
                    >
                      {vehicle.image_path ? (
                        <img 
                          src={vehicle.image_path} 
                          alt={`Vehicle ${vehicle.vehicle_number}`} 
                          style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'cover' }}
                        />
                      ) : (
                        <VehicleIcon style={{ fontSize: 60, color: '#999' }} />
                      )}
                    </Box>
                    <CardContent>
                      <Typography variant="h6" component="div" gutterBottom>
                        {vehicle.vehicle_number}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Detected at {vehicle.location} on {new Date(vehicle.timestamp).toLocaleDateString()}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        Reason: {vehicle.reason || "Not in authorized list"}
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="success" 
                        fullWidth
                        onClick={() => handleAuthorizeVehicle(vehicle.id, true)}
                      >
                        Authorize Vehicle
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Paper>
      </TabPanel>

      {/* Analytics tab */}
      <TabPanel value={tabValue} index={4}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Vehicle Analytics
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
                      Total Entries
                    </Typography>
                    <Typography variant="h3" color="primary">
                      {analytics.total_entries || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Total Exits
                    </Typography>
                    <Typography variant="h3" color="secondary">
                      {analytics.total_exits || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Vehicle Flow (Last 7 Days)
                    </Typography>
                    {/* In a real app, we would render a chart here using Chart.js or Recharts */}
                    <Box sx={{ height: 300, bgcolor: '#f5f5f5', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Typography variant="body1">
                        Vehicle flow chart would be displayed here
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Vehicle Types Distribution
                    </Typography>
                    {/* In a real app, we would render a chart here using Chart.js or Recharts */}
                    <Box sx={{ height: 300, bgcolor: '#f5f5f5', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Typography variant="body1">
                        Vehicle types distribution chart would be displayed here
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Paper>
      </TabPanel>
    </Container>
  );
};

export default VehicleRecognitionPage;