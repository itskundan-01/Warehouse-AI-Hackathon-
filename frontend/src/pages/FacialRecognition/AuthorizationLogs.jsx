import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Stack,
  Button,
  IconButton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Tooltip
} from '@mui/material';
import { 
  CheckCircle as CheckCircleIcon, 
  Cancel as CancelIcon, 
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Event as EventIcon
} from '@mui/icons-material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DateTimePicker } from '@mui/x-date-pickers';

/**
 * Authorization Logs Component
 * 
 * This component displays the logs of facial recognition authentication attempts,
 * including both successful and failed attempts. It provides filtering and
 * pagination capabilities.
 */
const AuthorizationLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Filter state
  const [filters, setFilters] = useState({
    employeeId: '',
    location: '',
    startDate: null,
    endDate: null,
    status: 'all', // 'all', 'authorized', 'unauthorized'
  });

  // Stats
  const [stats, setStats] = useState({
    authorized: 0,
    unauthorized: 0,
    totalEvents: 0,
    lastEvent: null
  });

  // Fetch logs on component mount
  useEffect(() => {
    fetchAuthLogs();
  }, []);

  // Update filtered logs when filters or logs change
  useEffect(() => {
    applyFilters();
  }, [logs, filters]);

  // Fetch authentication logs from API
  const fetchAuthLogs = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/facial/history');
      // const data = await response.json();
      // setLogs(data || []);
      
      // Mock data for development
      const mockData = generateMockLogs(50);
      setLogs(mockData);
      
      // Calculate stats
      calculateStats(mockData);
      setError(null);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      setError('Failed to load authorization logs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Generate mock logs for development
  const generateMockLogs = (count) => {
    const locations = ['Main Entrance', 'East Wing', 'Admin Block', 'West Wing'];
    const personnel = [
      { id: 'EMP001', name: 'John Doe' },
      { id: 'EMP002', name: 'Jane Smith' },
      { id: 'EMP003', name: 'Mark Johnson' },
      { id: null, name: 'Unknown Person' }
    ];
    
    const logs = [];
    const now = new Date();
    
    for (let i = 0; i < count; i++) {
      const timeOffset = Math.floor(Math.random() * 14 * 24 * 60 * 60 * 1000); // Up to 14 days
      const timestamp = new Date(now.getTime() - timeOffset);
      const personIndex = Math.floor(Math.random() * personnel.length);
      const person = personnel[personIndex];
      const isAuthorized = person.id !== null && Math.random() > 0.3; // 70% success rate for known personnel
      
      logs.push({
        id: `log-${i}`,
        timestamp: timestamp.toISOString(),
        personnel_id: person.id,
        name: person.name,
        location: locations[Math.floor(Math.random() * locations.length)],
        camera_id: `CAM-${Math.floor(Math.random() * 5) + 1}`,
        is_authorized: isAuthorized,
        confidence_score: isAuthorized ? 
          (0.7 + Math.random() * 0.3) : // 0.7 to 1.0 for authorized
          (0.3 + Math.random() * 0.4)   // 0.3 to 0.7 for unauthorized
      });
    }
    
    // Sort logs by timestamp in descending order
    return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  // Calculate statistics from logs
  const calculateStats = (logsData) => {
    const authorized = logsData.filter(log => log.is_authorized).length;
    const unauthorized = logsData.filter(log => !log.is_authorized).length;
    
    // Find the most recent event
    let lastEvent = null;
    if (logsData.length > 0) {
      lastEvent = logsData.reduce((latest, current) => {
        const latestDate = new Date(latest.timestamp);
        const currentDate = new Date(current.timestamp);
        return currentDate > latestDate ? current : latest;
      });
    }
    
    setStats({
      authorized,
      unauthorized,
      totalEvents: logsData.length,
      lastEvent
    });
  };

  // Apply filters to logs
  const applyFilters = () => {
    let filtered = [...logs];
    
    if (filters.employeeId) {
      filtered = filtered.filter(log => 
        log.personnel_id && log.personnel_id.toLowerCase().includes(filters.employeeId.toLowerCase())
      );
    }
    
    if (filters.location) {
      filtered = filtered.filter(log => 
        log.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }
    
    if (filters.startDate) {
      filtered = filtered.filter(log => 
        new Date(log.timestamp) >= new Date(filters.startDate)
      );
    }
    
    if (filters.endDate) {
      filtered = filtered.filter(log => 
        new Date(log.timestamp) <= new Date(filters.endDate)
      );
    }
    
    if (filters.status !== 'all') {
      filtered = filtered.filter(log => 
        filters.status === 'authorized' ? log.is_authorized : !log.is_authorized
      );
    }
    
    setFilteredLogs(filtered);
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      employeeId: '',
      location: '',
      startDate: null,
      endDate: null,
      status: 'all',
    });
  };

  // Handle filter changes
  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Pagination handlers
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Export to CSV
  const exportToCSV = () => {
    const headers = ['Date', 'Time', 'Employee ID', 'Name', 'Location', 'Camera', 'Status', 'Confidence'];
    
    const csvData = filteredLogs.map(log => {
      const date = new Date(log.timestamp);
      return [
        date.toLocaleDateString(),
        date.toLocaleTimeString(),
        log.personnel_id || 'N/A',
        log.name,
        log.location,
        log.camera_id,
        log.is_authorized ? 'Authorized' : 'Unauthorized',
        log.confidence_score.toFixed(2)
      ];
    });
    
    // Add headers to the beginning
    csvData.unshift(headers);
    
    // Convert to CSV format
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    
    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `facial-auth-logs-${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Format date for display
  const formatDate = (dateString) => {
    const options = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        Authorization Logs
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">Total Events</Typography>
              <Typography variant="h3">{stats.totalEvents}</Typography>
              <Typography variant="body2" color="text.secondary">
                All authentication attempts
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">Authorized</Typography>
              <Typography variant="h3">{stats.authorized}</Typography>
              <Typography variant="body2" color="text.secondary">
                Successful authentications
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="error.main">Unauthorized</Typography>
              <Typography variant="h3">{stats.unauthorized}</Typography>
              <Typography variant="body2" color="text.secondary">
                Failed authentication attempts
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="info.main">Last Event</Typography>
              {stats.lastEvent ? (
                <>
                  <Typography variant="subtitle1">
                    {stats.lastEvent.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(stats.lastEvent.timestamp)}
                  </Typography>
                </>
              ) : (
                <Typography variant="body2">No events recorded</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" sx={{ mb: 2 }}>
          <FilterListIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
          Filter Logs
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              label="Employee ID"
              fullWidth
              variant="outlined"
              size="small"
              value={filters.employeeId}
              onChange={(e) => handleFilterChange('employeeId', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Location"
              fullWidth
              variant="outlined"
              size="small"
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                label="Status"
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="authorized">Authorized</MenuItem>
                <MenuItem value="unauthorized">Unauthorized</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Grid item xs={12} md={2}>
              <DateTimePicker
                label="Start Date"
                value={filters.startDate}
                onChange={(newValue) => handleFilterChange('startDate', newValue)}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <DateTimePicker
                label="End Date"
                value={filters.endDate}
                onChange={(newValue) => handleFilterChange('endDate', newValue)}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </Grid>
          </LocalizationProvider>
        </Grid>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="outlined" sx={{ mr: 1 }} onClick={resetFilters}>
            Reset Filters
          </Button>
          <Button variant="outlined" startIcon={<DownloadIcon />} onClick={exportToCSV}>
            Export CSV
          </Button>
          <Tooltip title="Refresh">
            <IconButton color="primary" onClick={fetchAuthLogs} sx={{ ml: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      {/* Logs Table */}
      <Paper>
        {loading ? (
          <LinearProgress />
        ) : error ? (
          <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>
        ) : (
          <>
            <TableContainer>
              <Table sx={{ minWidth: 650 }} size="medium">
                <TableHead>
                  <TableRow>
                    <TableCell>Date & Time</TableCell>
                    <TableCell>Employee ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredLogs
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((log) => (
                      <TableRow
                        key={log.id}
                        sx={{
                          backgroundColor: log.is_authorized ? 'success.lightest' : 'error.lightest',
                          '&:hover': {
                            backgroundColor: log.is_authorized ? 'success.lighter' : 'error.lighter',
                          }
                        }}
                      >
                        <TableCell>
                          <Tooltip title={new Date(log.timestamp).toLocaleString()}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <EventIcon fontSize="small" sx={{ mr: 1, opacity: 0.6 }} />
                              {formatDate(log.timestamp)}
                            </Box>
                          </Tooltip>
                        </TableCell>
                        <TableCell>{log.personnel_id || 'N/A'}</TableCell>
                        <TableCell>{log.name}</TableCell>
                        <TableCell>{log.location} ({log.camera_id})</TableCell>
                        <TableCell>
                          {log.is_authorized ? (
                            <Chip 
                              icon={<CheckCircleIcon fontSize="small" />} 
                              label="Authorized" 
                              color="success" 
                              size="small"
                            />
                          ) : (
                            <Chip 
                              icon={<CancelIcon fontSize="small" />} 
                              label="Unauthorized" 
                              color="error" 
                              size="small"
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          {(log.confidence_score * 100).toFixed(1)}%
                        </TableCell>
                      </TableRow>
                    ))}
                  
                  {filteredLogs.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                        <Typography variant="subtitle1" color="textSecondary">
                          No logs found matching your criteria
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
              count={filteredLogs.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        )}
      </Paper>
    </Box>
  );
};

export default AuthorizationLogs;