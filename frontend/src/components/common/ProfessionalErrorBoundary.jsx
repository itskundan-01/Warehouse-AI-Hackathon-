import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  AlertTitle,
  Divider,
  Chip
} from '@mui/material';
import {
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  BugReport as BugIcon
} from '@mui/icons-material';

class ProfessionalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: Date.now().toString(36) + Math.random().toString(36).substr(2)
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // In production, you would send this to an error reporting service
    if (process.env.NODE_ENV === 'production') {
      // Example: errorReportingService.captureException(error, { extra: errorInfo });
    }
  }

  handleRetry = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null 
    });
    
    // Refresh the page in case of persistent errors
    if (this.props.refreshOnRetry) {
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      // Professional error UI
      return (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: this.props.fullScreen ? '100vh' : '400px',
            p: 3,
            bgcolor: 'background.default'
          }}
        >
          <Card 
            className="modern-card"
            sx={{ 
              maxWidth: 600, 
              width: '100%',
              textAlign: 'center'
            }}
          >
            <CardContent sx={{ p: 4 }}>
              <ErrorIcon 
                sx={{ 
                  fontSize: 64, 
                  color: 'error.main', 
                  mb: 2 
                }} 
              />
              
              <Typography 
                variant="h5" 
                sx={{ 
                  fontWeight: 600, 
                  color: 'primary.main',
                  mb: 1 
                }}
              >
                Something went wrong
              </Typography>
              
              <Typography 
                variant="body1" 
                color="text.secondary" 
                sx={{ mb: 3 }}
              >
                We're sorry, but something unexpected happened. Our team has been notified.
              </Typography>

              <Alert 
                severity="error" 
                sx={{ 
                  mb: 3, 
                  textAlign: 'left',
                  '& .MuiAlert-message': {
                    width: '100%'
                  }
                }}
              >
                <AlertTitle>Error Details</AlertTitle>
                <Box sx={{ mt: 1 }}>
                  <Chip 
                    icon={<BugIcon />}
                    label={`Error ID: ${this.state.errorId}`}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  {process.env.NODE_ENV === 'development' && this.state.error && (
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontFamily: 'monospace',
                        fontSize: '0.8rem',
                        mt: 1,
                        p: 1,
                        bgcolor: 'rgba(0, 0, 0, 0.05)',
                        borderRadius: 1,
                        wordBreak: 'break-word'
                      }}
                    >
                      {this.state.error.toString()}
                    </Typography>
                  )}
                </Box>
              </Alert>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  startIcon={<RefreshIcon />}
                  onClick={this.handleRetry}
                  sx={{ 
                    borderRadius: 2,
                    px: 3
                  }}
                >
                  Try Again
                </Button>
                
                <Button
                  variant="outlined"
                  onClick={() => window.location.href = '/dashboard'}
                  sx={{ 
                    borderRadius: 2,
                    px: 3
                  }}
                >
                  Go to Dashboard
                </Button>
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography 
                variant="caption" 
                color="text.secondary"
                sx={{ display: 'block' }}
              >
                If this problem persists, please contact your system administrator.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ProfessionalErrorBoundary;
