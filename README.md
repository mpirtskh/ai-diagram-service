# AI Diagram Generation Service

An async, stateless Python API service that allows users to create diagrams using AI agents powered by Large Language Models (LLM). The service enables users to describe diagram components, nodes, or flow in natural language and get back rendered images.

## 🚀 Features

- **Natural Language to Diagram**: Convert text descriptions into visual diagrams
- **AI Assistant Interface**: Conversational interface for diagram creation help
- **Multiple Output Formats**: Support for PNG, SVG, and JPG formats
- **Stateless Architecture**: No database or session management required
- **Docker Support**: Easy containerization and deployment
- **Mock Mode**: Local development without API keys
- **Comprehensive Testing**: Unit tests for all components

## 🏗️ Architecture

The service is built with a modular architecture:

- **FastAPI**: Async web framework for the API
- **LangChain**: LLM integration and agent framework
- **Google Gemini**: LLM provider (with mock mode for development)
- **Diagrams Package**: Python library for creating cloud architecture diagrams
- **UV**: Modern Python package management

## 📋 Requirements

- Python 3.9+
- Docker (optional)
- Google API Key (for production use)

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SD_Solutions_Project
   ```

2. **Install UV package manager** (if not already installed)
   ```bash
   pip install uv
   ```

3. **Install dependencies**
   ```bash
   uv pip install --system .
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the service**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build manually**
   ```bash
   docker build -t ai-diagram-service .
   docker run -p 8000:8000 ai-diagram-service
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# LLM Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Service Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# File Storage
TEMP_DIR=./temp
MAX_FILE_SIZE=10485760  # 10MB

# Logging
LOG_LEVEL=INFO

# Development
MOCK_LLM=false  # Set to true for local development without API key
```

### Mock Mode

For development without an API key, set `MOCK_LLM=true` in your `.env` file. This enables:
- Simulated LLM responses
- Pre-built diagram templates
- No external API dependencies

## 📚 API Endpoints

### 1. Generate Diagram
**POST** `/generate-diagram`

Generate a diagram from natural language description.

**Request Body:**
```json
{
  "description": "Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named 'Web Tier'.",
  "format": "png"
}
```

**Response:**
```json
{
  "success": true,
  "image_url": "/images/diagram_abc123.png",
  "diagram_code": "from diagrams import Diagram, Cluster..."
}
```

### 2. Assistant Chat
**POST** `/assistant`

Conversational interface for diagram creation help.

**Request Body:**
```json
{
  "message": "Help me create a microservices architecture diagram",
  "conversation_id": "optional-conversation-id"
}
```

**Response:**
```json
{
  "message": "I'd be happy to help you create a microservices diagram!",
  "conversation_id": "conversation-uuid",
  "has_diagram": true,
  "diagram_url": "/images/diagram_xyz789.png",
  "diagram_code": "from diagrams import Diagram, Cluster..."
}
```

### 3. Health Check
**GET** `/health`

Check service health and status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 4. Get Image
**GET** `/images/{filename}`

Serve generated diagram images.

### 5. Delete Conversation
**DELETE** `/conversations/{conversation_id}`

Clean up conversation context.

### 6. Cleanup
**POST** `/cleanup`

Trigger cleanup of temporary files.

## 🎯 Example Usage

### Example 1: Web Application Architecture

**Input:**
```
"Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named 'Web Tier'."
```

**Output:**
- Generated PNG image showing:
  - Application Load Balancer
  - Two EC2 instances in "Web Tier" cluster
  - RDS database
  - Proper connections between components

### Example 2: Microservices Architecture

**Input:**
```
"Design a microservices architecture with three services: an authentication service, a payment service, and an order service. Include an API Gateway for routing, an SQS queue for message passing between services, and a shared RDS database. Group the services in a cluster called 'Microservices'. Add CloudWatch for monitoring."
```

**Output:**
- Generated PNG image showing:
  - API Gateway
  - Three microservices in "Microservices" cluster
  - SQS message queue
  - Shared RDS database
  - CloudWatch monitoring
  - All connections and relationships

## 🧪 Testing

### Run Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_services.py
```

### Test Coverage
The test suite covers:
- LLM service functionality
- Diagram generation tools
- Agent service orchestration
- API endpoints
- Error handling

## 🐳 Docker Deployment

### Production Deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Configuration
```bash
# Run with custom environment
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e LOG_LEVEL=DEBUG \
  ai-diagram-service
```

## 🌐 Web Interface

A simple web interface is available at `http://localhost:8080` when using Docker Compose. Features include:

- Interactive diagram generation
- Assistant chat interface
- Health monitoring
- Real-time results display

## 🔍 Supported Node Types

The service supports various node types through the diagrams package:

### AWS Services
- EC2 (Compute)
- RDS (Database)
- ALB (Load Balancer)
- VPC (Network)
- S3 (Storage)
- SQS (Message Queue)
- CloudWatch (Monitoring)
- IAM (Security)
- API Gateway (API Management)

### On-Premise Services
- Server (Compute)
- PostgreSQL (Database)
- Internet (Network)

### Programming Frameworks
- React (Frontend)
- FastAPI (Backend)
- Python (Language)

## 🚨 Limitations & Considerations

### Current Limitations
- Limited to cloud architecture diagrams
- Requires Graphviz for diagram rendering
- Temporary files stored on disk
- No persistent storage for conversations

### Performance Considerations
- LLM API rate limits
- Diagram generation time varies by complexity
- Memory usage scales with concurrent requests
- Temporary file cleanup required

### Security Considerations
- API keys should be kept secure
- Input validation on all endpoints
- CORS configured for web interface
- No authentication implemented

## 🔧 Development

### Project Structure
```
SD_Solutions_Project/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   └── agent_service.py
│   └── tools/             # Diagram generation tools
│       ├── __init__.py
│       └── diagram_tools.py
├── tests/                 # Unit tests
├── web/                   # Web interface
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── env.example
└── README.md
```

### Adding New Node Types
1. Import the new node type in `app/tools/diagram_tools.py`
2. Add to the `node_types` dictionary
3. Update the LLM prompt in `app/services/llm_service.py`
4. Add tests for the new functionality

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Include logs and error messages

## 🎉 Acknowledgments

- [Diagrams](https://diagrams.mingrammer.com/) - Python library for cloud architecture diagrams
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://langchain.com/) - LLM application framework
- [Google Gemini](https://ai.google.dev/) - Large Language Model API 