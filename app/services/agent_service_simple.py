"""
Simple Agent Service - The Brain of Our App
===========================================

This service coordinates everything in our AI Diagram Generator.
Think of it as the "project manager" that makes sure everyone does their job!

What it does:
1. Takes user descriptions and sends them to AI
2. Gets back structured descriptions from AI
3. Converts those into Python code
4. Creates actual diagram images
5. Returns everything to the user

I'm keeping this simple so it's easy to understand!
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


class SimpleAgentService:
    """
    This is our main coordinator service.
    
    When someone wants a diagram, this class:
    1. Takes their description and sends it to the AI
    2. Gets back a structured description of what they want
    3. Converts that into actual diagram code
    4. Generates the image file
    5. Returns everything to the user
    
    It's like a smart assistant that understands what you want and makes it happen!
    """
    
    def __init__(self):
        """
        Set up our services when we start.
        
        We need:
        - LLM service: to understand what users want
        - Diagram tools: to actually create the diagrams
        - A place to store conversations (for the chat feature)
        """
        logger.info("🧠 Setting up our AI Agent Service...")
        
        # Create our AI service (this talks to Google Gemini)
        self.llm_service = LLMService()
        
        # Create our diagram tools (this creates the actual images)
        self.diagram_tools = DiagramGenerator(settings.temp_dir)
        
        # Store conversations in memory for now
        # In a real app, you'd use a database
        self.conversations = {}
        
        # Create the temp directory if it doesn't exist
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info("✅ Agent Service is ready!")
    
    async def generate_diagram(self, description: str, output_format: str = "png") -> Dict[str, Any]:
        """
        This is the main function that creates diagrams from text descriptions.
        
        Here's what happens step by step:
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
            logger.info(f"🎨 Starting to create a diagram for: {description[:50]}...")
            
            # Step 1: Ask the AI to understand what they want
            # The AI gives us back a structured description instead of code
            logger.info("🤖 Asking AI to understand the description...")
            structured_description = await self.llm_service.generate_diagram_code(description)
            logger.info("✅ Got structured description from AI")
            
            # Step 2: Convert the structured description into actual diagram code
            logger.info("🔧 Converting description to Python code...")
            diagram_code = self._build_diagram_from_description(structured_description)
            logger.info("✅ Converted to diagram code")
            
            # Step 3: Generate a unique filename for this diagram
            filename = f"diagram_{uuid.uuid4().hex[:8]}.{output_format}"
            file_path = self.temp_dir / filename
            
            # Step 4: Create the actual image file
            logger.info("🖼️ Creating the actual image...")
            result = self.diagram_tools.create_diagram(
                description=description,
                output_format=output_format,
                filename=filename.replace(f".{output_format}", "")
            )
            
            success = result["success"]
            
            if success:
                # Step 5: Return success with the image URL and code
                image_url = f"/diagrams/{filename}"
                logger.info(f"🎉 Successfully created diagram: {filename}")
                
                return {
                    "success": True,
                    "filename": filename,
                    "image_url": image_url,
                    "code": diagram_code,
                    "error": None
                }
            else:
                # Something went wrong with creating the image
                logger.error("❌ Failed to create diagram image")
                return {
                    "success": False,
                    "filename": None,
                    "image_url": None,
                    "code": diagram_code,  # Still return the code so they can see what we tried
                    "error": "Failed to generate diagram image"
                }
                
        except Exception as e:
            # If anything goes wrong, log it and return an error
            logger.error(f"❌ Error creating diagram: {e}")
            return {
                "success": False,
                "filename": None,
                "image_url": None,
                "code": None,
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
            logger.info(f"💬 Processing chat message: {message[:50]}...")
            
            # If this is a new conversation, create an ID for it
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.conversations[conversation_id] = []
                logger.info(f"🆕 Started new conversation: {conversation_id}")
            
            # Add the user's message to the conversation history
            self.conversations[conversation_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now()
            })
            
            # Get the assistant's response
            logger.info("🤖 Getting AI assistant response...")
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
                logger.info("🎨 Assistant wants to create a diagram, trying to generate one...")
                diagram_result = await self.generate_diagram(message)
                
                if diagram_result["success"]:
                    result["has_diagram"] = True
                    result["diagram_url"] = diagram_result["image_url"]
                    result["diagram_code"] = diagram_result["code"]
                    logger.info("✅ Successfully created diagram from chat!")
                else:
                    logger.warning("⚠️ Failed to create diagram from chat")
            
            logger.info("✅ Chat response ready")
            return result
            
        except Exception as e:
            # If anything goes wrong, log it and return an error
            logger.error(f"❌ Error in assistant chat: {e}")
            return {
                "message": f"Sorry, I encountered an error: {str(e)}",
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "has_diagram": False,
                "diagram_url": None,
                "diagram_code": None
            }
    
    def _build_diagram_from_description(self, structured_description: str) -> str:
        """
        Convert a structured description into Python code that creates a diagram.
        
        This is where the magic happens! We take what the AI understood and
        turn it into actual Python code that the diagrams library can use.
        
        Args:
            structured_description: What the AI understood (components and connections)
            
        Returns:
            Python code that creates the diagram
        """
        try:
            # Parse the structured description to get components and connections
            components, connections = self._parse_structured_description(structured_description)
            
            # Start building the Python code
            code_lines = [
                "# Generated diagram code",
                "# This code creates the diagram you requested",
                "",
                "from diagrams import Diagram, Cluster",
                "from diagrams.aws.compute import EC2",
                "from diagrams.aws.database import RDS",
                "from diagrams.aws.network import ELB",
                "from diagrams.aws.storage import S3",
                "from diagrams.onprem.compute import Server",
                "from diagrams.onprem.database import PostgreSQL",
                "from diagrams.onprem.network import Internet",
                "from diagrams.onprem.storage import Storage",
                "",
                "# Create the diagram",
                "with Diagram('Architecture Diagram', show=False):",
                "    # Define components"
            ]
            
            # Add components
            for i, component in enumerate(components):
                component_type = component.get('type', 'Server')
                component_name = component.get('name', f'Component_{i}')
                component_label = component.get('label', component_name)
                
                # Map component types to actual diagram classes
                if 'web' in component_type.lower() or 'server' in component_type.lower():
                    code_lines.append(f"    {component_name} = Server('{component_label}')")
                elif 'database' in component_type.lower() or 'db' in component_type.lower():
                    code_lines.append(f"    {component_name} = PostgreSQL('{component_label}')")
                elif 'load' in component_type.lower() or 'balancer' in component_type.lower():
                    code_lines.append(f"    {component_name} = ELB('{component_label}')")
                elif 'storage' in component_type.lower():
                    code_lines.append(f"    {component_name} = Storage('{component_label}')")
                else:
                    code_lines.append(f"    {component_name} = Server('{component_label}')")
            
            # Add connections
            if connections:
                code_lines.append("")
                code_lines.append("    # Define connections")
                for connection in connections:
                    from_component = connection.get('from', 'Component_0')
                    to_component = connection.get('to', 'Component_1')
                    code_lines.append(f"    {from_component} >> {to_component}")
            
            # Join all the lines into a single string
            return "\n".join(code_lines)
            
        except Exception as e:
            logger.error(f"Error building diagram code: {e}")
            # Return a simple fallback diagram
            return self._web_app_template()
    
    def _parse_structured_description(self, description: str) -> tuple:
        """
        Parse the AI's structured description into components and connections.
        
        The AI gives us text like:
        "Components: web_server (Web Server), database (Database)
         Connections: web_server -> database"
        
        We need to extract the components and connections from this.
        
        Args:
            description: The structured description from the AI
            
        Returns:
            Tuple of (components_list, connections_list)
        """
        components = []
        connections = []
        
        try:
            # Split the description into lines
            lines = description.strip().split('\n')
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check what section we're in
                if 'component' in line.lower():
                    current_section = 'components'
                    continue
                elif 'connection' in line.lower():
                    current_section = 'connections'
                    continue
                
                # Parse components
                if current_section == 'components':
                    # Look for patterns like "name (type)" or "name: type"
                    if '(' in line and ')' in line:
                        # Format: name (type)
                        name_part = line.split('(')[0].strip()
                        type_part = line.split('(')[1].split(')')[0].strip()
                        
                        components.append({
                            'name': name_part,
                            'type': type_part,
                            'label': name_part.replace('_', ' ').title()
                        })
                    elif ':' in line:
                        # Format: name: type
                        parts = line.split(':')
                        if len(parts) >= 2:
                            name_part = parts[0].strip()
                            type_part = parts[1].strip()
                            
                            components.append({
                                'name': name_part,
                                'type': type_part,
                                'label': name_part.replace('_', ' ').title()
                            })
                
                # Parse connections
                elif current_section == 'connections':
                    # Look for patterns like "from -> to" or "from to"
                    if '->' in line:
                        parts = line.split('->')
                        if len(parts) >= 2:
                            from_part = parts[0].strip()
                            to_part = parts[1].strip()
                            
                            connections.append({
                                'from': from_part,
                                'to': to_part
                            })
            
            # If we didn't find any components, create some defaults
            if not components:
                components = [
                    {'name': 'web_server', 'type': 'Web Server', 'label': 'Web Server'},
                    {'name': 'database', 'type': 'Database', 'label': 'Database'}
                ]
            
            # If we didn't find any connections, create a default one
            if not connections and len(components) >= 2:
                connections = [
                    {'from': components[0]['name'], 'to': components[1]['name']}
                ]
            
            logger.info(f"Parsed {len(components)} components and {len(connections)} connections")
            return components, connections
            
        except Exception as e:
            logger.error(f"Error parsing structured description: {e}")
            # Return default components and connections
            return [
                {'name': 'web_server', 'type': 'Web Server', 'label': 'Web Server'},
                {'name': 'database', 'type': 'Database', 'label': 'Database'}
            ], [
                {'from': 'web_server', 'to': 'database'}
            ]
    
    def _get_conversation_context(self, conversation_id: str) -> str:
        """
        Get the conversation history as context for the AI.
        
        This helps the AI remember what was said before.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            A string with the conversation history
        """
        if conversation_id not in self.conversations:
            return ""
        
        # Get the last few messages for context
        recent_messages = self.conversations[conversation_id][-5:]  # Last 5 messages
        
        context_lines = ["Previous conversation:"]
        for msg in recent_messages:
            role = msg['role']
            content = msg['content']
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def cleanup_temp_files(self):
        """
        Clean up old diagram files to save disk space.
        
        This removes diagram files that are older than 24 hours.
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            deleted_count = 0
            
            for file_path in self.temp_dir.glob("diagram_*"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"🧹 Cleaned up {deleted_count} old diagram files")
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def cleanup_conversation(self, conversation_id: str):
        """
        Remove a conversation from memory.
        
        This helps free up memory when conversations are no longer needed.
        
        Args:
            conversation_id: The ID of the conversation to remove
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"🗑️ Cleaned up conversation: {conversation_id}")
    
    def _web_app_template(self) -> str:
        """
        A simple template for web applications.
        
        This is used as a fallback when we can't parse the AI's response.
        
        Returns:
            Python code for a basic web app diagram
        """
        return '''# Simple Web Application Template
# This is a fallback diagram when we can't parse the AI response

from diagrams import Diagram
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL

# Create a simple web app diagram
with Diagram('Web Application', show=False):
    # Web server
    web_server = Server('Web Server')
    
    # Database
    database = PostgreSQL('Database')
    
    # Connection
    web_server >> database
''' 