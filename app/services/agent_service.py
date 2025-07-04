"""
This service handles the main logic for creating diagrams.

Think of this as the "brain" of our app. It coordinates between:
- The LLM service (which understands what users want)
- The diagram tools (which actually create the diagrams)
- The file system (where we save the diagrams)

I'm still learning how to structure this kind of code, so I'm keeping it simple!
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Import our other services
from app.config import settings
from app.services.llm_service import LLMService
from app.tools.diagram_tools import DiagramGenerator

# Set up logging so we can see what's happening
logger = logging.getLogger(__name__)


class AgentService:
    """
    This is our main service that coordinates everything.
    
    When someone wants a diagram, this class:
    1. Takes their description and sends it to the AI
    2. Gets back a structured description of what they want
    3. Converts that into actual diagram code
    4. Generates the image file
    5. Returns everything to the user
    
    It's like a project manager that makes sure everyone does their job!
    """
    
    def __init__(self):
        """
        Set up our services when we start.
        
        We need:
        - LLM service: to understand what users want
        - Diagram tools: to actually create the diagrams
        - A place to store conversations (for the chat feature)
        """
        self.llm_service = LLMService()
        self.diagram_tools = DiagramGenerator(settings.temp_dir)
        
        # Store conversations in memory for now
        # In a real app, you'd use a database
        self.conversations = {}
        
        # Create the temp directory if it doesn't exist
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    async def generate_diagram(self, description: str, output_format: str = "png") -> Dict[str, Any]:
        """
        This is the main function that creates diagrams from text descriptions.
        
        Here's the step-by-step process:
        1. User gives us a description like "Create a web app with a database"
        2. We ask the AI to break this down into components and connections
        3. We convert that into Python code that creates the diagram
        4. We run the code to generate the actual image
        5. We save the image and return the URL
        
        Args:
            description: What the user wants (e.g., "Create a web app with a database")
            output_format: What type of image they want (png, svg, jpg)
            
        Returns:
            A dictionary with success status, image URL, and the code we generated
        """
        try:
            logger.info(f"Starting to create a diagram for: {description[:50]}...")
            
            # Step 1: Ask the AI to understand what they want
            # The AI gives us back a structured description instead of code
            structured_description = await self.llm_service.generate_diagram_code(description)
            logger.info("Got structured description from AI")
            
            # Step 2: Convert the structured description into actual diagram code
            diagram_code = self._build_diagram_from_description(structured_description)
            logger.info("Converted to diagram code")
            
            # Step 3: Generate a unique filename for this diagram
            filename = f"diagram_{uuid.uuid4().hex[:8]}.{output_format}"
            file_path = self.temp_dir / filename
            
            # Step 4: Create the actual image file
            result = self.diagram_tools.create_diagram(
                description=description,
                output_format=output_format,
                filename=filename.replace(f".{output_format}", "")
            )
            
            success = result["success"]
            
            if success:
                # Step 5: Return success with the image URL and code
                image_url = f"/images/{filename}"
                logger.info(f"Successfully created diagram: {filename}")
                
                return {
                    "success": True,
                    "image_url": image_url,
                    "diagram_code": diagram_code,
                    "error": None
                }
            else:
                # Something went wrong with creating the image
                logger.error("Failed to create diagram image")
                return {
                    "success": False,
                    "image_url": None,
                    "diagram_code": diagram_code,  # Still return the code so they can see what we tried
                    "error": "Failed to generate diagram image"
                }
                
        except Exception as e:
            # If anything goes wrong, log it and return an error
            logger.error(f"Error creating diagram: {e}")
            return {
                "success": False,
                "image_url": None,
                "diagram_code": None,
                "error": str(e)
            }
    
    async def assistant_chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        This handles the chat feature where users can talk to an AI assistant.
        
        The assistant can:
        - Answer questions about diagrams
        - Help users figure out what kind of diagram they need
        - Sometimes create diagrams directly from the conversation
        
        Args:
            message: What the user said
            conversation_id: To remember previous messages (optional)
            
        Returns:
            The assistant's response and maybe a diagram
        """
        try:
            # If this is a new conversation, create an ID for it
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.conversations[conversation_id] = []
            
            # Add the user's message to the conversation history
            self.conversations[conversation_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now()
            })
            
            # Get the assistant's response
            assistant_response = await self.llm_service.assistant_response(
                message=message,
                context=self._get_conversation_context(conversation_id)
            )
            
            # Add the assistant's response to history
            self.conversations[conversation_id].append({
                "role": "assistant", 
                "content": assistant_response,
                "timestamp": datetime.now()
            })
            
            # Check if the assistant wants to create a diagram
            # For now, we'll just check if they mention creating a diagram
            has_diagram = "diagram" in assistant_response.lower() and any(
                word in message.lower() for word in ["create", "make", "generate", "show"]
            )
            
            result = {
                "message": assistant_response,
                "conversation_id": conversation_id,
                "has_diagram": has_diagram,
                "diagram_url": None,
                "diagram_code": None
            }
            
            # If they want a diagram, try to create one
            if has_diagram:
                logger.info("Assistant wants to create a diagram, trying to generate one...")
                diagram_result = await self.generate_diagram(message)
                
                if diagram_result["success"]:
                    result["has_diagram"] = True
                    result["diagram_url"] = diagram_result["image_url"]
                    result["diagram_code"] = diagram_result["diagram_code"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error in assistant chat: {e}")
            return {
                "message": "Sorry, I'm having trouble right now. Please try again!",
                "conversation_id": conversation_id,
                "has_diagram": False,
                "diagram_url": None,
                "diagram_code": None
            }
    
    def _build_diagram_from_description(self, structured_description: str) -> str:
        """
        This converts the AI's structured description into actual Python code.
        
        The AI gives us something like:
        "Components: Load Balancer, Web Server, Database
         Connections: Load Balancer -> Web Server, Web Server -> Database"
        
        We convert this into Python code that the diagrams library can understand.
        
        Args:
            structured_description: The AI's structured description
            
        Returns:
            Python code that creates the diagram
        """
        try:
            # Parse the structured description to extract components and connections
            components, connections = self._parse_structured_description(structured_description)
            
            # Build the Python code
            code_lines = [
                "from diagrams import Diagram, Cluster",
                "from diagrams.aws.compute import EC2",
                "from diagrams.aws.database import RDS", 
                "from diagrams.aws.network import ALB",
                "",
                "with Diagram(\"Generated Architecture\", show=False):"
            ]
            
            # Add components
            component_vars = {}
            for i, component in enumerate(components):
                var_name = f"component_{i}"
                component_vars[component] = var_name
                
                # Try to map to appropriate AWS icons
                if "load balancer" in component.lower() or "alb" in component.lower():
                    code_lines.append(f"    {var_name} = ALB(\"{component}\")")
                elif "database" in component.lower() or "db" in component.lower():
                    code_lines.append(f"    {var_name} = RDS(\"{component}\")")
                else:
                    code_lines.append(f"    {var_name} = EC2(\"{component}\")")
            
            # Add connections
            for connection in connections:
                if " -> " in connection:
                    from_comp, to_comp = connection.split(" -> ")
                    from_var = component_vars.get(from_comp.strip(), "component_0")
                    to_var = component_vars.get(to_comp.strip(), "component_1")
                    code_lines.append(f"    {from_var} >> {to_var}")
            
            return "\n".join(code_lines)
            
        except Exception as e:
            logger.error(f"Error building diagram code: {e}")
            # Return a simple fallback diagram
            return """
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Simple Architecture", show=False):
    web = EC2("Web Server")
    db = RDS("Database")
    web >> db
"""
    
    def _parse_structured_description(self, description: str) -> tuple:
        """
        Parse the AI's structured description into components and connections.
        
        This is a simple parser that looks for patterns in the text.
        In a real app, you might use more sophisticated parsing.
        
        Args:
            description: The structured description from the AI
            
        Returns:
            Tuple of (components list, connections list)
        """
        components = []
        connections = []
        
        lines = description.split('\n')
        in_components = False
        in_connections = False
        
        for line in lines:
            line = line.strip()
            
            if "components:" in line.lower():
                in_components = True
                in_connections = False
                continue
            elif "connections:" in line.lower():
                in_components = False
                in_connections = True
                continue
            
            if in_components and line and not line.startswith('-'):
                # Extract component name
                if ':' in line:
                    component = line.split(':')[1].strip()
                else:
                    component = line.strip()
                if component:
                    components.append(component)
            
            elif in_connections and line and not line.startswith('-'):
                # Extract connection
                if '->' in line or 'connects' in line.lower():
                    connections.append(line.strip())
        
        # If we didn't find anything, make up some defaults
        if not components:
            components = ["Web Server", "Database"]
        if not connections:
            connections = ["Web Server -> Database"]
        
        return components, connections
    
    def _get_conversation_context(self, conversation_id: str) -> str:
        """
        Get the conversation history as context for the AI.
        
        This helps the AI remember what the user has been talking about.
        
        Args:
            conversation_id: The conversation to get context for
            
        Returns:
            A string with the conversation history
        """
        if conversation_id not in self.conversations:
            return ""
        
        # Get the last few messages for context
        recent_messages = self.conversations[conversation_id][-6:]  # Last 6 messages
        
        context_lines = []
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def cleanup_temp_files(self):
        """
        Remove old diagram files to save disk space.
        
        This is important because we generate a lot of files over time.
        We only keep files from the last 24 hours.
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            deleted_count = 0
            
            for file_path in self.temp_dir.glob("diagram_*"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old diagram files")
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def cleanup_conversation(self, conversation_id: str):
        """
        Remove a conversation from memory.
        
        This is called when users want to delete their chat history.
        
        Args:
            conversation_id: The conversation to delete
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")

def parse_llm_diagram_response(response: str):
    components = []
    connections = []
    in_components = False
    in_connections = False
    for line in response.splitlines():
        line = line.strip()
        if line.lower().startswith("components:"):
            in_components = True
            in_connections = False
            continue
        if line.lower().startswith("connections:"):
            in_components = False
            in_connections = True
            continue
        if in_components and line.startswith("-"):
            components.append(line[1:].strip())
        if in_connections and line.startswith("-"):
            connections.append(line[1:].strip())
    return components, connections 