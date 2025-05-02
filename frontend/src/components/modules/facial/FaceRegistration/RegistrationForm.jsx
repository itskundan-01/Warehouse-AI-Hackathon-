import React, { useState } from 'react';
import {
  Paper,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Typography
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';

/**
 * Registration form component for adding new personnel
 */
const RegistrationForm = ({ onSubmit, loading, disabled }) => {
  const [formData, setFormData] = useState({
    employeeId: '',
    name: '',
    department: '',
    accessLevel: 1
  });

  const departments = [
    'Administration',
    'Warehouse Operations',
    'Shipping & Logistics',
    'Security',
    'Management',
    'IT',
    'Other'
  ];
  
  const accessLevels = [
    { value: 1, label: 'Level 1 - Basic Access' },
    { value: 2, label: 'Level 2 - Standard Access' },
    { value: 3, label: 'Level 3 - Extended Access' },
    { value: 4, label: 'Level 4 - Management' },
    { value: 5, label: 'Level 5 - Administrator' }
  ];
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };
  
  return (
    <Paper
      component="form"
      elevation={3}
      onSubmit={handleSubmit}
      sx={{
        p: 3,
        height: '100%'
      }}
    >
      <Typography variant="subtitle1" gutterBottom>
        Personnel Information
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            label="Employee ID"
            name="employeeId"
            value={formData.employeeId}
            onChange={handleChange}
            margin="normal"
            disabled={loading}
          />
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            required
            fullWidth
            label="Full Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            margin="normal"
            disabled={loading}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="department-label">Department</InputLabel>
            <Select
              labelId="department-label"
              name="department"
              value={formData.department}
              onChange={handleChange}
              label="Department"
              disabled={loading}
            >
              {departments.map(dept => (
                <MenuItem key={dept} value={dept}>{dept}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="access-level-label">Access Level</InputLabel>
            <Select
              labelId="access-level-label"
              name="accessLevel"
              value={formData.accessLevel}
              onChange={handleChange}
              label="Access Level"
              disabled={loading}
            >
              {accessLevels.map(level => (
                <MenuItem key={level.value} value={level.value}>
                  {level.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      <Button
        type="submit"
        variant="contained"
        color="primary"
        fullWidth
        startIcon={loading ? null : <PersonAddIcon />}
        disabled={disabled || !formData.employeeId || !formData.name}
        sx={{ mt: 3 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Register Personnel'}
      </Button>
    </Paper>
  );
};

export default RegistrationForm;