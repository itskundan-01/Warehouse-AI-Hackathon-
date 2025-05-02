import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Switch,
  FormControlLabel,
  Slider,
  TextField,
  Divider,
  Alert,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Tooltip,
  Snackbar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress
} from '@mui/material';
import {
  Security as SecurityIcon,
  Lock as LockIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
  Save as SaveIcon,
  VerifiedUser as VerifiedUserIcon,
  AddAlert as AddAlertIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';

/**
 * Access Control Component
 * 
 * This component provides an interface for configuring facial recognition
 * security settings, authentication thresholds, and access control policies.
 */
const AccessControl = () => {
  // Security settings state
  const [securitySettings, setSecuritySettings] = useState({
    minRecognitionConfidence: 0.7,
    enableAntiSpoofing: true,
    maxAuthAttempts: 3,
    lockoutDurationMinutes: 15,
    notifyOnUnauthorized: true,
    strictModeEnabled: false,
    reAuthIntervalHours: 8,
    multiFactorAuth: false,
    autoDeleteInactiveDays: 90,
  });

  // Access schedules and locations
  const [accessSchedules, setAccessSchedules] = useState([
    { 
      id: '1', 
      name: 'Standard Working Hours', 
      startTime: '09:00', 
      endTime: '18:00', 
      days: [1, 2, 3, 4, 5], // Mon-Fri
      active: true 
    },
    { 
      id: '2', 
      name: 'Weekend Access', 
      startTime: '10:00', 
      endTime: '16:00', 
      days: [6, 0], // Sat-Sun
      active: false 
    },
    { 
      id: '3', 
      name: 'Extended Hours', 
      startTime: '07:00', 
      endTime: '22:00', 
      days: [1, 2, 3, 4, 5], // Mon-Fri
      active: false 
    }
  ]);

  const [accessLocations, setAccessLocations] = useState([
    { id: '1', name: 'Main Entrance', cameras: ['CAM-1', 'CAM-2'], requireLevel: 1, active: true },
    { id: '2', name: 'Admin Block', cameras: ['CAM-3'], requireLevel: 3, active: true },
    { id: '3', name: 'Warehouse Area', cameras: ['CAM-4', 'CAM-5'], requireLevel: 2, active: true },
    { id: '4', name: 'Server Room', cameras: ['CAM-6'], requireLevel: 4, active: true }
  ]);

  // UI state
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState(''); // 'schedule' or 'location'
  const [currentItem, setCurrentItem] = useState(null);
  
  // Form state for dialog
  const [formState, setFormState] = useState({
    name: '',
    startTime: '',
    endTime: '',
    days: [],
    requireLevel: 1,
    cameras: '',
    active: true
  });

  // Load settings from API
  useEffect(() => {
    // In a real app, fetch settings from API
    // For now, we're using the initial state
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 800);
  }, []);

  // Handle security settings changes
  const handleSettingChange = (key, value) => {
    setSecuritySettings({
      ...securitySettings,
      [key]: value
    });
  };

  // Save settings to API
  const saveSettings = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // TODO: Replace with actual API call
      // await fetch('/api/v1/facial/settings', {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(securitySettings)
      // });
      
      setNotification({
        open: true,
        message: 'Security settings saved successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error("Failed to save settings:", error);
      setNotification({
        open: true,
        message: 'Failed to save settings. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Dialog handlers
  const handleOpenDialog = (type, item = null) => {
    setDialogType(type);
    
    if (item) {
      // Edit existing item
      setCurrentItem(item);
      if (type === 'schedule') {
        setFormState({
          name: item.name,
          startTime: item.startTime,
          endTime: item.endTime,
          days: item.days,
          active: item.active
        });
      } else if (type === 'location') {
        setFormState({
          name: item.name,
          cameras: item.cameras.join(', '),
          requireLevel: item.requireLevel,
          active: item.active
        });
      }
    } else {
      // Add new item
      setCurrentItem(null);
      setFormState({
        name: '',
        startTime: '09:00',
        endTime: '17:00',
        days: [1, 2, 3, 4, 5], // Mon-Fri
        cameras: '',
        requireLevel: 1,
        active: true
      });
    }
    
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const handleFormChange = (key, value) => {
    setFormState({
      ...formState,
      [key]: value
    });
  };

  const handleSaveDialog = () => {
    if (dialogType === 'schedule') {
      if (currentItem) {
        // Update existing schedule
        setAccessSchedules(accessSchedules.map(schedule => 
          schedule.id === currentItem.id ? { ...schedule, ...formState } : schedule
        ));
      } else {
        // Add new schedule
        const newSchedule = {
          id: Date.now().toString(),
          ...formState
        };
        setAccessSchedules([...accessSchedules, newSchedule]);
      }
    } else if (dialogType === 'location') {
      // Parse cameras string into array
      const camerasArray = formState.cameras.split(',').map(cam => cam.trim()).filter(Boolean);
      
      if (currentItem) {
        // Update existing location
        setAccessLocations(accessLocations.map(location => 
          location.id === currentItem.id ? 
          { ...location, ...formState, cameras: camerasArray } : 
          location
        ));
      } else {
        // Add new location
        const newLocation = {
          id: Date.now().toString(),
          ...formState,
          cameras: camerasArray
        };
        setAccessLocations([...accessLocations, newLocation]);
      }
    }
    
    setNotification({
      open: true,
      message: `${currentItem ? 'Updated' : 'Added new'} ${dialogType} successfully`,
      severity: 'success'
    });
    
    handleCloseDialog();
  };

  // Delete item
  const handleDelete = (type, item) => {
    if (window.confirm(`Are you sure you want to delete this ${type}?`)) {
      if (type === 'schedule') {
        setAccessSchedules(accessSchedules.filter(schedule => schedule.id !== item.id));
      } else if (type === 'location') {
        setAccessLocations(accessLocations.filter(location => location.id !== item.id));
      }
      
      setNotification({
        open: true,
        message: `${type.charAt(0).toUpperCase() + type.slice(1)} deleted successfully`,
        severity: 'success'
      });
    }
  };

  // Toggle active status
  const handleToggleActive = (type, item) => {
    if (type === 'schedule') {
      setAccessSchedules(accessSchedules.map(schedule => 
        schedule.id === item.id ? { ...schedule, active: !schedule.active } : schedule
      ));
    } else if (type === 'location') {
      setAccessLocations(accessLocations.map(location => 
        location.id === item.id ? { ...location, active: !location.active } : location
      ));
    }
  };

  // Format day names from day numbers
  const formatDays = (days) => {
    const dayNames = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
    return days.map(day => dayNames[day]).join(', ');
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        <SecurityIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
        Access Control Settings
      </Typography>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      <Grid container spacing={3}>
        {/* Security Settings Card */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                Security Settings
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Recognition Confidence Threshold: {(securitySettings.minRecognitionConfidence * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={securitySettings.minRecognitionConfidence}
                  onChange={(e, value) => handleSettingChange('minRecognitionConfidence', value)}
                  step={0.05}
                  marks={[
                    { value: 0.5, label: '50%' },
                    { value: 0.7, label: '70%' },
                    { value: 0.9, label: '90%' }
                  ]}
                  min={0.5}
                  max={0.95}
                />
                <Typography variant="body2" color="text.secondary">
                  Minimum confidence score required for face recognition. Higher values are more strict.
                </Typography>
              </Box>
              
              <Box sx={{ mt: 3 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={securitySettings.enableAntiSpoofing}
                      onChange={(e) => handleSettingChange('enableAntiSpoofing', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Enable Anti-Spoofing Protection"
                />
                <Typography variant="body2" color="text.secondary">
                  Detect and prevent presentation attacks (photos, masks, videos)
                </Typography>
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Failed Authentication Limits
                </Typography>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={6}>
                    <TextField
                      label="Max Attempts"
                      type="number"
                      value={securitySettings.maxAuthAttempts}
                      onChange={(e) => handleSettingChange('maxAuthAttempts', parseInt(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 1, max: 10 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Lockout (minutes)"
                      type="number"
                      value={securitySettings.lockoutDurationMinutes}
                      onChange={(e) => handleSettingChange('lockoutDurationMinutes', parseInt(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 5, max: 60 }}
                    />
                  </Grid>
                </Grid>
              </Box>
              
              <Box sx={{ mt: 3 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={securitySettings.notifyOnUnauthorized}
                      onChange={(e) => handleSettingChange('notifyOnUnauthorized', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Send Notification on Unauthorized Access"
                />
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Re-Authentication Interval (Hours)
                </Typography>
                <Slider
                  value={securitySettings.reAuthIntervalHours}
                  onChange={(e, value) => handleSettingChange('reAuthIntervalHours', value)}
                  step={1}
                  marks={[
                    { value: 4, label: '4h' },
                    { value: 8, label: '8h' },
                    { value: 12, label: '12h' },
                    { value: 24, label: '24h' }
                  ]}
                  min={1}
                  max={24}
                />
                <Typography variant="body2" color="text.secondary">
                  How frequently personnel must re-authenticate
                </Typography>
              </Box>
              
              <Box sx={{ mt: 3 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={securitySettings.strictModeEnabled}
                      onChange={(e) => handleSettingChange('strictModeEnabled', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Enable Strict Mode"
                />
                <Typography variant="body2" color="text.secondary">
                  Enforces additional security checks and more stringent access control
                </Typography>
              </Box>
              
              <Box sx={{ mt: 3 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={securitySettings.multiFactorAuth}
                      onChange={(e) => handleSettingChange('multiFactorAuth', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Require Multi-Factor Authentication"
                />
                <Typography variant="body2" color="text.secondary">
                  Require additional verification for higher access levels
                </Typography>
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Auto-Delete Inactive Personnel (Days)
                </Typography>
                <TextField
                  type="number"
                  value={securitySettings.autoDeleteInactiveDays}
                  onChange={(e) => handleSettingChange('autoDeleteInactiveDays', parseInt(e.target.value))}
                  fullWidth
                  size="small"
                  inputProps={{ min: 30, max: 365 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Automatically deactivate personnel after specified days of inactivity (0 to disable)
                </Typography>
              </Box>
            </CardContent>
            <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<SaveIcon />}
                onClick={saveSettings}
                disabled={loading}
              >
                Save Security Settings
              </Button>
            </CardActions>
          </Card>
        </Grid>
        
        {/* Access Schedules Card */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" color="primary" gutterBottom>
                  Access Schedules
                </Typography>
                <Button 
                  variant="outlined" 
                  size="small" 
                  onClick={() => handleOpenDialog('schedule')}
                >
                  Add Schedule
                </Button>
              </Box>
              
              <List>
                {accessSchedules.map((schedule) => (
                  <React.Fragment key={schedule.id}>
                    <ListItem
                      secondaryAction={
                        <Box>
                          <Tooltip title="Edit">
                            <IconButton edge="end" onClick={() => handleOpenDialog('schedule', schedule)}>
                              <SettingsIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton edge="end" onClick={() => handleDelete('schedule', schedule)}>
                              <WarningIcon fontSize="small" color="error" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      }
                    >
                      <ListItemIcon>
                        <AccessTimeIcon color={schedule.active ? 'primary' : 'disabled'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {schedule.name}
                            {!schedule.active && (
                              <Chip 
                                label="Inactive" 
                                size="small" 
                                sx={{ ml: 1 }} 
                                variant="outlined"
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography variant="body2" component="span">
                              {schedule.startTime} - {schedule.endTime} ({formatDays(schedule.days)})
                            </Typography>
                            <FormControlLabel
                              control={
                                <Switch 
                                  size="small"
                                  checked={schedule.active}
                                  onChange={() => handleToggleActive('schedule', schedule)}
                                />
                              }
                              label={schedule.active ? "Active" : "Inactive"}
                              sx={{ ml: 2 }}
                            />
                          </>
                        }
                      />
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
                
                {accessSchedules.length === 0 && (
                  <ListItem>
                    <ListItemText 
                      primary="No schedules defined" 
                      secondary="Click 'Add Schedule' to create an access schedule"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
          
          {/* Access Locations Card */}
          <Card elevation={2} sx={{ mt: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" color="primary" gutterBottom>
                  Access Locations
                </Typography>
                <Button 
                  variant="outlined" 
                  size="small" 
                  onClick={() => handleOpenDialog('location')}
                >
                  Add Location
                </Button>
              </Box>
              
              <List>
                {accessLocations.map((location) => (
                  <React.Fragment key={location.id}>
                    <ListItem
                      secondaryAction={
                        <Box>
                          <Tooltip title="Edit">
                            <IconButton edge="end" onClick={() => handleOpenDialog('location', location)}>
                              <SettingsIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton edge="end" onClick={() => handleDelete('location', location)}>
                              <WarningIcon fontSize="small" color="error" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      }
                    >
                      <ListItemIcon>
                        <LockIcon color={location.active ? 'primary' : 'disabled'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {location.name}
                            {!location.active && (
                              <Chip 
                                label="Inactive" 
                                size="small" 
                                sx={{ ml: 1 }} 
                                variant="outlined"
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography variant="body2" component="span">
                              Cameras: {location.cameras.join(', ')} | Level {location.requireLevel}+ required
                            </Typography>
                            <FormControlLabel
                              control={
                                <Switch 
                                  size="small"
                                  checked={location.active}
                                  onChange={() => handleToggleActive('location', location)}
                                />
                              }
                              label={location.active ? "Active" : "Inactive"}
                              sx={{ ml: 2 }}
                            />
                          </>
                        }
                      />
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
                
                {accessLocations.length === 0 && (
                  <ListItem>
                    <ListItemText 
                      primary="No locations defined" 
                      secondary="Click 'Add Location' to create an access location"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Dialog for adding/editing schedules or locations */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {currentItem 
            ? `Edit ${dialogType === 'schedule' ? 'Schedule' : 'Location'}`
            : `Add New ${dialogType === 'schedule' ? 'Schedule' : 'Location'}`
          }
        </DialogTitle>
        <DialogContent>
          {dialogType === 'schedule' ? (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <TextField
                  label="Schedule Name"
                  fullWidth
                  value={formState.name}
                  onChange={(e) => handleFormChange('name', e.target.value)}
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Start Time"
                  type="time"
                  fullWidth
                  value={formState.startTime}
                  onChange={(e) => handleFormChange('startTime', e.target.value)}
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                  inputProps={{ step: 300 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="End Time"
                  type="time"
                  fullWidth
                  value={formState.endTime}
                  onChange={(e) => handleFormChange('endTime', e.target.value)}
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                  inputProps={{ step: 300 }}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="days-select-label">Days of Week</InputLabel>
                  <Select
                    labelId="days-select-label"
                    multiple
                    value={formState.days}
                    onChange={(e) => handleFormChange('days', e.target.value)}
                    renderValue={(selected) => formatDays(selected)}
                    label="Days of Week"
                  >
                    <MenuItem value={0}>Sunday</MenuItem>
                    <MenuItem value={1}>Monday</MenuItem>
                    <MenuItem value={2}>Tuesday</MenuItem>
                    <MenuItem value={3}>Wednesday</MenuItem>
                    <MenuItem value={4}>Thursday</MenuItem>
                    <MenuItem value={5}>Friday</MenuItem>
                    <MenuItem value={6}>Saturday</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={formState.active}
                      onChange={(e) => handleFormChange('active', e.target.checked)}
                    />
                  }
                  label="Active"
                />
              </Grid>
            </Grid>
          ) : (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <TextField
                  label="Location Name"
                  fullWidth
                  value={formState.name}
                  onChange={(e) => handleFormChange('name', e.target.value)}
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Cameras (comma-separated)"
                  fullWidth
                  value={formState.cameras}
                  onChange={(e) => handleFormChange('cameras', e.target.value)}
                  margin="normal"
                  helperText="Example: CAM-1, CAM-2"
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="access-level-label">Required Access Level</InputLabel>
                  <Select
                    labelId="access-level-label"
                    value={formState.requireLevel}
                    onChange={(e) => handleFormChange('requireLevel', e.target.value)}
                    label="Required Access Level"
                  >
                    <MenuItem value={1}>Level 1 - Basic Access</MenuItem>
                    <MenuItem value={2}>Level 2 - Extended Access</MenuItem>
                    <MenuItem value={3}>Level 3 - Supervisory Access</MenuItem>
                    <MenuItem value={4}>Level 4 - Administrative Access</MenuItem>
                    <MenuItem value={5}>Level 5 - Full Access</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={formState.active}
                      onChange={(e) => handleFormChange('active', e.target.checked)}
                    />
                  }
                  label="Active"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSaveDialog} 
            variant="contained" 
            color="primary"
            disabled={
              !formState.name || 
              (dialogType === 'schedule' && (!formState.startTime || !formState.endTime || formState.days.length === 0)) ||
              (dialogType === 'location' && !formState.cameras)
            }
          >
            {currentItem ? 'Save Changes' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Notification Snackbar */}
      <Snackbar 
        open={notification.open} 
        autoHideDuration={6000} 
        onClose={() => setNotification({...notification, open: false})}
      >
        <Alert 
          onClose={() => setNotification({...notification, open: false})} 
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AccessControl;