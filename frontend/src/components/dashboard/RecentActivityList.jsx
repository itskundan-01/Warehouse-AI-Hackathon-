import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Chip,
  Divider,
  IconButton
} from '@mui/material';
import {
  History as HistoryIcon,
  DirectionsCar as VehicleIcon,
  Person as PersonIcon,
  Inventory as InventoryIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  AccessTime as TimeIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';

const RecentActivityList = () => {
  const activities = [
    {
      id: 1,
      type: 'vehicle',
      title: 'Vehicle Entry Logged',
      description: 'TN-01-AB-1234 entered Main Gate',
      timestamp: '2 minutes ago',
      status: 'success',
      icon: <VehicleIcon />
    },
    {
      id: 2,
      type: 'personnel',
      title: 'Personnel Check-in',
      description: 'Raj Patel checked in at Zone B',
      timestamp: '5 minutes ago',
      status: 'success',
      icon: <PersonIcon />
    },
    {
      id: 3,
      type: 'gunny',
      title: 'Gunny Bags Counted',
      description: '150 bags processed in Warehouse A',
      timestamp: '8 minutes ago',
      status: 'info',
      icon: <InventoryIcon />
    },
    {
      id: 4,
      type: 'security',
      title: 'Security Alert',
      description: 'Motion detected in restricted area',
      timestamp: '12 minutes ago',
      status: 'warning',
      icon: <SecurityIcon />
    },
    {
      id: 5,
      type: 'vehicle',
      title: 'Unauthorized Vehicle',
      description: 'Unknown vehicle detected at perimeter',
      timestamp: '18 minutes ago',
      status: 'error',
      icon: <WarningIcon />
    },
    {
      id: 6,
      type: 'personnel',
      title: 'Personnel Check-out',
      description: 'Maya Singh checked out from Zone A',
      timestamp: '25 minutes ago',
      status: 'success',
      icon: <PersonIcon />
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'vehicle': return 'gradient-secondary';
      case 'personnel': return 'gradient-info';
      case 'gunny': return 'gradient-primary';
      case 'security': return 'gradient-warning';
      default: return 'gradient-primary';
    }
  };

  return (
    <Card className="modern-card" sx={{ height: '100%' }}>
      <CardHeader
        avatar={
          <Avatar className="gradient-info" sx={{ width: 48, height: 48 }}>
            <HistoryIcon />
          </Avatar>
        }
        title={
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            Recent Activity
          </Typography>
        }
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label="Live"
              color="success"
              size="small"
              sx={{ fontWeight: 600 }}
            />
            <IconButton size="small">
              <MoreVertIcon />
            </IconButton>
          </Box>
        }
        sx={{ pb: 1 }}
      />
      
      <Divider />
      
      <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
        <List sx={{ py: 0 }}>
          {activities.map((activity, index) => (
            <React.Fragment key={activity.id}>
              <ListItem
                sx={{
                  py: 2,
                  px: 3,
                  '&:hover': {
                    backgroundColor: 'rgba(21, 101, 192, 0.05)',
                    cursor: 'pointer'
                  }
                }}
              >
                <ListItemIcon>
                  <Avatar
                    className={getTypeColor(activity.type)}
                    sx={{ width: 40, height: 40 }}
                  >
                    {activity.icon}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {activity.title}
                      </Typography>
                      <Chip
                        label={activity.status}
                        color={getStatusColor(activity.status)}
                        size="small"
                        sx={{ 
                          fontSize: '0.7rem', 
                          height: 18,
                          fontWeight: 600,
                          textTransform: 'capitalize'
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
                        {activity.description}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TimeIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                        <Typography variant="caption" color="text.secondary">
                          {activity.timestamp}
                        </Typography>
                      </Box>
                    </Box>
                  }
                />
              </ListItem>
              {index < activities.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
        
        <Box sx={{ p: 2, pt: 1, textAlign: 'center', borderTop: '1px solid', borderColor: 'divider' }}>
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
            View All Activity →
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RecentActivityList;