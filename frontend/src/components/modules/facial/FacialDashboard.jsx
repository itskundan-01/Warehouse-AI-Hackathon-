import React, { useState, useEffect } from 'react';
import FaceCapture from './FaceCapture/FaceCapture';
import FaceRecognition from './FaceRecognition/FaceRecognition';
import FaceRegistration from './FaceRegistration/FaceRegistration';
import FaceVerification from './FaceVerification/FaceVerification';

/**
 * Main dashboard component for the facial recognition module
 */
const FacialDashboard = () => {
  const [activeTab, setActiveTab] = useState('recognition');
  const [recognitionData, setRecognitionData] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch initial data when component mounts
  useEffect(() => {
    const fetchInitialData = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API call
        const response = await fetch('/api/facial/recent');
        const data = await response.json();
        setRecognitionData(data);
      } catch (error) {
        console.error('Error fetching facial recognition data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'capture':
        return <FaceCapture />;
      case 'registration':
        return <FaceRegistration />;
      case 'verification':
        return <FaceVerification />;
      case 'recognition':
      default:
        return <FaceRecognition data={recognitionData} loading={loading} />;
    }
  };

  return (
    <div className="facial-dashboard">
      <h2>Facial Recognition System</h2>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'recognition' ? 'active' : ''}`}
          onClick={() => setActiveTab('recognition')}
        >
          Recognition
        </button>
        <button 
          className={`tab ${activeTab === 'verification' ? 'active' : ''}`}
          onClick={() => setActiveTab('verification')}
        >
          Verification
        </button>
        <button 
          className={`tab ${activeTab === 'registration' ? 'active' : ''}`}
          onClick={() => setActiveTab('registration')}
        >
          Registration
        </button>
        <button 
          className={`tab ${activeTab === 'capture' ? 'active' : ''}`}
          onClick={() => setActiveTab('capture')}
        >
          Capture
        </button>
      </div>
      
      <div className="tab-content">
        {renderActiveTab()}
      </div>
    </div>
  );
};

export default FacialDashboard;