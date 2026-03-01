import BaseService, { apiClient, mockResponse } from './baseService';
import API_CONFIG from '../../config/api.config';
import axios from 'axios';

// Test server configuration
const TEST_SERVER_URL = 'http://localhost:8000';

/**
 * License Plate Detection API Service
 * Handles comprehensive license plate detection and tracking using YOLOv8 + EasyOCR
 */
class PlateDetectionService extends BaseService {
  constructor() {
    super(API_CONFIG.endpoints.plates.detect);
    
    // Create a separate axios instance for test server
    this.testClient = axios.create({
      baseURL: TEST_SERVER_URL,
      timeout: 30000,
    });
  }

  /**
   * Detect license plates from uploaded file (image or video)
   * @param {File} file - Image or video file to process
   * @param {string} location - Location where detection was performed
   * @param {boolean} storeResults - Whether to store results in database
   * @returns {Promise} - Response with detection results
   */
  async detectPlates(file, location = 'unknown', storeResults = true) {
    if (API_CONFIG.useMocks) {
      // Generate mock response based on file type
      const isVideo = file.type.startsWith('video/');
      return mockResponse({
        success: true,
        file_type: isVideo ? 'video' : 'image',
        original_filename: file.name,
        location: location,
        processing_timestamp: new Date().toISOString(),
        total_plates_detected: isVideo ? 3 : 1,
        unique_plates: isVideo ? 2 : 1,
        plates_with_text: [
          {
            plate_text: 'MH-12-AB-1234',
            confidence: 0.95,
            bbox: [150, 200, 350, 280],
            timestamp: isVideo ? 5.2 : null
          }
        ],
        processing_time: isVideo ? 12.5 : 2.3,
        database_stored: storeResults
      });
    }

    // Use test server for now
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await this.testClient.post('/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Detection failed');
    }
  }

  /**
   * Get detection history for a specific license plate
   * @param {string} plateText - License plate text to search for
   * @param {number} limit - Maximum number of records to return
   * @returns {Promise} - Response with detection history
   */
  async getPlateHistory(plateText, limit = 50) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        success: true,
        plate_text: plateText,
        total_detections: 5,
        detections: [
          {
            detection_id: 'det_001',
            location: 'main_gate',
            detected_at: new Date(Date.now() - 86400000).toISOString(),
            confidence: 0.94,
            source_type: 'image'
          },
          {
            detection_id: 'det_002',
            location: 'parking_area',
            detected_at: new Date(Date.now() - 172800000).toISOString(),
            confidence: 0.87,
            source_type: 'video'
          }
        ]
      });
    }

    return apiClient.get(API_CONFIG.endpoints.plates.history(plateText), {
      params: { limit }
    });
  }

  /**
   * Get recent license plate detections
   * @param {number} limit - Maximum number of records to return
   * @param {string} location - Optional location filter
   * @returns {Promise} - Response with recent detections
   */
  async getRecentDetections(limit = 50, location = null) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        success: true,
        total_count: 15,
        detections: [
          {
            detection_id: 'det_003',
            plate_text: 'KA-01-XY-5678',
            location: 'main_gate',
            detected_at: new Date(Date.now() - 3600000).toISOString(),
            confidence: 0.91,
            source_type: 'image'
          },
          {
            detection_id: 'det_004',
            plate_text: 'TN-03-CD-9012',
            location: 'loading_dock',
            detected_at: new Date(Date.now() - 7200000).toISOString(),
            confidence: 0.88,
            source_type: 'video'
          }
        ]
      });
    }

    const params = { limit };
    if (location) {
      params.location = location;
    }

    return apiClient.get(API_CONFIG.endpoints.plates.recent, { params });
  }

  /**
   * Get detection statistics
   * @returns {Promise} - Response with statistics
   */
  async getStatistics() {
    try {
      const response = await this.testClient.get('/statistics');
      return {
        total_detections: 0,
        successful_detections: 0,
        average_processing_time: 0,
        unique_plates: 0
      };
    } catch (error) {
      // Return mock statistics if test server doesn't have this endpoint
      return {
        total_detections: 0,
        successful_detections: 0,
        average_processing_time: 0,
        unique_plates: 0
      };
    }
  }

  /**
   * Get detection history
   * @returns {Promise} - Response with history
   */
  async getHistory() {
    // Return empty history for now
    return [];
  }

  /**
   * Verify a license plate detection
   * @param {string} plateId - ID of the plate detection to verify
   * @param {boolean} isVerified - Whether the detection is verified as correct
   * @param {string} correctedText - Optional corrected plate text if OCR was wrong
   * @returns {Promise} - Response with verification result
   */
  async verifyPlateDetection(plateId, isVerified, correctedText = null) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        success: true,
        plate_id: plateId,
        is_verified: isVerified,
        corrected_text: correctedText,
        updated_at: new Date().toISOString()
      });
    }

    const formData = new FormData();
    formData.append('is_verified', isVerified.toString());
    if (correctedText) {
      formData.append('corrected_text', correctedText);
    }

    return apiClient.post(API_CONFIG.endpoints.plates.verify(plateId), formData);
  }

  /**
   * Delete a detection record
   * @param {string} detectionId - ID of the detection to delete
   * @returns {Promise} - Response with deletion result
   */
  async deleteDetection(detectionId) {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        success: true,
        detection_id: detectionId,
        deleted_detection_records: 1,
        deleted_plate_records: 1,
        deleted_at: new Date().toISOString()
      });
    }

    return apiClient.delete(API_CONFIG.endpoints.plates.delete(detectionId));
  }

  /**
   * Check health status of plate detection service
   * @returns {Promise} - Response with health status
   */
  async checkHealth() {
    if (API_CONFIG.useMocks) {
      return mockResponse({
        success: true,
        service: 'License Plate Detection API',
        status: 'healthy',
        components: {
          yolo_model: 'available',
          ocr_reader: 'available',
          database: 'connected'
        },
        timestamp: new Date().toISOString()
      });
    }

    return apiClient.get(API_CONFIG.endpoints.plates.health);
  }

  /**
   * Process video file with polling for results
   * @param {File} videoFile - Video file to process
   * @param {string} location - Location where video was captured
   * @param {Function} onProgress - Callback for progress updates
   * @returns {Promise} - Response with final results
   */
  async processVideoWithPolling(videoFile, location, onProgress = null) {
    try {
      // Start processing
      const response = await this.detectPlates(videoFile, location, true);
      
      if (!response.success) {
        throw new Error(response.error || 'Processing failed');
      }

      // If it's an image, return immediately
      if (response.file_type === 'image') {
        return response;
      }

      // For videos, poll for completion if needed
      // This would be used if the backend supports async processing
      if (onProgress) {
        onProgress(100); // Assume immediate processing for now
      }

      return response;
    } catch (error) {
      throw new Error(`Video processing failed: ${error.message}`);
    }
  }
}

export default new PlateDetectionService();
