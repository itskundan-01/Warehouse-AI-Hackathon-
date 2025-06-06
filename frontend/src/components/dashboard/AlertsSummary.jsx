import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Box,
  Divider
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  MoreVert as MoreVertIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';

const AlertsSummary = () => {
  const alerts = [
    {
      id: 1,
      type: 'security',
      severity: 'high',
      title: 'Unauthorized Vehicle Detected',
      description: 'Unknown vehicle at Main Gate - License: ABC-1234',
      timestamp: '2 minutes ago',
      status: 'active'
    },
    {
      id: 2,
      type: 'safety',
      severity: 'medium',
      title: 'Personnel Safety Alert',
      description: 'Worker without safety equipment in Zone B',
      timestamp: '15 minutes ago',
      status: 'investigating'
    },
    {
      id: 3,
      type: 'operational',
      severity: 'low',
      title: 'Inventory Threshold',
      description: 'Gunny bag count approaching storage limit',
      timestamp: '1 hour ago',
      status: 'acknowledged'
    },
    {
      id: 4,
      type: 'system',
      severity: 'medium',
      title: 'Camera Maintenance',
      description: 'Camera 7 scheduled for maintenance at 3 PM',
      timestamp: '2 hours ago',
      status: 'scheduled'
    }
  ];

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <ErrorIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'error';
      case 'investigating': return 'warning';
      case 'acknowledged': return 'info';
      case 'scheduled': return 'primary';
      case 'resolved': return 'success';
      default: return 'default';
    }
  };

  const formatStatus = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <Card className="modern-card" sx={{ height: '100%' }}>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon color="warning" />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Recent Alerts
            </Typography>
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`${alerts.length} Active`}
              color="warning"
              size="small"
              sx={{ fontWeight: 600 }}
            />
          </Box>
        }
        sx={{ pb: 1 }}
      />
      <Divider />
      <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
        <List sx={{ py: 0 }}>
          {alerts.map((alert, index) => (
            <React.Fragment key={alert.id}>
              <ListItem
                sx={{
                  py: 2,
                  px: 3,
                  '&:hover': {
                    backgroundColor: 'rgba(21, 101, 192, 0.05)'
                  }
                }}
              >
                <ListItemIcon>
                  {getSeverityIcon(alert.severity)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {alert.title}
                      </Typography>
                      <Chip
                        label={alert.severity.toUpperCase()}
                        color={getSeverityColor(alert.severity)}
                        size="small"
                        sx={{ 
                          fontSize: '0.7rem', 
                          height: 20,
                          fontWeight: 600
                        }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 0.5 }}
                      >
                        {alert.description}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TimeIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {alert.timestamp}
                        </Typography>
                        <Chip
                          label={formatStatus(alert.status)}
                          color={getStatusColor(alert.status)}
                          size="small"
                          variant="outlined"
                          sx={{ 
                            fontSize: '0.7rem', 
                            height: 18,
                            ml: 1
                          }}
                        />
                      </Box>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" size="small" sx={{ color: 'text.secondary' }}>
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              {index < alerts.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
        
        <Box sx={{ p: 2, pt: 1, textAlign: 'center' }}>
          <Typography
            variant="caption"
            color="primary"
            sx={{ 
              cursor: 'pointer',
              fontWeight: 600,
              '&:hover': {
                textDecoration: 'underline'
              }
            }}
          >
            View All Alerts →
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AlertsSummary;