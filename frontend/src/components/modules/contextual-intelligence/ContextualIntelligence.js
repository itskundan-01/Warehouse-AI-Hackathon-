import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

// Import the components that we'll create next
import VideoResultsList from './VideoResultsList';
import FilterDialog from './FilterDialog';
import VideoPlayerDialog from './VideoPlayerDialog';

// This will eventually be replaced with actual Redux actions
const mockSearchQuery = async (query, filters) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        results: [
          {
            id: 1,
            timestamp: "2025-05-01 10:15:32",
            duration: 42,
            confidence: 0.89,
            thumbnail: "https://via.placeholder.com/300x200?text=Warehouse+Entry",
            location: "Loading Bay",
            title: "Truck #A452 entering loading bay",
            bookmarked: false,
            videoUrl: "/assets/videos/sample1.mp4"
          },
          {
            id: 2,
            timestamp: "2025-05-01 10:22:18",
            duration: 35,
            confidence: 0.76,
            thumbnail: "https://via.placeholder.com/300x200?text=Workers+Handling+Bags",
            location: "Station 3",
            title: "Workers transferring gunny bags",
            bookmarked: true,
            videoUrl: "/assets/videos/sample2.mp4"
          },
          {
            id: 3,
            timestamp: "2025-05-01 10:45:07",
            duration: 28,
            confidence: 0.92,
            thumbnail: "https://via.placeholder.com/300x200?text=Security+Check",
            location: "Entry Gate",
            title: "Security personnel checking vehicle",
            bookmarked: false,
            videoUrl: "/assets/videos/sample3.mp4"
          }
        ],
        totalCount: 3
      });
    }, 1500);
  });
};

const ContextualIntelligence = ({ onNotify }) => {
  const dispatch = useDispatch();
  
  // States
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [filters, setFilters] = useState({
    dateRange: { start: '2025-05-01', end: '2025-05-02' },
    location: 'all',
    duration: [0, 60],
    confidence: 0.5
  });

  // Handle search submission
  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      // In a production app, this would dispatch a Redux action
      // const { results } = await dispatch(searchContextualQuery({ query, filters })).unwrap();
      
      // Using mock data for now
      const { results: searchResults } = await mockSearchQuery(query, filters);
      setResults(searchResults);
      
      if (searchResults.length === 0 && onNotify) {
        onNotify({
          severity: 'info',
          message: 'No results found. Try adjusting your search terms or filters.'
        });
      }
    } catch (error) {
      console.error('Search error:', error);
      if (onNotify) {
        onNotify({
          severity: 'error',
          message: 'Error performing search. Please try again.'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle video selection
  const handleVideoSelect = (video) => {
    setSelectedVideo(video);
  };

  // Handle video dialog close
  const handleCloseVideo = () => {
    setSelectedVideo(null);
  };

  // Handle filter changes
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  // Handle bookmark toggle
  const handleToggleBookmark = (videoId) => {
    setResults((prev) => 
      prev.map((item) => 
        item.id === videoId ? { ...item, bookmarked: !item.bookmarked } : item
      )
    );
    
    // In a real app, this would also dispatch a Redux action to update the server
    // dispatch(toggleVideoBookmark(videoId));
    
    if (onNotify) {
      onNotify({
        severity: 'success',
        message: 'Bookmark updated'
      });
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Search Area */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask anything about the warehouse video data..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button 
              variant="contained" 
              fullWidth 
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={loading || !query.trim()}
            >
              Search
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button 
              variant="outlined" 
              fullWidth 
              startIcon={<FilterIcon />}
              onClick={() => setFilterDialogOpen(true)}
            >
              Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Results Area */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              {results.length > 0 
                ? `${results.length} results found` 
                : 'No results yet'}
            </Typography>
            {results.length > 0 && (
              <Tooltip title="Refresh results">
                <IconButton onClick={handleSearch}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          
          <VideoResultsList 
            results={results} 
            onVideoSelect={handleVideoSelect}
            onToggleBookmark={handleToggleBookmark}
          />
        </Box>
      )}

      {/* Dialogs */}
      <FilterDialog 
        open={filterDialogOpen}
        filters={filters}
        onClose={() => setFilterDialogOpen(false)}
        onApply={(newFilters) => {
          handleFilterChange(newFilters);
          setFilterDialogOpen(false);
          handleSearch();
        }}
      />

      <VideoPlayerDialog
        video={selectedVideo}
        open={!!selectedVideo}
        onClose={handleCloseVideo}
        onToggleBookmark={handleToggleBookmark}
      />
    </Box>
  );
};

export default ContextualIntelligence;