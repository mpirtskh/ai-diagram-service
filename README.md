# AI Diagram Service

This project is a Python web service that turns natural language descriptions into architecture diagrams. You describe what you want (like a web app with a load balancer and database), and the service generates a diagram image for you.

## Features

- Converts text descriptions into diagrams (PNG, SVG, JPG)
- Powered by FastAPI and Google Gemini (LLM)
- Supports several AWS and on-premise node types
- Simple web interface included
- Can run locally or in Docker

## Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/mpirtskh/ai-diagram-service.git
   cd ai-diagram-service
   ```

2. **Install dependencies**
   ```bash
   pip install uv
   uv pip install --system .
   ```

3. **Set up environment**
   - Copy `env.example` to `.env` and add your Google API key.

4. **Run the app**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

5. **Open the web UI**
   - Open `web/index.html` in your browser.

## API Overview

- `POST /generate-diagram` — Send a description, get a diagram image.
- `POST /assistant` — Chat with the assistant for help.
- `GET /health` — Health check.

## Requirements

- Python 3.9+
- [Graphviz](https://graphviz.gitlab.io/) installed and in your PATH
- Google API key (for production)

## Testing

Run all tests with:
```bash
uv run pytest
```

## License

MIT 