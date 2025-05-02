import BaseService, { apiClient, mockResponse } from './baseService';
import API_CONFIG from '../../config/api.config';
import vehicleMockData from './mocks/vehicleMockData';

/**
 * Vehicle Recognition API Service
 * Handles API calls related to vehicle detection, tracking and authorization
 */
class VehicleService extends BaseService {
  constructor() {
    super(API_CONFIG.endpoints.vehicle.vehicles, vehicleMockData);
  }

  /**
   * Detect and recognize vehicle from an image
   * @param {File} image - Image file containing vehicle/license plate
   * @param {string} location - Location where the image was captured
   * @returns {Promise} - Response with detection results
   */
  detectVehicle(image, location) {
    if (API_CONFIG.useMocks) {
      return mockResponse(vehicleMockData.detection);
    }
    
    const formData = new FormData();
    formData.append('image', image);
    formData.append('location', location);
    
    return apiClient.post(API_CONFIG.endpoints.vehicle.detect, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }

  /**
   * Get list of vehicles with optional filtering
   * @param {Object} params - Query parameters
   * @param {string} params.status - Filter by status (authorized, unauthorized, pending_review)
   * @param {string} params.type - Filter by vehicle type
   * @param {string} params.licensePlate - Search by license plate
   * @param {number} params.page - Page number for pagination (1-based)
   * @param {number} params.limit - Maximum number of records to return
   * @returns {Promise} - Response with list of vehicles
   */
  getVehicles(params = {}) {
    if (API_CONFIG.useMocks) {
      // Filter mock data based on params if provided
      let filteredData = [...vehicleMockData.vehicles.data];
      
      if (params.status) {
        filteredData = filteredData.filter(item => item.status === params.status);
      }
      
      if (params.type) {
        filteredData = filteredData.filter(item => item.vehicle_type === params.type);
      }
      
      if (params.licensePlate) {
        filteredData = filteredData.filter(
          item => item.license_plate.toLowerCase().includes(params.licensePlate.toLowerCase())
        );
      }
      
      // Simple pagination
      const page = params.page || 1;
      const limit = params.limit || 10;
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      
      return mockResponse({
        data: filteredData.slice(startIndex, endIndex),
        total: filteredData.length,
        page,
        limit
      });
    }
    
    return apiClient.get(API_CONFIG.endpoints.vehicle.vehicles, { params });
  }

  /**
   * Get vehicle details by ID
   * @param {string} vehicleId - UUID of the vehicle
   * @returns {Promise} - Response with vehicle details
   */
  getVehicleById(vehicleId) {
    if (API_CONFIG.useMocks) {
      const vehicle = vehicleMockData.vehicles.data.find(v => v.id === vehicleId);
      return mockResponse(vehicle || { error: 'Vehicle not found' });
    }
    
    return apiClient.get(API_CONFIG.endpoints.vehicle.vehicleById(vehicleId));
  }

  /**
   * Get entries/logs for a specific vehicle
   * @param {string} vehicleId - UUID of the vehicle
   * @param {Object} params - Query parameters for pagination
   * @returns {Promise} - Response with list of entries
   */
  getVehicleEntries(vehicleId, params = {}) {
    if (API_CONFIG.useMocks) {
      // Generate mock entries for this vehicle
      const entries = vehicleMockData.entries.data.map(entry => ({
        ...entry,
        vehicle_id: vehicleId
      }));
      
      return mockResponse({
        data: entries,
        total: entries.length,
        page: 1,
        limit: 10
      });
    }
    
    return apiClient.get(API_CONFIG.endpoints.vehicle.entries(vehicleId), { params });
  }

  /**
   * Update vehicle authorization status
   * @param {string} vehicleId - UUID of the vehicle
   * @param {string} status - New status (authorized, unauthorized)
   * @param {string} notes - Optional notes for the status change
   * @returns {Promise} - Response with updated vehicle
   */
  updateVehicleStatus(vehicleId, status, notes = '') {
    if (API_CONFIG.useMocks) {
      const vehicle = vehicleMockData.vehicles.data.find(v => v.id === vehicleId);
      if (!vehicle) {
        return mockResponse({ error: 'Vehicle not found' }, 404);
      }
      
      return mockResponse({
        ...vehicle,
        status,
        notes: notes || vehicle.notes,
        updated_at: new Date().toISOString()
      });
    }
    
    return apiClient.put(API_CONFIG.endpoints.vehicle.authorize(vehicleId), { status, notes });
  }

  /**
   * Get list of unauthorized vehicles
   * @param {Object} params - Query parameters
   * @returns {Promise} - Response with list of unauthorized vehicles
   */
  getUnauthorizedVehicles(params = {}) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        data: vehicleMockData.unauthorized,
        total: vehicleMockData.unauthorized.length,
        page: 1,
        limit: 10
      });
    }
    
    return this.getVehicles({ ...params, status: 'unauthorized' });
  }

  /**
   * Get analytics data for vehicles
   * @param {Object} params - Query parameters
   * @param {string} params.startDate - Optional start date filter (ISO format)
   * @param {string} params.endDate - Optional end date filter (ISO format)
   * @returns {Promise} - Response with analytics data
   */
  getAnalytics(params = {}) {
    if (API_CONFIG.useMocks) {
      return mockResponse(vehicleMockData.analytics);
    }
    
    return apiClient.get(`${this.endpoint}/analytics`, { params });
  }

  /**
   * Register a new vehicle in the system
   * @param {Object} vehicleData - Vehicle data to register
   * @param {File} image - Optional image of the vehicle
   * @returns {Promise} - Response with the created vehicle
   */
  registerVehicle(vehicleData, image = null) {
    if (API_CONFIG.useMocks) {
      const newVehicle = {
        id: `v-${Date.now()}`,
        ...vehicleData,
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        entry_count: 1,
        confidence_score: 0.95,
        created_at: new Date().toISOString()
      };
      
      return mockResponse(newVehicle);
    }
    
    const formData = new FormData();
    
    // Add vehicle data
    Object.keys(vehicleData).forEach(key => {
      formData.append(key, vehicleData[key]);
    });
    
    // Add image if provided
    if (image) {
      formData.append('image', image);
    }
    
    return apiClient.post(this.endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
}

export default new VehicleService();