import React from 'react';
import { Outlet } from 'react-router-dom';
import { 
  Box, 
  Container, 
  Paper, 
  Typography, 
  useTheme, 
  useMediaQuery 
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';

/**
 * AuthLayout component serves as a wrapper for authentication-related pages
 * such as login, registration, and forgot password.
 * 
 * It provides consistent styling and branding across all auth pages.
 */
const AuthLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: theme.palette.background.default,
        py: 3,
        backgroundImage: 'url("/assets/images/warehouse-bg.jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          zIndex: 1
        }
      }}
    >
      <Container 
        maxWidth="sm" 
        sx={{ 
          position: 'relative', 
          zIndex: 2 
        }}
      >
        <Box 
          display="flex" 
          flexDirection="column" 
          alignItems="center" 
          mb={4}
        >
          <SecurityIcon 
            color="primary" 
            sx={{ 
              fontSize: 60, 
              mb: 2 
            }} 
          />
          <Typography 
            variant="h4" 
            component="h1" 
            align="center" 
            gutterBottom
            sx={{
              fontWeight: 700,
              color: '#ffffff'
            }}
          >
            WarehouseVision AI
          </Typography>
          <Typography 
            variant="body1" 
            align="center" 
            sx={{ 
              mb: 4, 
              color: 'rgba(255,255,255,0.7)' 
            }}
          >
            Intelligent Surveillance & Monitoring System
          </Typography>
        </Box>
        
        <Paper 
          elevation={isMobile ? 0 : 6}
          sx={{
            p: 4,
            borderRadius: 2,
          }}
        >
          <Outlet />
        </Paper>
      </Container>
      
      <Box 
        component="footer" 
        sx={{ 
          mt: 4, 
          textAlign: 'center',
          position: 'relative',
          zIndex: 2,
          color: 'rgba(255,255,255,0.5)',
          fontSize: '0.875rem'
        }}
      >
        <Typography variant="body2">
          © {new Date().getFullYear()} WarehouseVision AI | All Rights Reserved
        </Typography>
      </Box>
    </Box>
  );
};

export default AuthLayout;