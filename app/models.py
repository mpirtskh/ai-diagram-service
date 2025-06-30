"""
Pydantic models for API validation.

These models define the request/response schemas for our endpoints.
Pydantic handles validation automatically - pretty neat!
"""

from typing import Optional
from pydantic import BaseModel, Field


class DiagramRequest(BaseModel):
    """
    Request model for /generate-diagram endpoint.
    
    Validates the incoming request data before processing.
    """
    
    description: str = Field(
        ...,  # Required field
        description="What kind of diagram do you want?",
        min_length=10,  # Need some actual content
        max_length=2000  # Don't want novels here
    )
    
    format: str = Field(
        default="png",
        description="Output format - png, svg, or jpg",
        pattern="^(png|svg|jpg)$"  # Only these formats supported
    )


class AssistantRequest(BaseModel):
    """
    Request model for /assistant endpoint.
    
    Handles chat messages and conversation context.
    """
    
    message: str = Field(
        ...,  # Required
        description="Your message to the AI assistant",
        min_length=1,  # Can't be empty
        max_length=2000  # Reasonable limit
    )
    
    conversation_id: Optional[str] = Field(
        None,  # Optional - for new conversations
        description="Keep the conversation going"
    )


class DiagramResponse(BaseModel):
    """
    Response from diagram generation.
    
    Either success with image URL, or error with details.
    """
    
    success: bool
    image_url: Optional[str] = None  # URL to the generated image
    error: Optional[str] = None      # What went wrong
    diagram_code: Optional[str] = None  # The Python code that was generated


class AssistantResponse(BaseModel):
    """
    Response from assistant chat.
    
    Includes the AI's response and optional diagram info.
    """
    
    message: str
    conversation_id: str
    has_diagram: bool = False
    diagram_url: Optional[str] = None
    diagram_code: Optional[str] = None


class HealthResponse(BaseModel):
    """
    Simple health check response.
    
    Used by load balancers and monitoring.
    """
    
    status: str
    version: str
    timestamp: str 