import React from 'react';
import { 
  Box, 
  CircularProgress, 
  Typography, 
  Card, 
  CardContent,
  Skeleton
} from '@mui/material';

// Professional loading component
export const ProfessionalLoader = ({ message = 'Loading...', size = 40 }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 200,
      p: 4
    }}
  >
    <CircularProgress 
      size={size} 
      sx={{ 
        color: 'primary.main',
        mb: 2 
      }} 
    />
    <Typography 
      variant="body1" 
      color="text.secondary"
      sx={{ fontWeight: 500 }}
    >
      {message}
    </Typography>
  </Box>
);

// Professional skeleton loader for cards
export const CardSkeleton = ({ height = 200 }) => (
  <Card className="modern-card" sx={{ height }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Skeleton variant="circular" width={48} height={48} sx={{ mr: 2 }} />
        <Box sx={{ flex: 1 }}>
          <Skeleton variant="text" width="60%" height={24} />
          <Skeleton variant="text" width="40%" height={16} />
        </Box>
      </Box>
      <Skeleton variant="rectangular" width="100%" height={80} sx={{ mb: 1 }} />
      <Skeleton variant="text" width="80%" />
      <Skeleton variant="text" width="60%" />
    </CardContent>
  </Card>
);

// Professional skeleton loader for lists
export const ListSkeleton = ({ items = 5 }) => (
  <Box>
    {Array.from({ length: items }).map((_, index) => (
      <Box key={index} sx={{ display: 'flex', alignItems: 'center', py: 2, px: 1 }}>
        <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
        <Box sx={{ flex: 1 }}>
          <Skeleton variant="text" width="70%" height={20} />
          <Skeleton variant="text" width="50%" height={16} />
        </Box>
        <Skeleton variant="text" width="15%" height={16} />
      </Box>
    ))}
  </Box>
);

// Professional skeleton loader for tables
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <Box>
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <Box key={rowIndex} sx={{ display: 'flex', py: 1.5, px: 2 }}>
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Box key={colIndex} sx={{ flex: 1, mr: colIndex < columns - 1 ? 2 : 0 }}>
            <Skeleton 
              variant="text" 
              width={colIndex === 0 ? "80%" : "60%"} 
              height={20} 
            />
          </Box>
        ))}
      </Box>
    ))}
  </Box>
);

export default ProfessionalLoader;
