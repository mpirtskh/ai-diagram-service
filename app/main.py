"""
This is the main file for our AI Diagram Generator app.

I'm building this to help people create diagrams just by describing them in plain English.
It uses FastAPI (a modern Python web framework) to create a web API that can:
- Take text descriptions and turn them into diagrams
- Chat with users to help them create better diagrams
- Serve the diagrams as images

This is my first time building something like this, so I'm keeping it simple and well-documented!
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# These are the libraries we need to make this work
import aiofiles
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# These are the files I created for this project
from app.config import settings
from app.models import (
    DiagramRequest, 
    DiagramResponse, 
    AssistantRequest, 
    AssistantResponse,
    HealthResponse
)
from app.services.agent_service import AgentService

# Set up logging so we can see what's happening when things go wrong
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create our FastAPI app - this is like the main container for our web service
app = FastAPI(
    title="AI Diagram Generation Service",
    description="A simple API that turns text descriptions into diagrams using AI",
    version="0.1.0",
    docs_url="/docs",  # This gives us automatic documentation
    redoc_url="/redoc"  # Another way to view the docs
)

# This is important! It allows our web page to talk to our API
# Without this, browsers would block the requests for security reasons
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In a real app, you'd be more specific about which websites can use this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a folder to store the diagrams we generate
temp_dir = Path(settings.temp_dir)
temp_dir.mkdir(exist_ok=True)

# This lets us serve the generated images directly from our API
app.mount("/images", StaticFiles(directory=str(temp_dir)), name="images")

# Create our main service that handles the AI stuff
agent_service = AgentService()


# These functions run when our app starts up and shuts down

@app.on_event("startup")
async def startup_event():
    """
    This runs when our app starts up.
    
    I'm just logging some basic info so we know everything is working.
    """
    logger.info("Starting up our AI Diagram Generator!")
    logger.info(f"Diagrams will be saved in: {temp_dir}")
    logger.info(f"Using mock AI mode: {settings.mock_llm}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    This runs when our app shuts down.
    
    We clean up any temporary files to save disk space.
    """
    logger.info("Shutting down our AI Diagram Generator")
    agent_service.cleanup_temp_files()


# Now let's create the actual endpoints that our web app will use

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    This endpoint just tells us if our service is working.
    
    It's useful for checking if everything is running properly.
    I use this to make sure the server is up before trying to generate diagrams.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    """
    This is the main endpoint - it takes a text description and creates a diagram.
    
    Here's how it works:
    1. User sends us a description like "Create a web app with a database"
    2. We use AI to understand what they want
    3. We generate the diagram code
    4. We create the actual image file
    5. We send back the image and the code
    
    Args:
        request: Contains the description and what format they want (PNG, SVG, etc.)
        
    Returns:
        Either a success response with the image, or an error message
    """
    try:
        logger.info(f"Someone wants a diagram for: {request.description[:100]}...")
        
        # Use our agent service to do the heavy lifting
        result = await agent_service.generate_diagram(
            description=request.description,
            output_format=request.format
        )
        
        # If it worked, send back the good news
        if result["success"]:
            return DiagramResponse(
                success=True,
                image_url=result["image_url"],
                diagram_code=result["diagram_code"]
            )
        else:
            # If something went wrong, send back the error
            return DiagramResponse(
                success=False,
                error=result["error"],
                diagram_code=result["diagram_code"]
            )
            
    except Exception as e:
        # If something really bad happened, log it and tell the user
        logger.error(f"Oops! Something went wrong: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assistant", response_model=AssistantResponse)
async def assistant_chat(request: AssistantRequest):
    """
    This endpoint lets users chat with an AI assistant about diagrams.
    
    It's like having a helpful friend who knows about diagrams and can:
    - Answer questions about how to create diagrams
    - Help you figure out what kind of diagram you need
    - Give you examples and tips
    
    Args:
        request: Contains the user's message and conversation history
        
    Returns:
        The assistant's response, and maybe a diagram if they created one
    """
    try:
        logger.info(f"Assistant chat: {request.message[:100]}...")
        
        # Let our agent service handle the conversation
        result = await agent_service.assistant_chat(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return AssistantResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
            has_diagram=result.get("has_diagram", False),
            diagram_url=result.get("diagram_url"),
            diagram_code=result.get("diagram_code")
        )
        
    except Exception as e:
        logger.error(f"Assistant chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    This endpoint serves the actual image files we generate.
    
    When someone wants to see a diagram, they need the image file.
    This function finds the file and sends it back to them.
    
    Args:
        filename: The name of the image file they want
        
    Returns:
        The image file, or an error if it doesn't exist
    """
    try:
        file_path = temp_dir / filename
        
        # Check if the file actually exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Send the file back to the user
        return FileResponse(
            path=str(file_path),
            media_type="image/png",  # We could make this smarter based on the file extension
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error serving image")


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    This endpoint lets users delete their chat history.
    
    Sometimes people want to start fresh with the assistant.
    This removes their conversation history so they can start over.
    
    Args:
        conversation_id: The ID of the conversation to delete
        
    Returns:
        A success message
    """
    try:
        # For now, we'll just return success
        # In a real app, we'd actually delete the conversation from storage
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Error deleting conversation")


@app.post("/cleanup")
async def cleanup_temp_files(background_tasks: BackgroundTasks):
    """
    This endpoint cleans up old diagram files.
    
    Over time, we generate a lot of diagram files that take up space.
    This function removes old files to keep our server tidy.
    
    Returns:
        A message about how many files were cleaned up
    """
    try:
        # Add the cleanup task to run in the background
        background_tasks.add_task(agent_service.cleanup_temp_files)
        return {"message": "Cleanup started in background"}
        
    except Exception as e:
        logger.error(f"Error starting cleanup: {e}")
        raise HTTPException(status_code=500, detail="Error starting cleanup")


# ===== Development Server =====
if __name__ == "__main__":
    import uvicorn
    
    # Run the development server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 