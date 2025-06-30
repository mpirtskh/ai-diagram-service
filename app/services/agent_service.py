"""
Agent service for orchestrating LLM and diagram generation.

This module coordinates between the LLM service and diagram generation tools.
It provides a high-level interface for generating diagrams and handling conversations.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

# Import our services and configuration
from app.services.llm_service import LLMService
from app.tools.diagram_tools import DiagramGenerator
from app.config import settings

# Set up logging for this module
logger = logging.getLogger(__name__)


class AgentService:
    """
    Service for orchestrating LLM agents and diagram generation.
    
    This class provides methods to:
    - Generate diagrams from natural language descriptions
    - Handle conversational interactions with the AI assistant
    - Manage conversation context and temporary files
    """
    
    def __init__(self):
        """
        Initialize the agent service.
        
        Creates instances of the LLM service and diagram generator,
        and initializes conversation storage.
        """
        # Create the LLM service for generating code and responses
        self.llm_service = LLMService()
        
        # Create the diagram generator for creating actual diagrams
        self.diagram_generator = DiagramGenerator(settings.temp_dir)
        
        # Store conversation contexts (conversation_id -> context)
        self.conversations: Dict[str, str] = {}
    
    async def generate_diagram(self, description: str, output_format: str = "png") -> Dict[str, Any]:
        """
        Generate a diagram from natural language description.
        
        This method orchestrates the entire diagram generation process:
        1. Uses the LLM to generate Python code from the description
        2. Uses the diagram generator to create the actual image
        3. Returns the result with file path and metadata
        
        Args:
            description: Natural language description of the diagram
            output_format: Output format (png, svg, jpg)
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating if generation was successful
            - image_url: URL to access the generated image (if successful)
            - diagram_code: Generated Python code
            - error: Error message (if unsuccessful)
        """
        try:
            # Step 1: Generate diagram code using the LLM
            diagram_code = await self.llm_service.generate_diagram_code(description)
            
            # Step 2: Create the actual diagram using the generated code
            result = self.diagram_generator.create_diagram(
                description=description,
                output_format=output_format
            )
            
            # Step 3: Process the result
            if result["success"]:
                # Create a URL for the generated image
                image_url = f"/images/{Path(result['file_path']).name}"
                
                return {
                    "success": True,
                    "image_url": image_url,
                    "diagram_code": result["diagram_code"],
                    "file_path": result["file_path"]
                }
            else:
                # Return error with the generated code for debugging
                return {
                    "success": False,
                    "error": result["error"],
                    "diagram_code": diagram_code
                }
                
        except Exception as e:
            # Log the error and return error response
            logger.error(f"Error generating diagram: {e}")
            return {
                "success": False,
                "error": str(e),
                "diagram_code": None
            }
    
    async def assistant_chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle assistant-style chat interactions.
        
        This method provides a conversational interface where users can:
        - Ask questions about diagram creation
        - Get help with architecture design
        - Create diagrams through natural conversation
        
        Args:
            message: User's message to the assistant
            conversation_id: Optional conversation ID for maintaining context
            
        Returns:
            Dictionary containing:
            - message: Assistant's response
            - conversation_id: Unique identifier for the conversation
            - has_diagram: Whether a diagram was generated
            - diagram_url: URL to the generated diagram (if any)
            - diagram_code: Generated Python code (if any)
        """
        try:
            # Generate or get conversation ID
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Get conversation context for continuity
            context = self.conversations.get(conversation_id, "")
            
            # Check if user wants to create a diagram
            message_lower = message.lower()
            diagram_keywords = ["create", "generate", "make", "build", "diagram", "architecture"]
            
            # If the message contains diagram-related keywords, try to generate a diagram
            if any(keyword in message_lower for keyword in diagram_keywords):
                # Try to generate a diagram
                diagram_result = await self.generate_diagram(message)
                
                if diagram_result["success"]:
                    # Update conversation context
                    self.conversations[conversation_id] = (
                        f"{context}\nUser: {message}\n"
                        f"Assistant: I've created a diagram for you!"
                    )
                    
                    return {
                        "message": f"I've created a diagram based on your request! "
                                  f"You can view it at {diagram_result['image_url']}",
                        "conversation_id": conversation_id,
                        "has_diagram": True,
                        "diagram_url": diagram_result["image_url"],
                        "diagram_code": diagram_result["diagram_code"]
                    }
                else:
                    # If diagram generation failed, fall back to assistant response
                    assistant_response = await self.llm_service.assistant_response(message, context)
                    self.conversations[conversation_id] = (
                        f"{context}\nUser: {message}\n"
                        f"Assistant: {assistant_response}"
                    )
                    
                    return {
                        "message": f"I tried to create a diagram but encountered an issue: "
                                  f"{diagram_result['error']}. Let me help you with some guidance instead.",
                        "conversation_id": conversation_id,
                        "has_diagram": False
                    }
            else:
                # Regular assistant response (no diagram generation)
                assistant_response = await self.llm_service.assistant_response(message, context)
                self.conversations[conversation_id] = (
                    f"{context}\nUser: {message}\n"
                    f"Assistant: {assistant_response}"
                )
                
                return {
                    "message": assistant_response,
                    "conversation_id": conversation_id,
                    "has_diagram": False
                }
                
        except Exception as e:
            # Log the error and return error response
            logger.error(f"Error in assistant chat: {e}")
            return {
                "message": "I'm sorry, I encountered an error. Please try again.",
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "has_diagram": False
            }
    
    def cleanup_conversation(self, conversation_id: str) -> None:
        """
        Clean up a conversation context.
        
        This method removes the stored context for a specific conversation,
        effectively "forgetting" the conversation history.
        
        Args:
            conversation_id: ID of the conversation to clean up
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def cleanup_temp_files(self) -> None:
        """
        Clean up temporary diagram files.
        
        This method removes all temporary diagram files from the temp directory.
        Useful for maintenance and freeing up disk space.
        """
        self.diagram_generator.cleanup_temp_files() 