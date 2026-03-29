import React from 'react';
import { Box, CircularProgress, Typography, Skeleton } from '@mui/material';

export const LoadingSpinner = ({ message = 'Loading...' }) => (
  <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" p={4}>
    <CircularProgress size={40} />
    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
      {message}
    </Typography>
  </Box>
);

export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <Box>
    {Array.from({ length: rows }).map((_, index) => (
      <Box key={index} display="flex" gap={2} mb={1}>
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Skeleton key={colIndex} variant="text" width="100%" height={40} />
        ))}
      </Box>
    ))}
  </Box>
);

export const CardSkeleton = () => (
  <Box p={2}>
    <Skeleton variant="text" width="60%" height={30} />
    <Skeleton variant="text" width="40%" height={60} />
    <Skeleton variant="text" width="80%" height={20} />
  </Box>
);