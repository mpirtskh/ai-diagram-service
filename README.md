# AI Diagram Generator

Hey there! 👋 I built this project to help people create architecture diagrams just by describing them in plain English. It's like having a smart assistant that can draw diagrams for you!

## What does it do?

This app lets you:
- **Describe a system** in natural language (like "Create a web app with a load balancer and database")
- **Get a diagram** automatically generated with proper AWS-style icons
- **Chat with an AI assistant** to get help with diagram design
- **Download diagrams** in different formats (PNG, SVG, JPG)

## How it works

The app has two main parts:
1. **Backend API** (Python/FastAPI) - handles the AI logic and diagram generation
2. **Frontend** (HTML/JavaScript) - provides a simple web interface

When you describe what you want, the app:
1. Sends your description to an AI (Google Gemini)
2. The AI breaks it down into components and connections
3. We convert that into Python code using the `diagrams` library
4. The code generates an actual image file
5. You get back both the image and the code that created it

## Getting Started

### Prerequisites

You'll need:
- Python 3.8+ 
- Graphviz (for diagram generation)
- A Google API key (optional - there's a mock mode for testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd SD_Solutions_Project
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Graphviz** (required for diagram generation)
   ```bash
   # On macOS:
   brew install graphviz
   
   # On Ubuntu/Debian:
   sudo apt-get install graphviz
   
   # On Windows:
   # Download from https://graphviz.org/download/
   ```

5. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your Google API key (optional)
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   source venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the frontend server** (in a new terminal)
   ```bash
   cd web
   python -m http.server 3000
   ```

3. **Open your browser**
   Go to `http://localhost:3000`

## How to Use

### Generating Diagrams

1. **Enter a description** in the text area, like:
   - "Create a web application with a load balancer and two web servers"
   - "Design a microservices architecture with three services"
   - "Show a simple database with a web server"

2. **Choose a format** (PNG, SVG, or JPG)

3. **Click "Generate Diagram"**

4. **View your diagram** and the code that created it!

### Using the AI Assistant

1. **Ask questions** about diagram creation
2. **Get help** with architecture design
3. **Request diagrams** through conversation

## Project Structure

```
SD_Solutions_Project/
├── app/                    # Backend code
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration settings
│   ├── models.py          # Data models
│   ├── services/          # Business logic
│   │   ├── agent_service.py    # Main coordination
│   │   └── llm_service.py      # AI interactions
│   └── tools/             # Diagram generation
│       └── diagram_tools.py    # Creates actual diagrams
├── web/                   # Frontend
│   └── index.html         # Web interface
├── temp/                  # Generated diagrams (created automatically)
└── requirements.txt       # Python dependencies
```

## Configuration

The app uses environment variables for configuration. Copy `env.example` to `.env` and adjust:

```env
# Required: Your Google API key for AI features
GOOGLE_API_KEY=your_api_key_here

# Optional: Set to true for testing without API key
MOCK_LLM=false

# Optional: Where to store generated diagrams
TEMP_DIR=./temp

# Optional: Logging level
LOG_LEVEL=INFO
```

## Development Notes

### Mock Mode

If you don't have a Google API key, you can run in mock mode:
```env
MOCK_LLM=true
```

This will use pre-built templates instead of calling the AI, which is great for testing!

### Adding New Diagram Types

To add support for new diagram types:

1. **Add templates** in `app/tools/diagram_tools.py`
2. **Update the parser** in `app/services/agent_service.py`
3. **Test with different descriptions**

### Troubleshooting

**"Network Error" when generating diagrams:**
- Make sure both servers are running (backend on port 8000, frontend on port 3000)
- Check that Graphviz is installed
- Try a hard refresh in your browser (Ctrl+Shift+R)

**"Failed to execute PosixPath('dot')":**
- Install Graphviz: `brew install graphviz` (macOS) or `sudo apt-get install graphviz` (Ubuntu)

**API errors:**
- Check your Google API key is valid
- Try mock mode for testing: set `MOCK_LLM=true` in `.env`

## Technologies Used

- **Backend**: FastAPI, Python
- **AI**: Google Gemini (via LangChain)
- **Diagrams**: Python `diagrams` library
- **Frontend**: HTML, CSS, JavaScript
- **Build**: Graphviz for image generation

## Contributing

This is a learning project, so feel free to:
- Add new diagram templates
- Improve the AI prompts
- Enhance the web interface
- Fix bugs or add features

## License

This project is for educational purposes. Feel free to use and modify as needed!

---

**Note**: This is my first time building something like this, so the code is intentionally simple and well-documented. I'm still learning, so there might be better ways to do things! 😊
