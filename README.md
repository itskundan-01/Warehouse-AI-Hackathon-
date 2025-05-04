# WarehouseVision AI

AI-powered surveillance system for warehouse management with computer vision capabilities.

## Features

- **Gunny Bag Counting**: Automated counting of gunny bags in storage areas
- **Vehicle Recognition**: License plate detection and vehicle tracking
- **Facial Recognition**: Employee and visitor identification
- **Contextual Intelligence**: Advanced scene understanding and anomaly detection

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
- OpenCV dependencies

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/warehousevision-ai.git
   cd warehousevision-ai
   ```

2. Create a virtual environment
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
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
# Run the main application
python -m src.main

# Run specific modules
python -m src.modules.gunny_counter.main
python -m src.modules.vehicle_recognition.main
python -m src.modules.facial_recognition.main
python -m src.modules.context_intelligence.main
```

## Security Notes

- Never commit `.env` files or any files containing sensitive information
- All API keys, passwords, and tokens should be stored in the `.env` file
- Pre-trained models should be downloaded during setup rather than committed to the repo
- Use environment variables for all sensitive configuration

## Development Guidelines

### Setting Up Development Environment

1. Install development dependencies
   ```
   pip install -r requirements-dev.txt
   ```

2. Set up pre-commit hooks
   ```
   pre-commit install
   ```

### Running Tests

```bash
pytest
```

### Creating Model Folders
The repository comes with placeholder directories for models. To use models:

```bash
# Create directories for models if they don't exist
mkdir -p models/facial models/vehicle models/gunny models/contextual
```

## License

[Insert your license here]

## Contact

For any questions, please reach out to the team.
