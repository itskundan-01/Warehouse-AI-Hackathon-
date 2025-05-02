import BaseService, { apiClient, mockResponse } from './baseService';
import API_CONFIG from '../../config/api.config';

// Mock data for development
const mockData = {
  count: {
    bag_count: 67,
    confidence_score: 0.92,
    image_url: '/mock-images/processed_gunny.jpg',
    location: 'Warehouse A',
    timestamp: new Date().toISOString()
  },
  list: {
    data: [
      {
        id: '1',
        count: 45,
        location: 'Warehouse A',
        timestamp: '2025-05-01T08:30:00Z',
        confidence_score: 0.96,
        processed_image_url: '/mock-images/gunny_1.jpg'
      },
      {
        id: '2',
        count: 78,
        location: 'Warehouse B',
        timestamp: '2025-05-01T10:15:00Z',
        confidence_score: 0.92,
        processed_image_url: '/mock-images/gunny_2.jpg'
      },
      {
        id: '3',
        count: 32,
        location: 'Loading Dock',
        timestamp: '2025-05-01T12:45:00Z',
        confidence_score: 0.88,
        processed_image_url: '/mock-images/gunny_3.jpg'
      }
    ],
    total: 3,
    page: 1,
    limit: 10
  },
  analytics: {
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
  }
};

/**
 * Gunny Bag Counter API Service
 * Handles API calls related to gunny bag counting and tracking
 */
class GunnyService extends BaseService {
  constructor() {
    super(API_CONFIG.endpoints.gunny.counts, mockData);
  }

  /**
   * Count gunny bags from an uploaded image
   * @param {File} image - Image file containing gunny bags
   * @param {string} location - Location where the image was taken
   * @returns {Promise} - Response with count results
   */
  countBags(image, location) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        ...mockData.count,
        location
      });
    }
    
    const formData = new FormData();
    formData.append('image', image);
    formData.append('location', location);
    
    return apiClient.post(API_CONFIG.endpoints.gunny.count, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }

  /**
   * Get list of gunny bag counts with optional filtering
   * @param {Object} params - Query parameters
   * @param {string} params.location - Optional location filter
   * @param {string} params.startDate - Optional start date filter (ISO format)
   * @param {string} params.endDate - Optional end date filter (ISO format)
   * @param {number} params.page - Page number for pagination (1-based)
   * @param {number} params.limit - Maximum number of records to return
   * @returns {Promise} - Response with list of counts
   */
  getCounts(params = {}) {
    if (API_CONFIG.useMocks) {
      // Filter mock data based on location if provided
      if (params.location) {
        const filteredData = mockData.list.data.filter(
          item => item.location.toLowerCase() === params.location.toLowerCase()
        );
        return mockResponse({
          data: filteredData,
          total: filteredData.length,
          page: 1,
          limit: 10
        });
      }
      return mockResponse(mockData.list);
    }
    
    return apiClient.get(API_CONFIG.endpoints.gunny.counts, { params });
  }

  /**
   * Get specific gunny bag count by ID
   * @param {string} countId - UUID of the count record
   * @returns {Promise} - Response with count details
   */
  getCountById(countId) {
    if (API_CONFIG.useMocks) {
      const item = mockData.list.data.find(i => i.id === countId);
      return mockResponse(item || { error: 'Count not found' });
    }
    
    return apiClient.get(API_CONFIG.endpoints.gunny.countById(countId));
  }

  /**
   * Get latest gunny bag count for a specific location
   * @param {string} location - Location identifier
   * @returns {Promise} - Response with the latest count
   */
  getLatestByLocation(location) {
    if (API_CONFIG.useMocks) {
      const items = mockData.list.data.filter(
        item => item.location.toLowerCase() === location.toLowerCase()
      );
      // Sort by timestamp descending
      items.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      return mockResponse(items[0] || { error: 'No counts found for this location' });
    }
    
    return apiClient.get(API_CONFIG.endpoints.gunny.latest(location));
  }

  /**
   * Get analytics data for gunny bag counts
   * @param {Object} params - Query parameters
   * @param {string} params.startDate - Optional start date filter (ISO format)
   * @param {string} params.endDate - Optional end date filter (ISO format)
   * @returns {Promise} - Response with analytics data
   */
  getAnalytics(params = {}) {
    if (API_CONFIG.useMocks) {
      return mockResponse(mockData.analytics);
    }
    
    return apiClient.get(`${this.endpoint}/analytics`, { params });
  }
}

export default new GunnyService();