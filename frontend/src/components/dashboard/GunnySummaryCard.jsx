import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Grid,
  Avatar,
  IconButton
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  TrendingUp as TrendingUpIcon,
  LocationOn as LocationIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';

const GunnySummaryCard = ({ data, onClick }) => {
  const calculateProgress = () => {
    return Math.min((data.todayCount / 500) * 100, 100); // Assuming daily target of 500
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'success';
    if (progress >= 60) return 'warning';
    return 'primary';
  };

  const progress = calculateProgress();

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
          <Avatar className="gradient-primary" sx={{ width: 48, height: 48 }}>
            <InventoryIcon />
          </Avatar>
        }
        title={
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            Gunny Counter
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
                {data.totalBags?.toLocaleString() || '0'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                total bags
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Today's Progress
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {data.todayCount || 0} / 500
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress}
                color={getProgressColor(progress)}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(0, 0, 0, 0.1)'
                }}
              />
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <LocationIcon fontSize="small" color="action" sx={{ mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                {data.activeWarehouse || 'No active warehouse'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Chip
                icon={<TrendingUpIcon />}
                label={`${data.trend > 0 ? '+' : ''}${data.trend}%`}
                color={data.trend > 0 ? 'success' : 'error'}
                size="small"
                sx={{ fontWeight: 600 }}
              />
              <Typography variant="caption" color="text.secondary">
                vs last period
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default GunnySummaryCard;