import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Inventory as InventoryIcon,
  DirectionsCar as VehicleIcon,
  People as PeopleIcon,
  Warning as AlertIcon
} from '@mui/icons-material';

const StatsSummaryGrid = ({ stats = {} }) => {
  const statsData = [
    {
      title: 'Gunny Bags Processed',
      value: stats.gunnyProcessed || '0',
      icon: <InventoryIcon fontSize="large" />,
      color: 'primary',
      trend: '+12.5%',
      trendDirection: 'up',
      description: 'Today'
    },
    {
      title: 'Vehicles Logged',
      value: stats.vehiclesLogged || '0',
      icon: <VehicleIcon fontSize="large" />,
      color: 'secondary',
      trend: '+8.2%',
      trendDirection: 'up',
      description: 'This shift'
    },
    {
      title: 'Active Personnel',
      value: stats.personnelActive || '0',
      icon: <PeopleIcon fontSize="large" />,
      color: 'info',
      trend: '+2.1%',
      trendDirection: 'up',
      description: 'Currently'
    },
    {
      title: 'Alerts Today',
      value: stats.alertsToday || '0',
      icon: <AlertIcon fontSize="large" />,
      color: 'warning',
      trend: '-15.3%',
      trendDirection: 'down',
      description: 'Last 24h'
    }
  ];

  const getColorClass = (color) => {
    switch (color) {
      case 'primary': return 'gradient-primary';
      case 'secondary': return 'gradient-success';
      case 'info': return 'gradient-info';
      case 'warning': return 'gradient-warning';
      default: return 'gradient-primary';
    }
  };

  const getTrendIcon = (direction) => {
    return direction === 'up' ? (
      <TrendingUpIcon fontSize="small" />
    ) : (
      <TrendingDownIcon fontSize="small" />
    );
  };

  const getTrendColor = (direction) => {
    return direction === 'up' ? 'success' : 'error';
  };

  return (
    <Grid container spacing={3}>
      {statsData.map((item, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card 
            className="modern-card stat-card stagger-item"
            sx={{ 
              height: '100%',
              position: 'relative',
              overflow: 'visible'
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                <Avatar
                  className={getColorClass(item.color)}
                  sx={{
                    width: 56,
                    height: 56,
                    mr: 2,
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                  }}
                >
                  {item.icon}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h4"
                    component="div"
                    sx={{
                      fontWeight: 700,
                      color: 'primary.main',
                      mb: 0.5
                    }}
                  >
                    {item.value}
                  </Typography>
                  <Typography
                    variant="subtitle1"
                    color="text.secondary"
                    sx={{ fontWeight: 500 }}
                  >
                    {item.title}
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                mt: 2
              }}>
                <Chip
                  icon={getTrendIcon(item.trendDirection)}
                  label={item.trend}
                  color={getTrendColor(item.trendDirection)}
                  size="small"
                  sx={{
                    fontWeight: 600,
                    borderRadius: 2
                  }}
                />
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ fontWeight: 500 }}
                >
                  {item.description}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default StatsSummaryGrid;