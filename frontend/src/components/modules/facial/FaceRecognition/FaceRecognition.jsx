import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TablePagination,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { format } from 'date-fns';

/**
 * Face Recognition Component
 * Shows recent facial recognition results and authentication logs
 */
const FaceRecognition = ({ data = [], loading = false }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  // Mock data in case none is provided
  const mockData = Array(10).fill(null).map((_, idx) => ({
    id: `rec-${idx}`,
    timestamp: new Date(Date.now() - Math.random() * 86400000 * 3),
    name: idx % 3 === 0 ? 'Unknown Person' : `Employee ${idx + 1}`,
    confidence: idx % 3 === 0 ? 0.48 : 0.75 + Math.random() * 0.2,
    authenticated: idx % 3 !== 0,
    location: ['Main Entrance', 'Loading Dock', 'Office Area'][idx % 3],
  }));

  const recognitionData = data.length > 0 ? data : mockData;
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Recent Facial Recognition Activity
      </Typography>
      
      <Paper elevation={3} sx={{ width: '100%', overflow: 'hidden' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : recognitionData.length === 0 ? (
          <Alert severity="info" sx={{ m: 2 }}>
            No recent facial recognition events found.
          </Alert>
        ) : (
          <>
            <TableContainer sx={{ maxHeight: 440 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Personnel</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recognitionData
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((record) => (
                      <TableRow key={record.id} hover>
                        <TableCell>
                          {format(new Date(record.timestamp), 'dd MMM yyyy, hh:mm a')}
                        </TableCell>
                        <TableCell>
                          {record.name}
                        </TableCell>
                        <TableCell>
                          {record.location}
                        </TableCell>
                        <TableCell>
                          {(record.confidence * 100).toFixed(1)}%
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={record.authenticated ? <CheckCircleIcon /> : <CancelIcon />}
                            label={record.authenticated ? "Authenticated" : "Unauthorized"}
                            color={record.authenticated ? "success" : "error"}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={recognitionData.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        )}
      </Paper>
      
      <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
        The system continuously logs facial recognition events. All unauthorized access 
        attempts are recorded and can trigger alerts based on security settings.
      </Typography>
    </Box>
  );
};

export default FaceRecognition;