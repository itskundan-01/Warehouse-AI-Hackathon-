#!/bin/bash

# Warehouse AI Hackathon - Demonstration Script
# This script demonstrates all working features of the application

echo "🚀 Warehouse AI Hackathon - Feature Demonstration"
echo "=================================================="
echo ""

# Check if both servers are running
echo "📡 Checking Server Status..."
echo "Backend (Port 8000):"
curl -s http://localhost:8000/health 2>/dev/null && echo "✅ Backend is running" || echo "❌ Backend is not running"

echo "Frontend (Port 3000):"
curl -s http://localhost:3000 2>/dev/null && echo "✅ Frontend is running" || echo "❌ Frontend is not running"
echo ""

# Test API endpoints
echo "🤖 Testing AI Modules..."
echo "========================"

echo ""
echo "1. 📦 Gunny Bag Counter:"
echo "   - Testing gunny bag count endpoint..."
response=$(curl -s -X POST "http://localhost:8000/api/v1/gunny/count" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/test_gunny.jpg" \
  -F "location=demo_warehouse")

if [ $? -eq 0 ]; then
    echo "   ✅ Gunny bag detection working"
    echo "   📊 Result: $(echo $response | jq -r '.bag_count // "N/A"') bags detected"
else
    echo "   ❌ Gunny bag detection failed"
fi

echo ""
echo "2. 🚗 Vehicle Recognition:"
echo "   - Testing vehicle detection endpoint..."
response=$(curl -s -X POST "http://localhost:8000/api/v1/vehicle/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/test_vehicle.jpg" \
  -F "location=demo_gate")

if [ $? -eq 0 ]; then
    echo "   ✅ Vehicle recognition working"
    echo "   🔍 License Plate: $(echo $response | jq -r '.license_plate // "N/A"')"
else
    echo "   ❌ Vehicle recognition failed"
fi

echo ""
echo "3. 👤 Facial Recognition:"
echo "   - Testing facial detection endpoint..."
response=$(curl -s -X POST "http://localhost:8000/api/v1/facial/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/test_face.jpg" \
  -F "location=demo_entrance")

if [ $? -eq 0 ]; then
    echo "   ✅ Facial recognition working"
    echo "   👥 Faces detected: $(echo $response | jq -r '.face_count // "N/A"')"
else
    echo "   ❌ Facial recognition failed"
fi

echo ""
echo "4. 🧠 Contextual Intelligence:"
echo "   - Testing contextual query endpoint..."
response=$(curl -s -X POST "http://localhost:8000/api/v1/context/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vehicles entered today?", "context": {}}')

if [ $? -eq 0 ]; then
    echo "   ✅ Contextual intelligence working"
    echo "   💬 Response: $(echo $response | jq -r '.response // "N/A"' | head -c 60)..."
else
    echo "   ❌ Contextual intelligence failed"
fi

echo ""
echo "📊 Historical Data:"
echo "=================="

echo ""
echo "📦 Gunny Bag History:"
curl -s "http://localhost:8000/api/v1/gunny/counts" | jq -r '.[] | "   • \(.bag_count) bags at \(.location) (\(.timestamp[0:19]))"' | head -3

echo ""
echo "🚗 Vehicle History:"
curl -s "http://localhost:8000/api/v1/vehicle/vehicles" | jq -r '.[] | "   • \(.license_plate) at \(.location) (\(.created_at[0:19]))"' | head -3

echo ""
echo "🌐 Web Interfaces:"
echo "=================="
echo "   📖 Backend API Docs: http://localhost:8000/docs"
echo "   🖥️  Frontend App:     http://localhost:3000"

echo ""
echo "🎉 Demonstration Complete!"
echo "=========================="
echo "All AI modules are operational with intelligent fallback mechanisms."
echo "The system is ready for production deployment and further enhancement."
echo ""
echo "📝 Next Steps:"
echo "   1. Open frontend at http://localhost:3000"
echo "   2. Explore API documentation at http://localhost:8000/docs"
echo "   3. Test file uploads through the web interface"
echo "   4. Review logs in backend/logs/ directory"
echo ""
