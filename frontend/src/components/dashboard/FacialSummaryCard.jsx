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
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Person as PersonIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Group as GroupIcon,
  ArrowForward as ArrowForwardIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';

const FacialSummaryCard = ({ data, onClick }) => {
  const recentLogs = data.recentLogs || [];
  
  const getStatusIcon = (status) => {
    return status === 'authorized' ? (
      <CheckCircleIcon color="success" />
    ) : (
      <CancelIcon color="error" />
    );
  };

  const getStatusColor = (status) => {
    return status === 'authorized' ? 'success' : 'error';
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
          <Avatar className="gradient-info" sx={{ width: 48, height: 48 }}>
            <PersonIcon />
          </Avatar>
        }
        title={
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            Facial Recognition
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
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: 'primary.main',
                  mb: 0.5
                }}
              >
                {data.authorizedPersonnel || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Personnel
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: 'success.main',
                  mb: 0.5
                }}
              >
                {data.presentToday || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Present Today
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1, mb: 2 }}>
              <Chip
                icon={<GroupIcon />}
                label={`${data.unauthorized || 0} Unauthorized`}
                color="error"
                size="small"
                sx={{ fontWeight: 600 }}
              />
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Recent Activity
            </Typography>
            
            <List sx={{ py: 0 }}>
              {recentLogs.slice(0, 2).map((log, index) => (
                <ListItem key={log.id} sx={{ px: 0, py: 1 }}>
                  <ListItemAvatar sx={{ minWidth: 32 }}>
                    <Avatar sx={{ width: 24, height: 24 }}>
                      {getStatusIcon(log.status)}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {log.name}
                      </Typography>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TimeIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {log.time}
                        </Typography>
                        <Chip
                          label={log.status}
                          color={getStatusColor(log.status)}
                          size="small"
                          sx={{ 
                            fontSize: '0.65rem', 
                            height: 16,
                            fontWeight: 600
                          }}
                        />
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
            
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center',
              mt: 1
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
                View All Logs →
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default FacialSummaryCard;