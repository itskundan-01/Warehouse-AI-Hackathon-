/**
 * Mock data for Vehicle Recognition module
 * Used during development when backend endpoints aren't available
 */

// Helper to generate random timestamps within a range
const randomDate = (start, end) => {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime())).toISOString();
};

// Vehicle status options
const STATUS_OPTIONS = ['authorized', 'unauthorized', 'pending_review'];

// Vehicle type options
const VEHICLE_TYPES = ['truck', 'car', 'van', 'motorcycle', 'forklift'];

// License plate formats for different regions
const generateLicensePlate = () => {
  const formats = [
    // Format: ABC 1234
    () => {
      const letters = 'ABCDEFGHJKLMNPRSTUVWXYZ';
      const prefix = Array(3).fill().map(() => letters.charAt(Math.floor(Math.random() * letters.length))).join('');
      const number = Math.floor(1000 + Math.random() * 9000);
      return `${prefix} ${number}`;
    },
    // Format: AB 12 CDE
    () => {
      const letters1 = 'ABCDEFGHJKLMNPRSTUVWXYZ';
      const letters2 = 'ABCDEFGHJKLMNPRSTUVWXYZ';
      const prefix = Array(2).fill().map(() => letters1.charAt(Math.floor(Math.random() * letters1.length))).join('');
      const number = Math.floor(10 + Math.random() * 90);
      const suffix = Array(3).fill().map(() => letters2.charAt(Math.floor(Math.random() * letters2.length))).join('');
      return `${prefix} ${number} ${suffix}`;
    }
  ];
  
  const formatIndex = Math.floor(Math.random() * formats.length);
  return formats[formatIndex]();
};

// Generate a list of vehicles
const generateVehicles = (count) => {
  const vehicles = [];
  
  for (let i = 0; i < count; i++) {
    const licensePlate = generateLicensePlate();
    const status = STATUS_OPTIONS[Math.floor(Math.random() * STATUS_OPTIONS.length)];
    const vehicleType = VEHICLE_TYPES[Math.floor(Math.random() * VEHICLE_TYPES.length)];
    
    vehicles.push({
      id: `v-${i + 1}`,
      license_plate: licensePlate,
      status: status,
      vehicle_type: vehicleType,
      first_seen: randomDate(new Date('2025-01-01'), new Date('2025-04-30')),
      last_seen: randomDate(new Date('2025-05-01'), new Date()),
      entry_count: Math.floor(1 + Math.random() * 50),
      confidence_score: Math.random() * 0.3 + 0.7,  // 0.7 to 1.0
      image_url: `/mock-images/vehicles/${vehicleType}_${i % 5 + 1}.jpg`,
      notes: i % 5 === 0 ? 'Regular delivery vehicle' : ''
    });
  }
  
  return vehicles;
};

// Generate vehicle entries (logs)
const generateVehicleEntries = (vehicleId, count) => {
  const entries = [];
  
  for (let i = 0; i < count; i++) {
    const entryTime = randomDate(new Date('2025-04-01'), new Date());
    const exitTime = Math.random() > 0.1 ? 
      new Date(new Date(entryTime).getTime() + Math.random() * 3600000).toISOString() : null;
    
    entries.push({
      id: `entry-${vehicleId}-${i + 1}`,
      vehicle_id: vehicleId,
      license_plate: `ABC ${1000 + Math.floor(Math.random() * 9000)}`,
      entry_time: entryTime,
      exit_time: exitTime,
      location: Math.random() > 0.5 ? 'Main Gate' : 'Delivery Entrance',
      confidence_score: Math.random() * 0.3 + 0.7,
      image_url: `/mock-images/entries/entry_${i % 5 + 1}.jpg`,
      status: exitTime ? 'completed' : 'active'
    });
  }
  
  return entries;
};

// Generate analytics data
const generateVehicleAnalytics = () => {
  const today = new Date();
  const thirtyDaysAgo = new Date(today);
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  
  // Daily traffic
  const dailyTraffic = [];
  for (let i = 0; i < 30; i++) {
    const day = new Date(thirtyDaysAgo);
    day.setDate(day.getDate() + i);
    
    dailyTraffic.push({
      date: day.toISOString().split('T')[0],
      count: Math.floor(10 + Math.random() * 40),
      unauthorized: Math.floor(Math.random() * 5)
    });
  }
  
  // Vehicle type distribution
  const vehicleTypeDistribution = VEHICLE_TYPES.map(type => ({
    type,
    count: Math.floor(50 + Math.random() * 200)
  }));
  
  // Peak hours data
  const peakHours = [];
  for (let hour = 0; hour < 24; hour++) {
    peakHours.push({
      hour,
      count: hour >= 8 && hour <= 18 ? 
        Math.floor(5 + Math.random() * 15) : 
        Math.floor(Math.random() * 5)
    });
  }
  
  return {
    daily_traffic: dailyTraffic,
    vehicle_type_distribution: vehicleTypeDistribution,
    peak_hours: peakHours,
    total_vehicles: 285,
    authorized_vehicles: 218,
    unauthorized_vehicles: 32,
    pending_review: 35,
    average_confidence: 0.89
  };
};

// Create mock data for API responses
export const vehicleMockData = {
  vehicles: {
    data: generateVehicles(30),
    total: 30,
    page: 1,
    limit: 10
  },
  
  unauthorized: generateVehicles(8).map(vehicle => ({
    ...vehicle,
    status: 'unauthorized',
    detection_time: randomDate(new Date('2025-05-01'), new Date()),
    security_alert: Math.random() > 0.7
  })),
  
  entries: {
    data: generateVehicleEntries('v-1', 10),
    total: 10,
    page: 1,
    limit: 10
  },
  
  detection: {
    license_plate: generateLicensePlate(),
    confidence_score: 0.91,
    vehicle_type: VEHICLE_TYPES[Math.floor(Math.random() * VEHICLE_TYPES.length)],
    timestamp: new Date().toISOString(),
    image_url: '/mock-images/vehicles/detected.jpg',
    status: STATUS_OPTIONS[Math.floor(Math.random() * STATUS_OPTIONS.length)],
    matches: [
      { 
        id: 'v-5', 
        license_plate: 'XYZ 1234',
        similarity_score: 0.93,
        status: 'authorized'
      },
      { 
        id: 'v-12', 
        license_plate: 'ABC 4321',
        similarity_score: 0.86,
        status: 'unauthorized'
      }
    ]
  },
  
  analytics: generateVehicleAnalytics()
};

export default vehicleMockData;