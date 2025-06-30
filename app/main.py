"""
Main FastAPI application for the AI Diagram Service.

This module contains the main FastAPI application with all endpoints,
middleware configuration, and application lifecycle management.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import FastAPI and related components
import aiofiles
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import our application components
from app.config import settings
from app.models import (
    DiagramRequest, 
    DiagramResponse, 
    AssistantRequest, 
    AssistantResponse,
    HealthResponse
)
from app.services.agent_service import AgentService

# ===== Logging Configuration =====
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===== FastAPI Application Setup =====
app = FastAPI(
    title="AI Diagram Generation Service",
    description="An async, stateless Python API service that allows users to create diagrams using AI agents",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# ===== CORS Middleware =====
# Allow cross-origin requests (needed for web interface)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Directory Setup =====
# Create temp directory for storing generated diagrams
temp_dir = Path(settings.temp_dir)
temp_dir.mkdir(exist_ok=True)

# ===== Static Files =====
# Mount the temp directory to serve generated images
app.mount("/images", StaticFiles(directory=str(temp_dir)), name="images")

# ===== Global Services =====
# Create a global agent service instance
agent_service = AgentService()


# ===== Application Lifecycle Events =====

@app.on_event("startup")
async def startup_event():
    """
    Initialize the application on startup.
    
    This function runs when the FastAPI application starts up.
    It logs important information about the service configuration.
    """
    logger.info("Starting AI Diagram Generation Service")
    logger.info(f"Temp directory: {temp_dir}")
    logger.info(f"Mock LLM mode: {settings.mock_llm}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown.
    
    This function runs when the FastAPI application shuts down.
    It cleans up temporary files to free up disk space.
    """
    logger.info("Shutting down AI Diagram Generation Service")
    agent_service.cleanup_temp_files()


# ===== API Endpoints =====

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    This endpoint is used to check if the service is running properly.
    It's commonly used by load balancers and monitoring systems.
    
    Returns:
        HealthResponse: Service status, version, and timestamp
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    """
    Generate a diagram from natural language description.
    
    This is the main endpoint for diagram generation. It takes a natural language
    description and returns a generated diagram image along with the Python code
    that was used to create it.
    
    Args:
        request: DiagramRequest containing description and format
        
    Returns:
        DiagramResponse: Success status, image URL, and generated code
        
    Raises:
        HTTPException: If there's an error during diagram generation
    """
    try:
        logger.info(f"Generating diagram for: {request.description[:100]}...")
        
        # Use the agent service to generate the diagram
        result = await agent_service.generate_diagram(
            description=request.description,
            output_format=request.format
        )
        
        # Return appropriate response based on success/failure
        if result["success"]:
            return DiagramResponse(
                success=True,
                image_url=result["image_url"],
                diagram_code=result["diagram_code"]
            )
        else:
            return DiagramResponse(
                success=False,
                error=result["error"],
                diagram_code=result["diagram_code"]
            )
            
    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assistant", response_model=AssistantResponse)
async def assistant_chat(request: AssistantRequest):
    """
    Assistant-style endpoint for conversational diagram creation.
    
    This endpoint provides a conversational interface where users can:
    - Ask questions about diagram creation
    - Get help with diagram design
    - Create diagrams through natural conversation
    
    Args:
        request: AssistantRequest containing message and optional conversation_id
        
    Returns:
        AssistantResponse: Assistant's response and optional diagram information
        
    Raises:
        HTTPException: If there's an error during assistant interaction
    """
    try:
        logger.info(f"Assistant chat: {request.message[:100]}...")
        
        # Use the agent service to handle the assistant interaction
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
        logger.error(f"Error in assistant chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve generated diagram images.
    
    This endpoint serves the generated diagram files from the temp directory.
    It's used by the web interface to display generated diagrams.
    
    Args:
        filename: Name of the image file to serve
        
    Returns:
        FileResponse: The image file
        
    Raises:
        HTTPException: If the image file is not found
    """
    file_path = temp_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="image/png",
        filename=filename
    )


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation context.
    
    This endpoint allows users to clean up conversation history.
    Useful for privacy and memory management.
    
    Args:
        conversation_id: ID of the conversation to delete
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If there's an error deleting the conversation
    """
    try:
        agent_service.cleanup_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cleanup")
async def cleanup_temp_files(background_tasks: BackgroundTasks):
    """
    Clean up temporary files.
    
    This endpoint triggers cleanup of temporary diagram files.
    It runs the cleanup in the background to avoid blocking the response.
    
    Args:
        background_tasks: FastAPI's background task manager
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If there's an error scheduling the cleanup
    """
    try:
        background_tasks.add_task(agent_service.cleanup_temp_files)
        return {"message": "Cleanup scheduled successfully"}
    except Exception as e:
        logger.error(f"Error scheduling cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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