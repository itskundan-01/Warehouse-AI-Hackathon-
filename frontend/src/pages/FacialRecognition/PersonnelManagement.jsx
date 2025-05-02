import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  TextField, 
  Dialog, 
  DialogActions, 
  DialogContent, 
  DialogTitle,
  IconButton,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Avatar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  LinearProgress,
  Tooltip,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PersonAdd as PersonAddIcon,
  VpnKey as VpnKeyIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Styled components
const PersonnelGrid = styled(Grid)(({ theme }) => ({
  marginTop: theme.spacing(3),
}));

const PersonnelCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'scale(1.02)',
    boxShadow: theme.shadows[8],
  }
}));

const PersonnelAvatar = styled(Avatar)(({ theme }) => ({
  width: 96,
  height: 96,
  margin: '0 auto',
  border: `2px solid ${theme.palette.primary.main}`,
}));

const SearchBar = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(3),
}));

/**
 * Personnel Management Component
 * 
 * This component provides an interface for managing personnel in the facial recognition system.
 * It allows adding new personnel, editing existing ones, and managing access levels.
 */
const PersonnelManagement = () => {
  // State for personnel data
  const [personnel, setPersonnel] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for dialog
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('add'); // 'add' or 'edit'
  const [currentPersonnel, setCurrentPersonnel] = useState(null);
  
  // Form state
  const [employeeId, setEmployeeId] = useState('');
  const [name, setName] = useState('');
  const [department, setDepartment] = useState('');
  const [accessLevel, setAccessLevel] = useState(1);
  const [isActive, setIsActive] = useState(true);
  const [imageBase64, setImageBase64] = useState('');
  
  // Search and filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  
  // Notification state
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  // Load personnel data
  useEffect(() => {
    fetchPersonnel();
  }, []);

  const fetchPersonnel = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/v1/facial/personnel');
      const data = await response.json();
      setPersonnel(data || []);
      setError(null);
    } catch (error) {
      console.error("Failed to fetch personnel:", error);
      setError("Failed to load personnel data. Please try again.");
      // For development, use mock data
      setPersonnel([
        {
          id: '1',
          employee_id: 'EMP001',
          name: 'John Doe',
          department: 'Security',
          access_level: 3,
          is_active: true,
          last_detection: '2025-04-30T15:30:00Z'
        },
        {
          id: '2',
          employee_id: 'EMP002',
          name: 'Jane Smith',
          department: 'Operations',
          access_level: 2,
          is_active: true,
          last_detection: '2025-05-01T09:15:00Z'
        },
        {
          id: '3',
          employee_id: 'EMP003',
          name: 'Mark Johnson',
          department: 'Administration',
          access_level: 4,
          is_active: false,
          last_detection: '2025-04-15T11:20:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAddDialog = () => {
    setDialogMode('add');
    resetForm();
    setOpenDialog(true);
  };

  const handleOpenEditDialog = (person) => {
    setDialogMode('edit');
    setCurrentPersonnel(person);
    setEmployeeId(person.employee_id);
    setName(person.name);
    setDepartment(person.department);
    setAccessLevel(person.access_level);
    setIsActive(person.is_active);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    resetForm();
  };

  const resetForm = () => {
    setEmployeeId('');
    setName('');
    setDepartment('');
    setAccessLevel(1);
    setIsActive(true);
    setImageBase64('');
    setCurrentPersonnel(null);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result.split(',')[1];
      setImageBase64(base64String);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async () => {
    // Form validation
    if (!employeeId || !name) {
      setNotification({
        open: true,
        message: 'Employee ID and Name are required fields',
        severity: 'error'
      });
      return;
    }

    if (dialogMode === 'add' && !imageBase64) {
      setNotification({
        open: true,
        message: 'Face image is required for registration',
        severity: 'error'
      });
      return;
    }

    try {
      if (dialogMode === 'add') {
        // Add new personnel
        const newPersonnel = {
          employee_id: employeeId,
          name: name,
          department: department,
          access_level: accessLevel,
          face_image_base64: imageBase64
        };

        // TODO: Replace with actual API call
        // await fetch('/api/v1/facial/personnel', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(newPersonnel)
        // });

        // For development, simulate adding to state
        setPersonnel([...personnel, {
          ...newPersonnel,
          id: Date.now().toString(),
          is_active: true,
          last_detection: null
        }]);

        setNotification({
          open: true,
          message: `${name} has been successfully registered`,
          severity: 'success'
        });
      } else {
        // Edit existing personnel
        const updatedData = {
          employee_id: employeeId,
          name: name,
          department: department,
          access_level: accessLevel,
          is_active: isActive
        };

        // TODO: Replace with actual API call
        // await fetch(`/api/v1/facial/personnel/${currentPersonnel.employee_id}`, {
        //   method: 'PUT',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(updatedData)
        // });

        // For development, simulate updating state
        setPersonnel(personnel.map(p => 
          p.id === currentPersonnel.id ? {...p, ...updatedData} : p
        ));

        setNotification({
          open: true,
          message: `${name}'s information has been updated`,
          severity: 'success'
        });
      }

      handleCloseDialog();
      // After successful operation, refresh the data
      // fetchPersonnel();
    } catch (error) {
      console.error("Failed to save personnel:", error);
      setNotification({
        open: true,
        message: `Failed to ${dialogMode === 'add' ? 'register' : 'update'} personnel. Please try again.`,
        severity: 'error'
      });
    }
  };

  const handleDeletePersonnel = async (person) => {
    if (window.confirm(`Are you sure you want to delete ${person.name}?`)) {
      try {
        // TODO: Replace with actual API call
        // await fetch(`/api/v1/facial/personnel/${person.employee_id}`, {
        //   method: 'DELETE'
        // });

        // For development, simulate deletion from state
        setPersonnel(personnel.filter(p => p.id !== person.id));

        setNotification({
          open: true,
          message: `${person.name} has been removed from the system`,
          severity: 'success'
        });
      } catch (error) {
        console.error("Failed to delete personnel:", error);
        setNotification({
          open: true,
          message: `Failed to delete personnel. Please try again.`,
          severity: 'error'
        });
      }
    }
  };

  const handleToggleActive = async (person) => {
    try {
      const updatedStatus = !person.is_active;
      
      // TODO: Replace with actual API call
      // await fetch(`/api/v1/facial/personnel/${person.employee_id}/status`, {
      //   method: 'PATCH',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ is_active: updatedStatus })
      // });

      // For development, simulate updating state
      setPersonnel(personnel.map(p => 
        p.id === person.id ? {...p, is_active: updatedStatus} : p
      ));

      setNotification({
        open: true,
        message: `${person.name} is now ${updatedStatus ? 'active' : 'inactive'}`,
        severity: 'info'
      });
    } catch (error) {
      console.error("Failed to update status:", error);
      setNotification({
        open: true,
        message: `Failed to update status. Please try again.`,
        severity: 'error'
      });
    }
  };

  // Filter personnel based on search term and department filter
  const filteredPersonnel = personnel.filter(person => {
    const matchesSearch = 
      person.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) || 
      person.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = filterDepartment ? person.department === filterDepartment : true;
    
    return matchesSearch && matchesDepartment;
  });

  // Get unique departments for filter dropdown
  const departments = [...new Set(personnel.map(p => p.department).filter(Boolean))];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Personnel Management
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<PersonAddIcon />}
          onClick={handleOpenAddDialog}
        >
          Add Personnel
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <SearchBar>
          <TextField
            label="Search by Name or ID"
            variant="outlined"
            fullWidth
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ color: 'action.active', mr: 1 }} />,
            }}
          />
          <FormControl variant="outlined" sx={{ ml: 2, minWidth: 180 }}>
            <InputLabel id="department-filter-label">Department</InputLabel>
            <Select
              labelId="department-filter-label"
              id="department-filter"
              value={filterDepartment}
              onChange={(e) => setFilterDepartment(e.target.value)}
              label="Department"
            >
              <MenuItem value="">All</MenuItem>
              {departments.map((dept) => (
                <MenuItem key={dept} value={dept}>{dept}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Tooltip title="Refresh">
            <IconButton color="primary" onClick={fetchPersonnel} sx={{ ml: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </SearchBar>

        {loading ? (
          <LinearProgress sx={{ my: 2 }} />
        ) : error ? (
          <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        ) : (
          <>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Showing {filteredPersonnel.length} of {personnel.length} personnel
            </Typography>
            
            <PersonnelGrid container spacing={3}>
              {filteredPersonnel.map((person) => (
                <Grid item xs={12} sm={6} md={4} key={person.id}>
                  <PersonnelCard elevation={2}>
                    <CardContent>
                      <Box sx={{ textAlign: 'center', mb: 2 }}>
                        <PersonnelAvatar src={`/api/v1/facial/personnel/${person.employee_id}/photo`} alt={person.name}>
                          {person.name.charAt(0)}
                        </PersonnelAvatar>
                        <Typography variant="h6" sx={{ mt: 1 }}>
                          {person.name}
                        </Typography>
                        <Typography color="textSecondary" gutterBottom>
                          ID: {person.employee_id}
                        </Typography>
                        
                        <Box sx={{ mt: 1 }}>
                          <Chip 
                            label={person.is_active ? "Active" : "Inactive"} 
                            color={person.is_active ? "success" : "default"} 
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Chip 
                            label={`Level ${person.access_level}`} 
                            color="primary" 
                            size="small" 
                            icon={<VpnKeyIcon fontSize="small" />}
                          />
                        </Box>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Department:</strong> {person.department || 'N/A'}
                      </Typography>
                      
                      {person.last_detection && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Last Detected:</strong> {new Date(person.last_detection).toLocaleString()}
                        </Typography>
                      )}
                    </CardContent>
                    <CardActions sx={{ justifyContent: 'space-between', p: 2, mt: 'auto' }}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={person.is_active} 
                            onChange={() => handleToggleActive(person)}
                            color="primary"
                          />
                        }
                        label="Active"
                      />
                      <Box>
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => handleOpenEditDialog(person)}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => handleDeletePersonnel(person)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </CardActions>
                  </PersonnelCard>
                </Grid>
              ))}
              
              {filteredPersonnel.length === 0 && (
                <Grid item xs={12}>
                  <Paper sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="subtitle1" color="textSecondary">
                      No personnel found matching your criteria
                    </Typography>
                    <Button 
                      variant="outlined" 
                      sx={{ mt: 2 }}
                      startIcon={<PersonAddIcon />}
                      onClick={handleOpenAddDialog}
                    >
                      Add New Personnel
                    </Button>
                  </Paper>
                </Grid>
              )}
            </PersonnelGrid>
          </>
        )}
      </Paper>
      
      {/* Add/Edit Personnel Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'add' ? 'Add New Personnel' : `Edit Personnel: ${currentPersonnel?.name}`}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Employee ID"
                fullWidth
                required
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                disabled={dialogMode === 'edit'}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Full Name"
                fullWidth
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Department"
                fullWidth
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel id="access-level-label">Access Level</InputLabel>
                <Select
                  labelId="access-level-label"
                  value={accessLevel}
                  onChange={(e) => setAccessLevel(e.target.value)}
                  label="Access Level"
                >
                  <MenuItem value={1}>Level 1 - Basic Access</MenuItem>
                  <MenuItem value={2}>Level 2 - Extended Access</MenuItem>
                  <MenuItem value={3}>Level 3 - Supervisory Access</MenuItem>
                  <MenuItem value={4}>Level 4 - Administrative Access</MenuItem>
                  <MenuItem value={5}>Level 5 - Full Access</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {dialogMode === 'add' && (
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Face Image (Required)
                </Typography>
                <input
                  accept="image/*"
                  style={{ display: 'none' }}
                  id="face-image-upload"
                  type="file"
                  onChange={handleImageUpload}
                />
                <label htmlFor="face-image-upload">
                  <Button variant="outlined" component="span">
                    Upload Image
                  </Button>
                </label>
                {imageBase64 && (
                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <img 
                      src={`data:image/jpeg;base64,${imageBase64}`} 
                      alt="Face Preview" 
                      style={{ maxWidth: '100%', maxHeight: '200px' }} 
                    />
                  </Box>
                )}
              </Grid>
            )}
            
            {dialogMode === 'edit' && (
              <Grid item xs={12} sx={{ mt: 1 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={isActive} 
                      onChange={(e) => setIsActive(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Active"
                />
                <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                  Inactive personnel will be denied access by the facial recognition system
                </Typography>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {dialogMode === 'add' ? 'Register' : 'Save Changes'}
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

export default PersonnelManagement;