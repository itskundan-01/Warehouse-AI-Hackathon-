import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks for API calls
export const fetchVehicleRecords = createAsyncThunk(
  'vehicle/fetchRecords',
  async (params, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        data: [
          {
            id: '1',
            vehicle_number: 'MH20AB1234',
            timestamp: '2025-05-01T09:30:00Z',
            location: 'Main Gate',
            direction: 'in',
            vehicle_type: 'Truck',
            confidence_score: 0.95,
            image_path: '/images/vehicles/veh_1.jpg'
          },
          {
            id: '2',
            vehicle_number: 'UP16CD5678',
            timestamp: '2025-05-01T10:15:00Z',
            location: 'Main Gate',
            direction: 'out',
            vehicle_type: 'Truck',
            confidence_score: 0.92,
            image_path: '/images/vehicles/veh_2.jpg'
          },
          {
            id: '3',
            vehicle_number: 'DL09EF9012',
            timestamp: '2025-05-01T13:45:00Z',
            location: 'Delivery Bay',
            direction: 'in',
            vehicle_type: 'Van',
            confidence_score: 0.89,
            image_path: '/images/vehicles/veh_3.jpg'
          }
        ],
        total: 3
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch vehicle records');
    }
  }
);

export const fetchVehicleAnalytics = createAsyncThunk(
  'vehicle/fetchAnalytics',
  async (timeRange, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        vehicle_flow: [
          { date: '2025-04-25', in: 25, out: 22 },
          { date: '2025-04-26', in: 18, out: 20 },
          { date: '2025-04-27', in: 15, out: 13 },
          { date: '2025-04-28', in: 30, out: 28 },
          { date: '2025-04-29', in: 35, out: 32 },
          { date: '2025-04-30', in: 28, out: 30 },
          { date: '2025-05-01', in: 32, out: 27 }
        ],
        vehicle_types: [
          { type: 'Truck', count: 85 },
          { type: 'Van', count: 45 },
          { type: 'Car', count: 28 },
          { type: 'Other', count: 15 },
        ],
        total_entries: 183,
        total_exits: 172,
        average_confidence: 0.93
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch vehicle analytics');
    }
  }
);

export const fetchUnauthorizedVehicles = createAsyncThunk(
  'vehicle/fetchUnauthorizedVehicles',
  async (params, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        data: [
          {
            id: '1',
            vehicle_number: 'HR51GH9876',
            timestamp: '2025-05-01T08:15:00Z',
            location: 'Side Gate',
            direction: 'attempted_entry',
            confidence_score: 0.87,
            image_path: '/images/vehicles/unauth_1.jpg',
            reason: 'Not in authorized list'
          },
          {
            id: '2',
            vehicle_number: 'KA03JK4321',
            timestamp: '2025-04-30T17:45:00Z',
            location: 'Main Gate',
            direction: 'attempted_entry',
            confidence_score: 0.91,
            image_path: '/images/vehicles/unauth_2.jpg',
            reason: 'Access expired'
          }
        ],
        total: 2
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch unauthorized vehicles');
    }
  }
);

// Initial state
const initialState = {
  records: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  analytics: {
    vehicle_flow: [],
    vehicle_types: [],
    total_entries: 0,
    total_exits: 0,
    average_confidence: 0,
    loading: false,
    error: null
  },
  unauthorizedVehicles: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  selectedVehicle: null,
  realTimeDetection: null
};

const vehicleSlice = createSlice({
  name: 'vehicle',
  initialState,
  reducers: {
    selectVehicle: (state, action) => {
      state.selectedVehicle = action.payload;
    },
    clearVehicleSelection: (state) => {
      state.selectedVehicle = null;
    },
    updateRealTimeDetection: (state, action) => {
      state.realTimeDetection = action.payload;
    }
  },
  extraReducers: (builder) => {
    // Vehicle records fetching
    builder.addCase(fetchVehicleRecords.pending, (state) => {
      state.records.loading = true;
      state.records.error = null;
    });
    builder.addCase(fetchVehicleRecords.fulfilled, (state, action) => {
      state.records.list = action.payload.data;
      state.records.total = action.payload.total;
      state.records.loading = false;
    });
    builder.addCase(fetchVehicleRecords.rejected, (state, action) => {
      state.records.error = action.payload;
      state.records.loading = false;
    });

    // Vehicle analytics fetching
    builder.addCase(fetchVehicleAnalytics.pending, (state) => {
      state.analytics.loading = true;
      state.analytics.error = null;
    });
    builder.addCase(fetchVehicleAnalytics.fulfilled, (state, action) => {
      state.analytics = {
        ...action.payload,
        loading: false,
        error: null
      };
    });
    builder.addCase(fetchVehicleAnalytics.rejected, (state, action) => {
      state.analytics.error = action.payload;
      state.analytics.loading = false;
    });

    // Unauthorized vehicles fetching
    builder.addCase(fetchUnauthorizedVehicles.pending, (state) => {
      state.unauthorizedVehicles.loading = true;
      state.unauthorizedVehicles.error = null;
    });
    builder.addCase(fetchUnauthorizedVehicles.fulfilled, (state, action) => {
      state.unauthorizedVehicles.list = action.payload.data;
      state.unauthorizedVehicles.total = action.payload.total;
      state.unauthorizedVehicles.loading = false;
    });
    builder.addCase(fetchUnauthorizedVehicles.rejected, (state, action) => {
      state.unauthorizedVehicles.error = action.payload;
      state.unauthorizedVehicles.loading = false;
    });
  }
});

export const { selectVehicle, clearVehicleSelection, updateRealTimeDetection } = vehicleSlice.actions;
export default vehicleSlice.reducer;