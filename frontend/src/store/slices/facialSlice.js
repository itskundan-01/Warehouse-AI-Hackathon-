import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import facialRecognitionService from '../../services/api/facialService';

// Async thunks for API calls
export const fetchPersonnel = createAsyncThunk(
  'facial/fetchPersonnel',
  async (params, { rejectWithValue }) => {
    try {
      // Call the actual API service
      const response = await facialRecognitionService.getPersonnel(params);
      return response;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch personnel data');
    }
  }
);

export const fetchAuthHistory = createAsyncThunk(
  'facial/fetchAuthHistory',
  async (params, { rejectWithValue }) => {
    try {
      // Call the actual API service
      const response = await facialRecognitionService.getAuthHistory(params);
      return response;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch authentication history');
    }
  }
);

export const fetchUnauthorizedAccess = createAsyncThunk(
  'facial/fetchUnauthorizedAccess',
  async (params, { rejectWithValue }) => {
    try {
      // Call the actual API service
      const response = await facialRecognitionService.getUnauthorizedAccess(params);
      return response;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch unauthorized access data');
    }
  }
);

export const registerFace = createAsyncThunk(
  'facial/registerFace',
  async (data, { rejectWithValue }) => {
    try {
      const response = await facialRecognitionService.registerFace(data);
      return response;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to register face');
    }
  }
);

export const authenticateFace = createAsyncThunk(
  'facial/authenticateFace',
  async (data, { rejectWithValue }) => {
    try {
      const response = await facialRecognitionService.authenticateFace(data);
      return response;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to authenticate face');
    }
  }
);

// Initial state
const initialState = {
  personnel: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  authHistory: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  unauthorizedAccess: {
    list: [],
    total: 0,
    loading: false,
    error: null
  },
  faceAuth: {
    result: null,
    loading: false,
    error: null
  },
  faceRegistration: {
    success: false,
    loading: false,
    error: null
  },
  selectedPersonnel: null
};

const facialSlice = createSlice({
  name: 'facial',
  initialState,
  reducers: {
    selectPersonnel: (state, action) => {
      state.selectedPersonnel = action.payload;
    },
    clearPersonnelSelection: (state) => {
      state.selectedPersonnel = null;
    },
    clearAuthResult: (state) => {
      state.faceAuth.result = null;
      state.faceAuth.error = null;
    },
    clearRegistrationStatus: (state) => {
      state.faceRegistration.success = false;
      state.faceRegistration.error = null;
    }
  },
  extraReducers: (builder) => {
    // Personnel fetching
    builder.addCase(fetchPersonnel.pending, (state) => {
      state.personnel.loading = true;
      state.personnel.error = null;
    });
    builder.addCase(fetchPersonnel.fulfilled, (state, action) => {
      state.personnel.loading = false;
      state.personnel.list = action.payload.data || [];
      state.personnel.total = action.payload.total || action.payload.data?.length || 0;
    });
    builder.addCase(fetchPersonnel.rejected, (state, action) => {
      state.personnel.loading = false;
      state.personnel.error = action.payload;
    });

    // Authentication history fetching
    builder.addCase(fetchAuthHistory.pending, (state) => {
      state.authHistory.loading = true;
      state.authHistory.error = null;
    });
    builder.addCase(fetchAuthHistory.fulfilled, (state, action) => {
      state.authHistory.loading = false;
      state.authHistory.list = action.payload.results || [];
      state.authHistory.total = action.payload.count || 0;
    });
    builder.addCase(fetchAuthHistory.rejected, (state, action) => {
      state.authHistory.loading = false;
      state.authHistory.error = action.payload;
    });

    // Unauthorized access fetching
    builder.addCase(fetchUnauthorizedAccess.pending, (state) => {
      state.unauthorizedAccess.loading = true;
      state.unauthorizedAccess.error = null;
    });
    builder.addCase(fetchUnauthorizedAccess.fulfilled, (state, action) => {
      state.unauthorizedAccess.loading = false;
      state.unauthorizedAccess.list = action.payload.results || [];
      state.unauthorizedAccess.total = action.payload.count || 0;
    });
    builder.addCase(fetchUnauthorizedAccess.rejected, (state, action) => {
      state.unauthorizedAccess.loading = false;
      state.unauthorizedAccess.error = action.payload;
    });

    // Face registration
    builder.addCase(registerFace.pending, (state) => {
      state.faceRegistration.loading = true;
      state.faceRegistration.error = null;
      state.faceRegistration.success = false;
    });
    builder.addCase(registerFace.fulfilled, (state) => {
      state.faceRegistration.loading = false;
      state.faceRegistration.success = true;
    });
    builder.addCase(registerFace.rejected, (state, action) => {
      state.faceRegistration.loading = false;
      state.faceRegistration.error = action.payload;
    });

    // Face authentication
    builder.addCase(authenticateFace.pending, (state) => {
      state.faceAuth.loading = true;
      state.faceAuth.error = null;
      state.faceAuth.result = null;
    });
    builder.addCase(authenticateFace.fulfilled, (state, action) => {
      state.faceAuth.loading = false;
      state.faceAuth.result = action.payload;
    });
    builder.addCase(authenticateFace.rejected, (state, action) => {
      state.faceAuth.loading = false;
      state.faceAuth.error = action.payload;
    });
  }
});

export const { 
  selectPersonnel, 
  clearPersonnelSelection, 
  clearAuthResult, 
  clearRegistrationStatus 
} = facialSlice.actions;

export default facialSlice.reducer;