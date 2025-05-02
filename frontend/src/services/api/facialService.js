import BaseService, { apiClient } from './baseService';

/**
 * Facial Recognition API Service
 * Handles API calls related to facial recognition and personnel management
 */
class FacialService extends BaseService {
  constructor() {
    super('/facial');
  }

  /**
   * Register a new personnel with facial recognition
   * @param {Object} data - Personnel data with face image
   * @param {string} data.employeeId - Employee ID
   * @param {string} data.name - Full name
   * @param {string} data.department - Department
   * @param {number} data.accessLevel - Access level
   * @param {string} data.faceImageBase64 - Base64 encoded face image
   * @returns {Promise} - Response with registration result
   */
  registerPersonnel(data) {
    return apiClient.post(`${this.endpoint}/personnel`, data);
  }

  /**
   * Get list of personnel with optional filtering
   * @param {Object} params - Query parameters
   * @param {string} params.department - Optional department filter
   * @param {boolean} params.isActive - Whether to include only active personnel
   * @returns {Promise} - Response with list of personnel
   */
  getPersonnel(params = {}) {
    return apiClient.get(`${this.endpoint}/personnel`, { params });
  }

  /**
   * Get details for a specific personnel by employee ID
   * @param {string} employeeId - Employee ID
   * @returns {Promise} - Response with personnel details
   */
  getPersonnelById(employeeId) {
    return apiClient.get(`${this.endpoint}/personnel/${employeeId}`);
  }

  /**
   * Update personnel information
   * @param {string} employeeId - Employee ID
   * @param {Object} data - Updated personnel data
   * @returns {Promise} - Response with update result
   */
  updatePersonnel(employeeId, data) {
    return apiClient.put(`${this.endpoint}/personnel/${employeeId}`, data);
  }

  /**
   * Deactivate personnel record
   * @param {string} employeeId - Employee ID
   * @returns {Promise} - Response with deactivation result
   */
  deactivatePersonnel(employeeId) {
    return apiClient.delete(`${this.endpoint}/personnel/${employeeId}`);
  }

  /**
   * Authenticate a face against registered personnel
   * @param {Object} data - Authentication request data
   * @param {string} data.faceImageBase64 - Base64 encoded face image
   * @param {string} data.location - Authentication location
   * @param {string} data.cameraId - Camera ID
   * @returns {Promise} - Response with authentication result
   */
  authenticateFace(data) {
    return apiClient.post(`${this.endpoint}/authenticate`, data);
  }

  /**
   * Get authentication history with optional filtering
   * @param {Object} data - History request parameters
   * @param {string} data.employeeId - Optional employee ID filter
   * @param {string} data.location - Optional location filter
   * @param {Date} data.startTime - Optional start time filter
   * @param {Date} data.endTime - Optional end time filter
   * @param {number} data.limit - Maximum number of results
   * @returns {Promise} - Response with authentication history
   */
  getAuthHistory(data) {
    return apiClient.post(`${this.endpoint}/history`, data);
  }

  /**
   * Get unauthorized access attempts
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to look back
   * @param {string} params.location - Optional location filter
   * @returns {Promise} - Response with unauthorized access attempts
   */
  getUnauthorizedAccess(params = {}) {
    return apiClient.get(`${this.endpoint}/unauthorized`, { params });
  }

  /**
   * Synchronize database with face recognizer
   * @returns {Promise} - Response with synchronization result
   */
  syncDatabase() {
    return apiClient.post(`${this.endpoint}/sync`);
  }
}

export default new FacialService();