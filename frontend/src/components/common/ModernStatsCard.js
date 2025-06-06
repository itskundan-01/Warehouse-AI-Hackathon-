import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Chip,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';

/**
 * Modern Statistics Card Component
 */
const ModernStatsCard = ({
  title,
  value,
  unit = '',
  subtitle,
  icon,
  trend,
  trendValue,
  trendPercentage,
  color = 'primary',
  progress,
  onClick,
  loading = false,
  className = '',
  sx = {},
}) => {
  // Color configurations
  const colorConfigs = {
    primary: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      light: 'rgba(102, 126, 234, 0.1)',
      main: '#667eea',
    },
    success: {
      background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      light: 'rgba(17, 153, 142, 0.1)',
      main: '#11998e',
    },
    warning: {
      background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      light: 'rgba(240, 147, 251, 0.1)',
      main: '#f093fb',
    },
    info: {
      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      light: 'rgba(79, 172, 254, 0.1)',
      main: '#4facfe',
    },
    error: {
      background: 'linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)',
      light: 'rgba(255, 65, 108, 0.1)',
      main: '#ff416c',
    },
  };

  const currentColor = colorConfigs[color] || colorConfigs.primary;

  // Format large numbers
  const formatValue = (val) => {
    if (typeof val !== 'number') return val;
    if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `${(val / 1000).toFixed(1)}K`;
    return val.toString();
  };

  return (
    <Card
      className={`modern-card stat-card hover-lift ${className}`}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick && {
          '& .action-button': {
            opacity: 1,
            transform: 'translateX(0)',
          },
        },
        ...sx,
      }}
      onClick={onClick}
    >
      {/* Background decoration */}
      <Box
        sx={{
          position: 'absolute',
          top: -20,
          right: -20,
          width: 80,
          height: 80,
          borderRadius: '50%',
          background: currentColor.light,
          opacity: 0.5,
        }}
      />
      
      <CardContent sx={{ position: 'relative', zIndex: 1, p: 3 }}>
        {/* Header with icon and action button */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {icon && (
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  background: currentColor.background,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                }}
              >
                {icon}
              </Box>
            )}
          </Box>
          
          {onClick && (
            <IconButton
              className="action-button"
              size="small"
              sx={{
                opacity: 0,
                transform: 'translateX(10px)',
                transition: 'all 0.3s ease',
                background: currentColor.light,
                '&:hover': {
                  background: currentColor.main,
                  color: 'white',
                },
              }}
            >
              <ArrowForwardIcon fontSize="small" />
            </IconButton>
          )}
        </Box>

        {/* Title */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
          {title}
        </Typography>

        {/* Main Value */}
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1 }}>
          {loading ? (
            <CircularProgress size={24} />
          ) : (
            <>
              <Typography variant="h3" sx={{ 
                fontWeight: 700,
                background: currentColor.background,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                {formatValue(value)}
              </Typography>
              {unit && (
                <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 500 }}>
                  {unit}
                </Typography>
              )}
            </>
          )}
        </Box>

        {/* Subtitle */}
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {subtitle}
          </Typography>
        )}

        {/* Trend indicator */}
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Chip
              icon={trend === 'up' ? <TrendingUpIcon /> : <TrendingDownIcon />}
              label={trendValue || `${trendPercentage}%`}
              size="small"
              sx={{
                background: trend === 'up' 
                  ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
                  : 'linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)',
                color: 'white',
                fontWeight: 600,
                '& .MuiChip-icon': {
                  color: 'white',
                },
              }}
            />
            <Typography variant="caption" color="text.secondary">
              vs last period
            </Typography>
          </Box>
        )}

        {/* Progress bar */}
        {progress !== undefined && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Progress
              </Typography>
              <Typography variant="caption" sx={{ fontWeight: 600, color: currentColor.main }}>
                {Math.round(progress)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: currentColor.light,
                '& .MuiLinearProgress-bar': {
                  background: currentColor.background,
                  borderRadius: 3,
                },
              }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ModernStatsCard;
