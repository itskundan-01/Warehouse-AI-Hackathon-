import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import {
  Box,
  Grid,
  Paper,
  Tabs,
  Tab,
  Typography,
  Button,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Snackbar,
  Alert,
  Skeleton,
  Divider,
  Card,
  CardHeader,
  CardContent,
  Stack,
  Switch,
  FormControlLabel,
  Pagination
} from '@mui/material';
import {
  Person as PersonIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  PhotoCamera as CameraIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

// Mock data for facial recognition (in real app, would come from API/Redux)
const mockPersonnel = [
  { 
    id: 1, 
    name: 'John Doe', 
    employeeId: 'EMP001', 
    department: 'Warehouse', 
    role: 'Manager', 
    accessLevel: 'Full Access',
    status: 'Active',
    lastDetection: '2025-05-02 10:45 AM'
  },
  { 
    id: 2, 
    name: 'Jane Smith', 
    employeeId: 'EMP002', 
    department: 'Logistics', 
    role: 'Supervisor', 
    accessLevel: 'Restricted Access',
    status: 'Active',
    lastDetection: '2025-05-02 09:15 AM'
  },
  { 
    id: 3, 
    name: 'Michael Johnson', 
    employeeId: 'EMP003', 
    department: 'Security', 
    role: 'Officer', 
    accessLevel: 'Limited Access',
    status: 'Inactive',
    lastDetection: '2025-05-01 16:30 PM'
  },
  { 
    id: 4, 
    name: 'Sarah Williams', 
    employeeId: 'EMP004', 
    department: 'Administration', 
    role: 'HR Officer', 
    accessLevel: 'Basic Access',
    status: 'Active',
    lastDetection: '2025-05-02 08:45 AM'
  },
  { 
    id: 5, 
    name: 'Robert Brown', 
    employeeId: 'EMP005', 
    department: 'Warehouse', 
    role: 'Operator', 
    accessLevel: 'Limited Access',
    status: 'Active',
    lastDetection: '2025-05-02 07:30 AM'
  }
];

const mockAccessLogs = [
  { 
    id: 1, 
    name: 'John Doe', 
    employeeId: 'EMP001',
    timestamp: '2025-05-02 10:45 AM', 
    location: 'Main Entrance', 
    status: 'Authorized',
    confidence: '98%'
  },
  { 
    id: 2, 
    name: 'Jane Smith', 
    employeeId: 'EMP002',
    timestamp: '2025-05-02 09:15 AM', 
    location: 'Office Entrance', 
    status: 'Authorized',
    confidence: '97%'
  },
  { 
    id: 3, 
    name: 'Unknown Person', 
    employeeId: 'N/A',
    timestamp: '2025-05-02 09:30 AM', 
    location: 'Loading Area', 
    status: 'Unauthorized',
    confidence: '75%'
  },
  { 
    id: 4, 
    name: 'Sarah Williams', 
    employeeId: 'EMP004',
    timestamp: '2025-05-02 08:45 AM', 
    location: 'Main Entrance', 
    status: 'Authorized',
    confidence: '96%'
  },
  { 
    id: 5, 
    name: 'Robert Brown', 
    employeeId: 'EMP005',
    timestamp: '2025-05-02 07:30 AM', 
    location: 'Warehouse Entrance', 
    status: 'Authorized',
    confidence: '95%'
  },
  { 
    id: 6, 
    name: 'Unknown Person', 
    employeeId: 'N/A',
    timestamp: '2025-05-02 06:45 AM', 
    location: 'Loading Area', 
    status: 'Unauthorized',
    confidence: '73%'
  }
];

const mockSettings = {
  detectionThreshold: 0.8,
  enableMotionDetection: true,
  enableAntispoofing: true,
  captureFormat: 'JPEG',
  recordVideoDuration: 10,
  notifyUnauthorized: true,
  retentionPeriod: 30,
  faceMatchingAlgorithm: 'ArcFace',
  maxConcurrentProcessing: 5
};

const FacialRecognition = () => {
  const dispatch = useDispatch();
  
  // State for tab control
  const [tabIndex, setTabIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [personnel, setPersonnel] = useState([]);
  const [accessLogs, setAccessLogs] = useState([]);
  const [settings, setSettings] = useState({});
  
  // State for personnel form dialog
  const [openPersonnelDialog, setOpenPersonnelDialog] = useState(false);
  const [personnelForm, setPersonnelForm] = useState({
    id: null,
    name: '',
    employeeId: '',
    department: '',
    role: '',
    accessLevel: '',
    status: 'Active'
  });
  
  // State for snackbar alerts
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  // State for search/filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  
  // Pagination state
  const [page, setPage] = useState(1);
  const rowsPerPage = 10;
  
  // Fetch data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // In a real app, these would be API calls or Redux actions
        // await dispatch(fetchPersonnel());
        // await dispatch(fetchAccessLogs());
        // await dispatch(fetchSettings());
        
        // For demo, use mock data with timeout to simulate loading
        setTimeout(() => {
          setPersonnel(mockPersonnel);
          setAccessLogs(mockAccessLogs);
          setSettings(mockSettings);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setLoading(false);
        showSnackbar('Failed to load data', 'error');
      }
    };
    
    fetchData();
  }, [dispatch]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };
  
  // Show snackbar alert
  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };
  
  // Handle snackbar close
  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  // Handle opening personnel dialog for adding/editing
  const handleOpenPersonnelDialog = (person = null) => {
    if (person) {
      setPersonnelForm({ ...person });
    } else {
      setPersonnelForm({
        id: null,
        name: '',
        employeeId: '',
        department: '',
        role: '',
        accessLevel: '',
        status: 'Active'
      });
    }
    setOpenPersonnelDialog(true);
  };
  
  // Handle personnel form submission
  const handleSubmitPersonnel = () => {
    try {
      // Validate form
      if (!personnelForm.name || !personnelForm.employeeId) {
        showSnackbar('Name and Employee ID are required', 'error');
        return;
      }
      
      // In a real app, this would be an API call or Redux action
      // const action = personnelForm.id 
      //   ? dispatch(updatePersonnel(personnelForm))
      //   : dispatch(createPersonnel(personnelForm));
      
      // Simulate API call
      setTimeout(() => {
        if (personnelForm.id) {
          // Update existing personnel
          setPersonnel(personnel.map(p => 
            p.id === personnelForm.id ? personnelForm : p
          ));
          showSnackbar('Personnel updated successfully');
        } else {
          // Add new personnel with generated ID
          const newPerson = {
            ...personnelForm,
            id: Date.now(),
            lastDetection: 'N/A'
          };
          setPersonnel([...personnel, newPerson]);
          showSnackbar('Personnel added successfully');
        }
        
        setOpenPersonnelDialog(false);
      }, 500);
    } catch (error) {
      console.error('Error saving personnel:', error);
      showSnackbar('Failed to save personnel', 'error');
    }
  };
  
  // Handle personnel deletion
  const handleDeletePersonnel = (id) => {
    try {
      // In a real app, this would be an API call or Redux action
      // await dispatch(deletePersonnel(id));
      
      // Simulate API call
      setTimeout(() => {
        setPersonnel(personnel.filter(p => p.id !== id));
        showSnackbar('Personnel deleted successfully');
      }, 500);
    } catch (error) {
      console.error('Error deleting personnel:', error);
      showSnackbar('Failed to delete personnel', 'error');
    }
  };
  
  // Handle form field changes
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setPersonnelForm({
      ...personnelForm,
      [name]: value
    });
  };
  
  // Handle settings change
  const handleSettingsChange = (setting, value) => {
    setSettings({
      ...settings,
      [setting]: value
    });
    
    // In a real app, save settings to backend
    // dispatch(updateSettings({ [setting]: value }));
    
    showSnackbar('Settings updated successfully');
  };
  
  // Filter personnel based on search term and filters
  const filteredPersonnel = personnel.filter(person => {
    const matchesSearch = 
      person.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.employeeId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.department.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesStatus = statusFilter === 'all' || person.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesDepartment = departmentFilter === 'all' || person.department === departmentFilter;
    
    return matchesSearch && matchesStatus && matchesDepartment;
  });
  
  // Get unique departments for filter
  const departments = ['all', ...new Set(personnel.map(p => p.department))];
  
  // Render loading skeletons
  if (loading) {
    return (
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
          Facial Recognition
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Skeleton variant="rectangular" width={400} height={40} />
        </Box>
        
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }
  
  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        Facial Recognition
      </Typography>
      
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs 
            value={tabIndex} 
            onChange={handleTabChange} 
            aria-label="facial recognition tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab 
              label="Personnel Management" 
              icon={<PersonIcon />} 
              iconPosition="start" 
            />
            <Tab 
              label="Authorization Logs" 
              icon={<VisibilityIcon />} 
              iconPosition="start" 
            />
            <Tab 
              label="Access Control Settings" 
              icon={<SecurityIcon />} 
              iconPosition="start" 
            />
          </Tabs>
        </Box>
        
        {/* Personnel Management Tab */}
        {tabIndex === 0 && (
          <Box>
            {/* Search and Filter Bar */}
            <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Search personnel..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel id="status-filter-label">Status</InputLabel>
                  <Select
                    labelId="status-filter-label"
                    id="status-filter"
                    value={statusFilter}
                    label="Status"
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="all">All Status</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="inactive">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel id="department-filter-label">Department</InputLabel>
                  <Select
                    labelId="department-filter-label"
                    id="department-filter"
                    value={departmentFilter}
                    label="Department"
                    onChange={(e) => setDepartmentFilter(e.target.value)}
                  >
                    {departments.map((dept) => (
                      <MenuItem key={dept} value={dept}>
                        {dept === 'all' ? 'All Departments' : dept}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => handleOpenPersonnelDialog()}
                  fullWidth
                >
                  Add Person
                </Button>
              </Grid>
            </Grid>
            
            {/* Personnel Table */}
            <TableContainer component={Paper} elevation={2}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Employee ID</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Access Level</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Last Detection</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredPersonnel.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                          No personnel found matching the current filters.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredPersonnel.map((person) => (
                      <TableRow key={person.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ mr: 1, width: 32, height: 32, backgroundColor: 'primary.main' }}>
                              {person.name.charAt(0)}
                            </Avatar>
                            {person.name}
                          </Box>
                        </TableCell>
                        <TableCell>{person.employeeId}</TableCell>
                        <TableCell>{person.department}</TableCell>
                        <TableCell>{person.role}</TableCell>
                        <TableCell>{person.accessLevel}</TableCell>
                        <TableCell>
                          <Chip
                            label={person.status}
                            color={person.status === 'Active' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{person.lastDetection}</TableCell>
                        <TableCell align="center">
                          <IconButton 
                            size="small" 
                            color="primary" 
                            onClick={() => handleOpenPersonnelDialog(person)}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="error" 
                            onClick={() => handleDeletePersonnel(person.id)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
              <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                <Pagination 
                  count={Math.ceil(filteredPersonnel.length / rowsPerPage)} 
                  page={page} 
                  onChange={(e, newPage) => setPage(newPage)}
                />
              </Box>
            </TableContainer>
          </Box>
        )}
        
        {/* Authorization Logs Tab */}
        {tabIndex === 1 && (
          <Box>
            <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Search logs..."
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value="all"
                    label="Status"
                  >
                    <MenuItem value="all">All Status</MenuItem>
                    <MenuItem value="authorized">Authorized</MenuItem>
                    <MenuItem value="unauthorized">Unauthorized</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  fullWidth
                >
                  Refresh Logs
                </Button>
              </Grid>
            </Grid>
            
            <TableContainer component={Paper} elevation={2}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Employee ID</TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {accessLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 1, width: 32, height: 32, bgcolor: log.status === 'Authorized' ? 'success.main' : 'error.main' }}>
                            {log.name.charAt(0)}
                          </Avatar>
                          {log.name}
                        </Box>
                      </TableCell>
                      <TableCell>{log.employeeId}</TableCell>
                      <TableCell>{log.timestamp}</TableCell>
                      <TableCell>{log.location}</TableCell>
                      <TableCell>
                        <Chip
                          label={log.status}
                          color={log.status === 'Authorized' ? 'success' : 'error'}
                          size="small"
                          icon={log.status === 'Authorized' ? <CheckCircleIcon fontSize="small" /> : <CancelIcon fontSize="small" />}
                        />
                      </TableCell>
                      <TableCell>{log.confidence}</TableCell>
                      <TableCell align="center">
                        <IconButton size="small">
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                <Pagination count={10} page={1} />
              </Box>
            </TableContainer>
          </Box>
        )}
        
        {/* Access Control Settings Tab */}
        {tabIndex === 2 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardHeader 
                    title="Detection Settings" 
                    avatar={<Avatar sx={{ bgcolor: 'primary.main' }}><CameraIcon /></Avatar>}
                  />
                  <Divider />
                  <CardContent>
                    <Stack spacing={3}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">Detection Threshold</Typography>
                        <TextField
                          type="number"
                          size="small"
                          value={settings.detectionThreshold}
                          onChange={(e) => handleSettingsChange('detectionThreshold', parseFloat(e.target.value))}
                          InputProps={{
                            inputProps: { 
                              min: 0.1, 
                              max: 1.0, 
                              step: 0.1 
                            }
                          }}
                          sx={{ width: '100px' }}
                        />
                      </Box>
                      
                      <Box>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.enableMotionDetection}
                              onChange={(e) => handleSettingsChange('enableMotionDetection', e.target.checked)}
                              color="primary"
                            />
                          }
                          label="Enable Motion Detection"
                        />
                      </Box>
                      
                      <Box>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.enableAntispoofing}
                              onChange={(e) => handleSettingsChange('enableAntispoofing', e.target.checked)}
                              color="primary"
                            />
                          }
                          label="Enable Anti-spoofing Protection"
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">Face Matching Algorithm</Typography>
                        <FormControl size="small" sx={{ width: '150px' }}>
                          <Select
                            value={settings.faceMatchingAlgorithm}
                            onChange={(e) => handleSettingsChange('faceMatchingAlgorithm', e.target.value)}
                          >
                            <MenuItem value="ArcFace">ArcFace</MenuItem>
                            <MenuItem value="FaceNet">FaceNet</MenuItem>
                            <MenuItem value="InsightFace">InsightFace</MenuItem>
                          </Select>
                        </FormControl>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardHeader 
                    title="Notification & Storage Settings" 
                    avatar={<Avatar sx={{ bgcolor: 'secondary.main' }}><SettingsIcon /></Avatar>}
                  />
                  <Divider />
                  <CardContent>
                    <Stack spacing={3}>
                      <Box>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.notifyUnauthorized}
                              onChange={(e) => handleSettingsChange('notifyUnauthorized', e.target.checked)}
                              color="primary"
                            />
                          }
                          label="Notify on Unauthorized Access"
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">Data Retention Period (days)</Typography>
                        <TextField
                          type="number"
                          size="small"
                          value={settings.retentionPeriod}
                          onChange={(e) => handleSettingsChange('retentionPeriod', parseInt(e.target.value))}
                          InputProps={{
                            inputProps: { 
                              min: 1, 
                              max: 365
                            }
                          }}
                          sx={{ width: '100px' }}
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">Capture Format</Typography>
                        <FormControl size="small" sx={{ width: '100px' }}>
                          <Select
                            value={settings.captureFormat}
                            onChange={(e) => handleSettingsChange('captureFormat', e.target.value)}
                          >
                            <MenuItem value="JPEG">JPEG</MenuItem>
                            <MenuItem value="PNG">PNG</MenuItem>
                          </Select>
                        </FormControl>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">Record Video Duration (seconds)</Typography>
                        <TextField
                          type="number"
                          size="small"
                          value={settings.recordVideoDuration}
                          onChange={(e) => handleSettingsChange('recordVideoDuration', parseInt(e.target.value))}
                          InputProps={{
                            inputProps: { 
                              min: 1, 
                              max: 60
                            }
                          }}
                          sx={{ width: '100px' }}
                        />
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<SecurityIcon />}
                  >
                    Save All Settings
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
      
      {/* Personnel Add/Edit Dialog */}
      <Dialog 
        open={openPersonnelDialog} 
        onClose={() => setOpenPersonnelDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {personnelForm.id ? 'Edit Personnel' : 'Add New Personnel'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                name="name"
                value={personnelForm.name}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Employee ID"
                name="employeeId"
                value={personnelForm.employeeId}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  name="department"
                  value={personnelForm.department}
                  onChange={handleFormChange}
                  label="Department"
                >
                  <MenuItem value="Administration">Administration</MenuItem>
                  <MenuItem value="Logistics">Logistics</MenuItem>
                  <MenuItem value="Warehouse">Warehouse</MenuItem>
                  <MenuItem value="Security">Security</MenuItem>
                  <MenuItem value="Management">Management</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Role"
                name="role"
                value={personnelForm.role}
                onChange={handleFormChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Access Level</InputLabel>
                <Select
                  name="accessLevel"
                  value={personnelForm.accessLevel}
                  onChange={handleFormChange}
                  label="Access Level"
                >
                  <MenuItem value="Full Access">Full Access</MenuItem>
                  <MenuItem value="Restricted Access">Restricted Access</MenuItem>
                  <MenuItem value="Limited Access">Limited Access</MenuItem>
                  <MenuItem value="Basic Access">Basic Access</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  name="status"
                  value={personnelForm.status}
                  onChange={handleFormChange}
                  label="Status"
                >
                  <MenuItem value="Active">Active</MenuItem>
                  <MenuItem value="Inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Box 
                sx={{ 
                  border: '1px dashed grey', 
                  p: 3, 
                  mt: 1, 
                  textAlign: 'center',
                  borderRadius: 1,
                  bgcolor: 'background.default'
                }}
              >
                <IconButton component="label" size="large">
                  <CameraIcon fontSize="large" />
                  <input hidden accept="image/*" type="file" />
                </IconButton>
                <Typography variant="body2" color="text.secondary">
                  Click to upload photo
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPersonnelDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmitPersonnel} variant="contained">
            {personnelForm.id ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for alerts */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FacialRecognition;