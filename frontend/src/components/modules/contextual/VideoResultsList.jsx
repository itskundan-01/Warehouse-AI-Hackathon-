import React from 'react';
import {
  Grid,
  Card,
  CardActionArea,
  CardMedia,
  CardContent,
  Typography,
  Box,
  IconButton,
  Chip
} from '@mui/material';
import { 
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  PlayCircleFilled as PlayIcon
} from '@mui/icons-material';

const VideoResultsList = ({ results, onVideoSelect, onToggleBookmark }) => {
  if (!results || results.length === 0) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No video results to display. Try adjusting your search criteria.
        </Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      {results.map((video) => (
        <Grid item xs={12} sm={6} md={4} key={video.id}>
          <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ position: 'relative' }}>
              <CardActionArea onClick={() => onVideoSelect(video)}>
                <CardMedia
                  component="img"
                  height="180"
                  image={video.thumbnail}
                  alt={video.title}
                />
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    bgcolor: 'rgba(0, 0, 0, 0.6)',
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    px: 2,
                    py: 0.5,
                  }}
                >
                  <Typography variant="body2">
                    {`${video.duration}s`}
                  </Typography>
                  <Box>
                    <Chip
                      size="small"
                      label={`${Math.round(video.confidence * 100)}%`}
                      color={video.confidence > 0.8 ? 'success' : video.confidence > 0.5 ? 'warning' : 'error'}
                      sx={{ mr: 1 }}
                    />
                  </Box>
                </Box>
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    opacity: 0.8,
                    '&:hover': {
                      opacity: 1,
                    },
                  }}
                >
                  <PlayIcon sx={{ fontSize: 60, color: 'white' }} />
                </Box>
              </CardActionArea>
              <Box
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                }}
              >
                <IconButton
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleBookmark(video.id);
                  }}
                  sx={{
                    color: 'white',
                    bgcolor: 'rgba(0, 0, 0, 0.3)',
                    '&:hover': {
                      bgcolor: 'rgba(0, 0, 0, 0.5)',
                    },
                  }}
                  size="small"
                >
                  {video.bookmarked ? (
                    <BookmarkIcon sx={{ color: 'primary.main' }} />
                  ) : (
                    <BookmarkBorderIcon />
                  )}
                </IconButton>
              </Box>
            </Box>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography gutterBottom variant="h6" component="div" noWrap>
                {video.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {video.timestamp}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {`Location: ${video.location}`}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default VideoResultsList;