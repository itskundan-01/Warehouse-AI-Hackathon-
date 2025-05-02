import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks for API calls
export const fetchInsights = createAsyncThunk(
  'context/fetchInsights',
  async (params, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        data: [
          {
            id: '1',
            insight_type: 'anomaly',
            description: 'Unusual movement pattern detected in Zone B during non-operational hours',
            timestamp: '2025-05-01T02:30:00Z',
            confidence_score: 0.88,
            severity: 'medium',
            source_modules: ['facial', 'context'],
            metadata: {
              zone: 'Zone B',
              camera_ids: ['CAM005', 'CAM006'],
              related_events: ['motion_after_hours', 'unauthorized_access_attempt']
            }
          },
          {
            id: '2',
            insight_type: 'optimization',
            description: 'Gunny bag arrangement optimization possible in Warehouse A to improve space efficiency',
            timestamp: '2025-05-01T10:15:00Z',
            confidence_score: 0.92,
            severity: 'low',
            source_modules: ['gunny', 'context'],
            metadata: {
              location: 'Warehouse A',
              potential_space_saving: '15%',
              recommended_action: 'Rearrangement of stacks in northwest corner'
            }
          },
          {
            id: '3',
            insight_type: 'security',
            description: 'Multiple unknown vehicles spotted near south perimeter within 24 hour period',
            timestamp: '2025-05-01T14:45:00Z',
            confidence_score: 0.85,
            severity: 'high',
            source_modules: ['vehicle', 'context'],
            metadata: {
              location: 'South Perimeter',
              vehicle_count: 3,
              timestamps: ['2025-04-30T22:10:00Z', '2025-05-01T06:30:00Z', '2025-05-01T13:15:00Z'],
              recommended_action: 'Increase security patrol in area'
            }
          }
        ],
        total: 3
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch contextual insights');
    }
  }
);

export const fetchPredictiveAnalytics = createAsyncThunk(
  'context/fetchPredictiveAnalytics',
  async (timeRange, { rejectWithValue }) => {
    try {
      // Mock data for development
      return {
        inventory_forecast: [
          { date: '2025-05-02', predicted_count: 890 },
          { date: '2025-05-03', predicted_count: 920 },
          { date: '2025-05-04', predicted_count: 905 },
          { date: '2025-05-05', predicted_count: 950 },
          { date: '2025-05-06', predicted_count: 980 },
          { date: '2025-05-07', predicted_count: 1020 },
          { date: '2025-05-08', predicted_count: 1050 }
        ],
        security_risk_forecast: [
          { date: '2025-05-02', risk_level: 'low' },
          { date: '2025-05-03', risk_level: 'low' },
          { date: '2025-05-04', risk_level: 'low' },
          { date: '2025-05-05', risk_level: 'medium' },
          { date: '2025-05-06', risk_level: 'medium' },
          { date: '2025-05-07', risk_level: 'low' },
          { date: '2025-05-08', risk_level: 'low' }
        ],
        vehicle_traffic_forecast: [
          { date: '2025-05-02', predicted_entries: 35, predicted_exits: 32 },
          { date: '2025-05-03', predicted_entries: 18, predicted_exits: 20 },
          { date: '2025-05-04', predicted_entries: 15, predicted_exits: 14 },
          { date: '2025-05-05', predicted_entries: 40, predicted_exits: 38 },
          { date: '2025-05-06', predicted_entries: 45, predicted_exits: 42 },
          { date: '2025-05-07', predicted_entries: 38, predicted_exits: 40 },
          { date: '2025-05-08', predicted_entries: 36, predicted_exits: 35 }
        ],
        model_accuracy: 0.89,
        last_updated: '2025-05-01T18:00:00Z'
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch predictive analytics');
    }
  }
);

export const generateReport = createAsyncThunk(
  'context/generateReport',
  async (params, { rejectWithValue }) => {
    try {
      // Mock data for development - simulating a report generation API call
      // This would normally return a URL or file path to the generated report
      return {
        report_id: 'REP' + Date.now(),
        report_url: '/reports/contextual_intelligence_report_20250501.pdf',
        generated_at: new Date().toISOString(),
        status: 'completed',
        report_type: params.reportType,
        time_range: params.timeRange
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to generate report');
    }
  }
);

// Initial state
const initialState = {
  insights: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  predictiveAnalytics: {
    inventory_forecast: [],
    security_risk_forecast: [],
    vehicle_traffic_forecast: [],
    model_accuracy: 0,
    last_updated: null,
    loading: false,
    error: null
  },
  reportGeneration: {
    report: null,
    loading: false,
    error: null
  },
  selectedInsight: null
};

const contextSlice = createSlice({
  name: 'context',
  initialState,
  reducers: {
    selectInsight: (state, action) => {
      state.selectedInsight = action.payload;
    },
    clearInsightSelection: (state) => {
      state.selectedInsight = null;
    },
    clearReportData: (state) => {
      state.reportGeneration = {
        report: null,
        loading: false,
        error: null
      };
    }
  },
  extraReducers: (builder) => {
    // Insights fetching
    builder.addCase(fetchInsights.pending, (state) => {
      state.insights.loading = true;
      state.insights.error = null;
    });
    builder.addCase(fetchInsights.fulfilled, (state, action) => {
      state.insights.list = action.payload.data;
      state.insights.total = action.payload.total;
      state.insights.loading = false;
    });
    builder.addCase(fetchInsights.rejected, (state, action) => {
      state.insights.error = action.payload;
      state.insights.loading = false;
    });

    // Predictive analytics fetching
    builder.addCase(fetchPredictiveAnalytics.pending, (state) => {
      state.predictiveAnalytics.loading = true;
      state.predictiveAnalytics.error = null;
    });
    builder.addCase(fetchPredictiveAnalytics.fulfilled, (state, action) => {
      state.predictiveAnalytics = {
        ...action.payload,
        loading: false,
        error: null
      };
    });
    builder.addCase(fetchPredictiveAnalytics.rejected, (state, action) => {
      state.predictiveAnalytics.error = action.payload;
      state.predictiveAnalytics.loading = false;
    });

    // Report generation
    builder.addCase(generateReport.pending, (state) => {
      state.reportGeneration.loading = true;
      state.reportGeneration.error = null;
    });
    builder.addCase(generateReport.fulfilled, (state, action) => {
      state.reportGeneration.report = action.payload;
      state.reportGeneration.loading = false;
    });
    builder.addCase(generateReport.rejected, (state, action) => {
      state.reportGeneration.error = action.payload;
      state.reportGeneration.loading = false;
    });
  }
});

export const { selectInsight, clearInsightSelection, clearReportData } = contextSlice.actions;
export default contextSlice.reducer;