# WarehouseVision AI

AI-powered surveillance system for warehouse management with computer vision capabilities.

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
