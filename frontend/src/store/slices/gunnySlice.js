import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks for API calls
export const fetchGunnyBagCounts = createAsyncThunk(
  'gunny/fetchCounts',
  async (params, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        data: [
          {
            id: '1',
            count: 45,
            location: 'Warehouse A',
            timestamp: '2025-05-01T08:30:00Z',
            confidence_score: 0.96,
            processed_image_url: '/images/processed/gunny_1.jpg'
          },
          {
            id: '2',
            count: 78,
            location: 'Warehouse B',
            timestamp: '2025-05-01T10:15:00Z',
            confidence_score: 0.92,
            processed_image_url: '/images/processed/gunny_2.jpg'
          },
          {
            id: '3',
            count: 32,
            location: 'Loading Dock',
            timestamp: '2025-05-01T12:45:00Z',
            confidence_score: 0.88,
            processed_image_url: '/images/processed/gunny_3.jpg'
          }
        ],
        total: 3
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch gunny bag counts');
    }
  }
);

export const fetchGunnyAnalytics = createAsyncThunk(
  'gunny/fetchAnalytics',
  async (timeRange, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        daily_counts: [
          { date: '2025-04-25', count: 120 },
          { date: '2025-04-26', count: 145 },
          { date: '2025-04-27', count: 135 },
          { date: '2025-04-28', count: 160 },
          { date: '2025-04-29', count: 175 },
          { date: '2025-04-30', count: 190 },
          { date: '2025-05-01', count: 155 }
        ],
        location_distribution: [
          { location: 'Warehouse A', count: 220 },
          { location: 'Warehouse B', count: 310 },
          { location: 'Loading Dock', count: 150 },
          { location: 'Storage Area', count: 180 },
        ],
        total_count: 860,
        average_confidence: 0.91
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch gunny analytics');
    }
  }
);

// Initial state
const initialState = {
  counts: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  analytics: {
    daily_counts: [],
    location_distribution: [],
    total_count: 0,
    average_confidence: 0,
    loading: false,
    error: null
  },
  selectedCount: null,
  realTimeCount: null
};

const gunnySlice = createSlice({
  name: 'gunny',
  initialState,
  reducers: {
    selectCount: (state, action) => {
      state.selectedCount = action.payload;
    },
    clearCountSelection: (state) => {
      state.selectedCount = null;
    },
    updateRealTimeCount: (state, action) => {
      state.realTimeCount = action.payload;
    }
  },
  extraReducers: (builder) => {
    // Gunny bag counts fetching
    builder.addCase(fetchGunnyBagCounts.pending, (state) => {
      state.counts.loading = true;
      state.counts.error = null;
    });
    builder.addCase(fetchGunnyBagCounts.fulfilled, (state, action) => {
      state.counts.list = action.payload.data;
      state.counts.total = action.payload.total;
      state.counts.loading = false;
    });
    builder.addCase(fetchGunnyBagCounts.rejected, (state, action) => {
      state.counts.error = action.payload;
      state.counts.loading = false;
    });

    // Gunny analytics fetching
    builder.addCase(fetchGunnyAnalytics.pending, (state) => {
      state.analytics.loading = true;
      state.analytics.error = null;
    });
    builder.addCase(fetchGunnyAnalytics.fulfilled, (state, action) => {
      state.analytics = {
        ...action.payload,
        loading: false,
        error: null
      };
    });
    builder.addCase(fetchGunnyAnalytics.rejected, (state, action) => {
      state.analytics.error = action.payload;
      state.analytics.loading = false;
    });
  }
});

export const { selectCount, clearCountSelection, updateRealTimeCount } = gunnySlice.actions;
export default gunnySlice.reducer;