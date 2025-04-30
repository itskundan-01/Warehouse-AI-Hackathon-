#!/bin/bash

# Create project structure for WarehouseVision AI
echo "Starting project structure creation for WarehouseVision AI..."

# Check if running from the correct directory
PROJECT_DIR="/Users/kundan/PROJECTS/Warehouse AI Hackathon"
CURRENT_DIR=$(pwd)

if [ "$CURRENT_DIR" != "$PROJECT_DIR" ]; then
    echo "Warning: You should run this script from $PROJECT_DIR"
    echo "Current directory: $CURRENT_DIR"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

# Root project directories
echo "Creating directory structure..."
mkdir -p .github/workflows
mkdir -p docs
mkdir -p src/config
mkdir -p src/core
mkdir -p src/modules/gunny_counter
mkdir -p src/modules/vehicle_recognition
mkdir -p src/modules/facial_recognition
mkdir -p src/modules/context_intelligence
mkdir -p src/api/endpoints
mkdir -p src/database
mkdir -p src/services
mkdir -p tests
mkdir -p models/yolo
mkdir -p models/ocr
mkdir -p models/facial
mkdir -p data/images
mkdir -p data/videos
mkdir -p scripts
mkdir -p notebooks
mkdir -p config/logstash
mkdir -p config/elasticsearch
mkdir -p config/kibana

# Create basic Python package structure
echo "Creating basic Python package files..."
touch .github/workflows/ci.yml
touch docs/architecture.md
touch docs/installation.md
touch docs/user_guide.md
touch docs/api_reference.md

touch src/__init__.py
touch src/main.py
touch src/config/__init__.py
touch src/config/settings.py
touch src/config/logging_config.py

touch src/core/__init__.py
touch src/core/models.py
touch src/core/security.py
touch src/core/utils.py

touch src/modules/__init__.py
touch src/modules/gunny_counter/__init__.py
touch src/modules/gunny_counter/detector.py
touch src/modules/gunny_counter/counter.py
touch src/modules/gunny_counter/volumetric.py

touch src/modules/vehicle_recognition/__init__.py
touch src/modules/vehicle_recognition/plate_detector.py
touch src/modules/vehicle_recognition/ocr.py
touch src/modules/vehicle_recognition/vehicle_tracker.py

touch src/modules/facial_recognition/__init__.py
touch src/modules/facial_recognition/face_detector.py
touch src/modules/facial_recognition/face_recognizer.py
touch src/modules/facial_recognition/auth_manager.py

touch src/modules/context_intelligence/__init__.py
touch src/modules/context_intelligence/event_detector.py
touch src/modules/context_intelligence/query_engine.py
touch src/modules/context_intelligence/video_indexer.py

touch src/api/__init__.py
touch src/api/routes.py
touch src/api/endpoints/__init__.py
touch src/api/endpoints/gunny.py
touch src/api/endpoints/vehicle.py
touch src/api/endpoints/facial.py
touch src/api/endpoints/contextual.py

touch src/database/__init__.py
touch src/database/models.py
touch src/database/operations.py

touch src/services/__init__.py
touch src/services/vahan_integration.py

# Create test files
echo "Creating test files..."
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_gunny_counter.py
touch tests/test_vehicle_recognition.py
touch tests/test_facial_recognition.py
touch tests/test_context_intelligence.py

# Create utility scripts
echo "Creating utility scripts..."
touch scripts/setup.sh
touch scripts/train.py
touch scripts/evaluate.py
touch scripts/init-db.sql

# Create notebook files
echo "Creating notebook files..."
touch notebooks/gunny_bag_analysis.ipynb
touch notebooks/vehicle_recognition.ipynb
touch notebooks/facial_recognition.ipynb
touch notebooks/context_intelligence.ipynb

# Create configuration files
echo "Creating configuration files..."
touch requirements.txt
touch Dockerfile.api
touch Dockerfile.worker
touch docker-compose.yml
touch .env.example
touch README.md
touch LICENSE

# Create ELK stack configuration files
echo "Creating ELK stack configuration files..."
touch config/logstash/logstash.conf
touch config/elasticsearch/elasticsearch.yml
touch config/kibana/kibana.yml

# Verify that directories were created
echo "Verifying directory structure..."
DIRS_TO_CHECK=("src" "models" "tests" "docs" "config" "notebooks")
for dir in "${DIRS_TO_CHECK[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir directory created successfully"
    else
        echo "❌ Failed to create $dir directory"
    fi
done

# Create a basic README.md with project structure visualization
echo "Creating README.md with project structure..."
cat > README.md << 'EOL'
# WarehouseVision AI

## Project Structure

```
warehousevision-ai/
├── .github/                        # GitHub workflows and templates
│   └── workflows/
│       └── ci.yml                  # CI configuration
├── docs/                           # Documentation
│   ├── architecture.md             # System architecture
│   ├── installation.md             # Setup instructions
│   ├── user_guide.md               # Usage guide
│   └── api_reference.md            # API documentation
├── src/                            # Source code
│   ├── config/                     # Configuration files
│   │   ├── __init__.py
│   │   ├── settings.py             # Application settings
│   │   └── logging_config.py       # Logging configuration
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py               # Data models
│   │   ├── security.py             # Authentication and security
│   │   └── utils.py                # Utility functions
│   ├── modules/                    # Feature modules
│   │   ├── __init__.py
│   │   ├── gunny_counter/          # Use Case 1: Gunny bag counting
│   │   ├── vehicle_recognition/    # Use Case 2: Vehicle recognition
│   │   ├── facial_recognition/     # Use Case 3: Facial recognition
│   │   └── context_intelligence/   # Use Case 4: Contextual intelligence
│   ├── api/                        # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py               # API routes
│   │   └── endpoints/              # API endpoint implementations
│   ├── database/                   # Database models and operations
│   │   ├── __init__.py
│   │   ├── models.py               # Database models
│   │   └── operations.py           # Database operations
│   ├── services/                   # External services integration
│   │   ├── __init__.py
│   │   └── vahan_integration.py    # VAHAN portal integration
│   ├── main.py                     # Application entry point
│   └── __init__.py
├── tests/                          # Test cases
├── models/                         # Pre-trained model files
├── data/                           # Sample data for testing
├── scripts/                        # Utility scripts
├── notebooks/                      # Jupyter notebooks for experiments
├── config/                         # Configuration files
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Docker Compose configuration
└── README.md                       # Project README
```

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- NVIDIA GPU with CUDA support (recommended)

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/warehousevision-ai.git
   cd warehousevision-ai
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Start the services
   ```
   docker-compose up -d
   ```

### Running the Application

```bash
python src/main.py
```

## Contact

For any questions, please reach out to the team.
EOL

echo "Project structure created successfully!"
echo "Next steps:"
echo "1. Execute 'chmod +x scripts/setup.sh' to make setup script executable"
echo "2. Run './scripts/setup.sh' to set up the development environment"
echo "3. Start implementing the modules according to the implementation tracker"
