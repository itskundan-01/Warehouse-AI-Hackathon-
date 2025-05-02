import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Card, 
  CardContent,
  Grid,
  Avatar,
  Chip,
  LinearProgress
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import ErrorIcon from '@mui/icons-material/Error';

/**
 * Recognition Results component to display individual recognition result details
 */
const RecognitionResults = ({ result }) => {
  if (!result) return null;
  
  const confidencePercent = Math.round(result.confidence * 100);
  const isAuthenticated = result.authenticated;
  
  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={3} md={2}>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Avatar 
                sx={{ 
                  width: 80, 
                  height: 80,
                  bgcolor: isAuthenticated ? 'success.main' : 'error.main'
                }}
              >
                <PersonIcon sx={{ fontSize: 40 }} />
              </Avatar>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={9} md={10}>
            <Typography variant="h6" gutterBottom>
              {result.name}
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <LocationOnIcon sx={{ color: 'text.secondary', mr: 1 }} />
                  <Typography variant="body2">
                    Location: {result.location}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccessTimeIcon sx={{ color: 'text.secondary', mr: 1 }} />
                  <Typography variant="body2">
                    Time: {result.timestamp ? new Date(result.timestamp).toLocaleString() : 'N/A'}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {isAuthenticated ? 
                    <VerifiedUserIcon color="success" sx={{ mr: 1 }} /> : 
                    <ErrorIcon color="error" sx={{ mr: 1 }} />
                  }
                  <Chip
                    label={isAuthenticated ? "Authenticated" : "Unauthorized"}
                    color={isAuthenticated ? "success" : "error"}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper elevation={0} variant="outlined" sx={{ p: 1.5 }}>
                  <Typography variant="body2" gutterBottom>
                    Confidence Score
                  </Typography>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    {confidencePercent}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={confidencePercent} 
                    color={confidencePercent > 70 ? "success" : confidencePercent > 50 ? "warning" : "error"}
                  />
                </Paper>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default RecognitionResults;