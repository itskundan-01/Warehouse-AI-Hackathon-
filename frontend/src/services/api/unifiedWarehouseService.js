import { apiClient, webSocketService } from './baseService';

/**
 * Unified Warehouse AI Service
 * Handles all AI modules communication with the backend
 */
class UnifiedWarehouseService {
  constructor() {
    this.isConnected = false;
    this.subscribers = new Map();
  }

  /**
   * Initialize real-time connection
   */
  initialize() {
    if (!this.isConnected) {
      webSocketService.connect();
      this.setupEventListeners();
      this.isConnected = true;
    }
  }

  /**
   * Setup WebSocket event listeners
   */
  setupEventListeners() {
    webSocketService.on('connected', (data) => {
      console.log('🏭 Warehouse AI connected');
      this.notifySubscribers('connected', data);
    });

    webSocketService.on('detection', (data) => {
      console.log('🔍 New detection:', data);
      this.notifySubscribers('detection', data);
      this.notifySubscribers(`${data.module}_detection`, data);
    });

    webSocketService.on('error', (data) => {
      console.error('❌ Warehouse AI error:', data);
      this.notifySubscribers('error', data);
    });
  }

  /**
   * Subscribe to events
   */
  subscribe(event, callback) {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, []);
    }
    this.subscribers.get(event).push(callback);
  }

  /**
   * Unsubscribe from events
   */
  unsubscribe(event, callback) {
    if (this.subscribers.has(event)) {
      const callbacks = this.subscribers.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Notify subscribers
   */
  notifySubscribers(event, data) {
    if (this.subscribers.has(event)) {
      this.subscribers.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Subscriber error:', error);
        }
      });
    }
  }

  /**
   * Process file with unified AI modules
   */
  async processFile(file, modules = ['face', 'plate', 'gunny', 'contextual'], warehouse = 'default') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('modules', modules.join(','));
      formData.append('warehouse', warehouse);

      const response = await apiClient.post('/api/process/unified', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Unified processing error:', error);
      throw error;
    }
  }

  /**
   * Face Recognition Module
   */
  async recognizeFaces(file, warehouse = 'default') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('warehouse', warehouse);

      const response = await apiClient.post('/api/face/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Face recognition error:', error);
      throw error;
    }
  }

  /**
   * License Plate Detection Module
   */
  async detectPlates(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/api/plate/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Plate detection error:', error);
      throw error;
    }
  }

  /**
   * Gunny Bag Counting Module
   */
  async countGunnyBags(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/api/gunny/count', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Gunny counting error:', error);
      throw error;
    }
  }

  /**
   * Contextual Intelligence Module
   */
  async analyzeContext(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/api/contextual/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Contextual analysis error:', error);
      throw error;
    }
  }

  /**
   * Get recent detections
   */
  async getRecentDetections() {
    try {
      const response = await apiClient.get('/api/detections/recent');
      return response.data;
    } catch (error) {
      console.error('Get recent detections error:', error);
      throw error;
    }
  }

  /**
   * Get system status
   */
  async getSystemStatus() {
    try {
      const response = await apiClient.get('/api/status');
      return response.data;
    } catch (error) {
      console.error('Get system status error:', error);
      throw error;
    }
  }

  /**
   * Start camera stream
   */
  startCameraStream() {
    webSocketService.send({
      type: 'start_camera'
    });
  }

  /**
   * Stop camera stream
   */
  stopCameraStream() {
    webSocketService.send({
      type: 'stop_camera'
    });
  }

  /**
   * Disconnect service
   */
  disconnect() {
    webSocketService.disconnect();
    this.isConnected = false;
  }
}

// Create singleton instance
export const unifiedWarehouseService = new UnifiedWarehouseService();

export default unifiedWarehouseService;
