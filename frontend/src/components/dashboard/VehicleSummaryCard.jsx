import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Chip,
  Grid,
  Avatar,
  IconButton,
  Divider
} from '@mui/material';
import {
  DirectionsCar as VehicleIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';

const VehicleSummaryCard = ({ data, onClick }) => {
  const getStatusData = () => [
    {
      label: 'Authorized',
      value: data.authorized || 0,
      color: 'success',
      icon: <CheckCircleIcon fontSize="small" />
    },
    {
      label: 'Unauthorized',
      value: data.unauthorized || 0,
      color: 'error',
      icon: <CancelIcon fontSize="small" />
    },
    {
      label: 'Pending',
      value: data.pendingVerification || 0,
      color: 'warning',
      icon: <ScheduleIcon fontSize="small" />
    }
  ];

  const statusData = getStatusData();
  const totalToday = data.totalToday || 0;

  return (
    <Card 
      className="modern-card glass-effect"
      sx={{ 
        height: '100%',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)'
        }
      }}
      onClick={onClick}
    >
      <CardHeader
        avatar={
          <Avatar className="gradient-secondary" sx={{ width: 48, height: 48 }}>
            <VehicleIcon />
          </Avatar>
        }
        title={
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            Vehicle Recognition
          </Typography>
        }
        action={
          <IconButton size="small" sx={{ color: 'text.secondary' }}>
            <ArrowForwardIcon />
          </IconButton>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ pt: 0 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'baseline', mb: 2 }}>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 700,
                  color: 'primary.main',
                  mr: 1
                }}
              >
                {totalToday}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                vehicles today
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
          </Grid>
          
          {statusData.map((status, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                py: 1
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {status.icon}
                  <Typography 
                    variant="body2" 
                    sx={{ ml: 1, fontWeight: 500 }}
                  >
                    {status.label}
                  </Typography>
                </Box>
                <Chip
                  label={status.value}
                  color={status.color}
                  size="small"
                  sx={{ 
                    fontWeight: 600,
                    minWidth: 45
                  }}
                />
              </Box>
            </Grid>
          ))}
          
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center',
              mt: 2
            }}>
              <Typography
                variant="body2"
                color="primary"
                sx={{
                  fontWeight: 600,
                  cursor: 'pointer',
                  '&:hover': {
                    textDecoration: 'underline'
                  }
                }}
              >
                View All Vehicles →
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default VehicleSummaryCard;