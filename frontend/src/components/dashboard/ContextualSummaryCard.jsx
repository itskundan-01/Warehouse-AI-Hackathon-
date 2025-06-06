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
  LinearProgress,
  Divider
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Videocam as VideocamIcon,
  Event as EventIcon,
  Warning as WarningIcon,
  ArrowForward as ArrowForwardIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

const ContextualSummaryCard = ({ data, onClick }) => {
  const activeCameras = data.activeCameras || 0;
  const eventsToday = data.eventsToday || 0;
  const openAlerts = data.openAlerts || 0;
  
  const cameraUtilization = Math.min((activeCameras / 30) * 100, 100); // Assuming 30 total cameras
  
  const getUtilizationColor = (utilization) => {
    if (utilization >= 80) return 'success';
    if (utilization >= 60) return 'warning';
    return 'error';
  };

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
          <Avatar className="gradient-warning" sx={{ width: 48, height: 48 }}>
            <PsychologyIcon />
          </Avatar>
        }
        title={
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            Contextual Intelligence
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
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: 'primary.main',
                  mb: 0.5
                }}
              >
                {activeCameras}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active Cameras
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: 'info.main',
                  mb: 0.5
                }}
              >
                {eventsToday}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Events Today
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: openAlerts > 0 ? 'warning.main' : 'success.main',
                  mb: 0.5
                }}
              >
                {openAlerts}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Open Alerts
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Camera Utilization
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {activeCameras}/30
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={cameraUtilization}
                color={getUtilizationColor(cameraUtilization)}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  bgcolor: 'rgba(0, 0, 0, 0.1)'
                }}
              />
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Chip
                  icon={<VideocamIcon />}
                  label="Live Feed"
                  color="success"
                  size="small"
                  sx={{ width: '100%', fontWeight: 600 }}
                />
              </Grid>
              <Grid item xs={6}>
                <Chip
                  icon={<EventIcon />}
                  label="AI Analysis"
                  color="primary"
                  size="small"
                  sx={{ width: '100%', fontWeight: 600 }}
                />
              </Grid>
            </Grid>
          </Grid>
          
          <Grid item xs={12}>
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
                View Insights →
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ContextualSummaryCard;