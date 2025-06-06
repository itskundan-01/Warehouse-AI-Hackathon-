import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Grid,
  Avatar,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Warehouse as WarehouseIcon,
  LocationOn as LocationIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  MoreVert as MoreVertIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';

const WarehouseOverview = () => {
  const warehouseData = {
    name: 'Chennai Central Warehouse',
    status: 'operational',
    zones: [
      { id: 1, name: 'Zone A - Storage', status: 'operational', utilization: 85 },
      { id: 2, name: 'Zone B - Processing', status: 'operational', utilization: 72 },
      { id: 3, name: 'Zone C - Loading', status: 'maintenance', utilization: 0 },
      { id: 4, name: 'Zone D - Security', status: 'operational', utilization: 100 }
    ],
    metrics: {
      totalArea: '50,000 sq ft',
      avgUtilization: '64%',
      securityLevel: 'High',
      operationalStatus: 'Normal'
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'success';
      case 'maintenance': return 'warning';
      case 'offline': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'operational': return <CheckCircleIcon />;
      case 'maintenance': return <WarningIcon />;
      case 'offline': return <ErrorIcon />;
      default: return <CheckCircleIcon />;
    }
  };

  const getUtilizationColor = (utilization) => {
    if (utilization >= 90) return 'error';
    if (utilization >= 75) return 'warning';
    if (utilization >= 50) return 'success';
    return 'info';
  };

  return (
    <Card className="modern-card" sx={{ height: '100%' }}>
      <CardHeader
        avatar={
          <Avatar className="gradient-secondary" sx={{ width: 48, height: 48 }}>
            <WarehouseIcon />
          </Avatar>
        }
        title={
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
              Warehouse Overview
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
              <LocationIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
              <Typography variant="body2" color="text.secondary">
                {warehouseData.name}
              </Typography>
            </Box>
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={warehouseData.status}
              color={getStatusColor(warehouseData.status)}
              size="small"
              sx={{ fontWeight: 600, textTransform: 'capitalize' }}
            />
            <IconButton size="small">
              <MoreVertIcon />
            </IconButton>
          </Box>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ pt: 0 }}>
        {/* Quick Metrics */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center', p: 1, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                {warehouseData.metrics.totalArea}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Area
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center', p: 1, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                {warehouseData.metrics.avgUtilization}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Avg Utilization
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ mb: 2 }} />

        {/* Zone Status */}
        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
          Zone Status
        </Typography>
        
        <List sx={{ py: 0 }}>
          {warehouseData.zones.map((zone, index) => (
            <React.Fragment key={zone.id}>
              <ListItem sx={{ px: 0, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  {getStatusIcon(zone.status)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {zone.name}
                    </Typography>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                      <Chip
                        label={zone.status}
                        color={getStatusColor(zone.status)}
                        size="small"
                        sx={{ fontSize: '0.7rem', height: 18, fontWeight: 600 }}
                      />
                      {zone.utilization > 0 && (
                        <Chip
                          label={`${zone.utilization}%`}
                          color={getUtilizationColor(zone.utilization)}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem', height: 18 }}
                        />
                      )}
                    </Box>
                  }
                />
              </ListItem>
              {index < warehouseData.zones.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        {/* Security & Operations */}
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SecurityIcon color="success" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Security Level
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {warehouseData.metrics.securityLevel}
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SpeedIcon color="primary" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Operations
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {warehouseData.metrics.operationalStatus}
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default WarehouseOverview;