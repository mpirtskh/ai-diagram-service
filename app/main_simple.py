"""
Simple AI Diagram Generator - Main Server File
==============================================

This file creates a web server that can:
1. Generate diagrams from text descriptions
2. Chat with an AI assistant
3. Serve the web interface

Think of this as the "reception desk" - it handles all incoming requests!
"""

# Import the tools we need
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os

# Import our own code
from app.config import settings
from app.models import DiagramRequest, DiagramResponse, AssistantRequest, AssistantResponse
from app.services.agent_service import AgentService

# Set up logging (this helps us see what's happening)
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create our web application
app = FastAPI(
    title="AI Diagram Generator",
    description="Turn text descriptions into beautiful architecture diagrams!",
    version="1.0.0"
)

# Allow the web page to talk to our server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create our main service (this does the actual work)
agent_service = AgentService()

# Make sure our temp folder exists
os.makedirs(settings.temp_dir, exist_ok=True)

# Serve static files (like the web interface)
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.on_event("startup")
async def startup_event():
    """This runs when the server starts up"""
    logger.info("🚀 Starting up our AI Diagram Generator!")
    logger.info(f"📁 Diagrams will be saved in: {settings.temp_dir}")
    logger.info(f"🤖 Using mock AI mode: {settings.mock_llm}")

@app.on_event("shutdown")
async def shutdown_event():
    """This runs when the server shuts down"""
    logger.info("🛑 Shutting down our AI Diagram Generator")
    agent_service.cleanup_temp_files()

# ============================================================================
# API ENDPOINTS (These are like "doors" that people can use)
# ============================================================================

@app.get("/")
async def root():
    """Serve the main web page"""
    return FileResponse("web/index.html")

@app.get("/health")
async def health_check():
    """Check if the server is working"""
    return {"status": "healthy", "message": "AI Diagram Generator is running!"}

@app.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    """
    Generate a diagram from a text description
    
    This is the main function! When someone wants a diagram:
    1. They send us a description
    2. We create the diagram
    3. We send back the image and code
    """
    try:
        logger.info(f"🎨 Someone wants a diagram for: {request.description[:50]}...")
        
        # Use our agent service to create the diagram
        result = await agent_service.generate_diagram(request.description)
        
        return DiagramResponse(
            success=True,
            image_url=f"/diagrams/{result['filename']}",
            diagram_code=result['code'],
            error=None
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create diagram: {str(e)}")

@app.post("/assistant", response_model=AssistantResponse)
async def assistant_chat(request: AssistantRequest):
    """
    Chat with the AI assistant
    
    This lets users have a conversation with the AI and potentially
    generate diagrams during the chat.
    """
    try:
        logger.info(f"💬 Assistant chat: {request.message[:50]}...")
        
        # Use our agent service to handle the chat
        response = await agent_service.assistant_chat(request.message, request.conversation_id)
        
        return AssistantResponse(
            message=response['message'],
            conversation_id=response['conversation_id'],
            has_diagram=response.get('has_diagram', False),
            diagram_url=response.get('diagram_url'),
            diagram_code=response.get('diagram_code')
        )
        
    except Exception as e:
        logger.error(f"❌ Error in assistant chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/diagrams/{filename}")
async def get_diagram(filename: str):
    """Serve a generated diagram image"""
    file_path = os.path.join(settings.temp_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    return FileResponse(file_path)

# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors (page not found)"""
    return {"error": "Page not found", "message": "The requested resource doesn't exist"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors (server errors)"""
    return {"error": "Internal server error", "message": "Something went wrong on our end"}

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    This runs when you start the file directly (not through uvicorn)
    """
    import uvicorn
    
    print("🚀 Starting AI Diagram Generator...")
    print("📖 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload when files change
    ) 