"""
LLM service for interacting with Google Gemini API.

This module handles all interactions with the Large Language Model (LLM).
It provides methods to generate diagram code and assistant responses.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

# Import Google's Generative AI library
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# Import our configuration
from app.config import settings

# Set up logging for this module
logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for LLM interactions.
    
    This class provides methods to:
    - Generate diagram code from natural language descriptions
    - Get assistant responses for conversational interactions
    - Handle both real API calls and mock responses for development
    """
    
    def __init__(self):
        """
        Initialize the LLM service.
        
        Sets up the LLM client if API key is available,
        or enables mock mode for development.
        """
        self.llm = None
        self.mock_mode = settings.mock_llm
        
        # If we have an API key and mock mode is disabled, set up the real LLM
        if not self.mock_mode and settings.google_api_key:
            # Create the LLM client
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",  # Use Gemini 1.5 Pro model
                temperature=0.7,     # Controls randomness (0.0 = deterministic, 1.0 = very random)
                max_tokens=2048,  # Maximum length of response
                convert_system_message_to_human=True,  # Required for Gemini
                google_api_key=settings.google_api_key
            )
        elif self.mock_mode:
            # Log that we're running in mock mode
            logger.info("Running in mock mode - LLM calls will be simulated")
    
    async def generate_diagram_code(self, description: str) -> str:
        """
        Generate diagram code from natural language description.
        
        This method takes a natural language description and uses the LLM
        to generate Python code that creates the described diagram.
        
        Args:
            description: Natural language description of the diagram
            
        Returns:
            Generated Python code for the diagram
            
        Raises:
            ValueError: If LLM is not configured and mock mode is disabled
        """
        # If in mock mode, use pre-built templates
        if self.mock_mode:
            return self._mock_diagram_code(description)
        
        # Check if LLM is properly configured
        if not self.llm:
            raise ValueError(
                "LLM not configured. Please set GOOGLE_API_KEY or enable MOCK_LLM."
            )
        
        # Define the system prompt that instructs the LLM how to generate diagram code
        system_prompt = """
You are a helpful assistant for creating architecture diagrams.

When a user describes a system, respond with a structured list of components, clusters, and how they are connected. Do not write any code. Just describe the diagram in terms of:

- Components (e.g., EC2 instance, RDS database, Load Balancer)
- Clusters or groups (e.g., "Web Tier" cluster)
- Connections (e.g., "Load Balancer connects to Web Tier", "Web Tier connects to Database")

Example:

User: "Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named 'Web Tier'."

Your response:
Components:
- Application Load Balancer
- Web Tier (cluster)
  - Web Server 1 (EC2)
  - Web Server 2 (EC2)
- Database (RDS)

Connections:
- Application Load Balancer connects to Web Server 1 and Web Server 2
- Web Server 1 and Web Server 2 connect to Database

If you need more information, ask clarifying questions.
"""
        
        # Create the messages for the LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User: {description}")
        ]
        
        try:
            # Call the LLM asynchronously
            response = await asyncio.to_thread(self.llm.invoke, messages)
            return response.content
        except Exception as e:
            # Log the error and re-raise it
            logger.error(f"Error generating diagram code: {e}")
            raise
    
    async def assistant_response(self, message: str, context: Optional[str] = None) -> str:
        """
        Generate assistant response for conversational interface.
        
        This method provides a conversational AI assistant that can:
        - Answer questions about diagram creation
        - Provide guidance on architecture design
        - Help troubleshoot issues
        
        Args:
            message: User's message to the assistant
            context: Optional conversation context for continuity
            
        Returns:
            Assistant's response message
            
        Raises:
            ValueError: If LLM is not configured and mock mode is disabled
        """
        # If in mock mode, use pre-built responses
        if self.mock_mode:
            return self._mock_assistant_response(message)
        
        # Check if LLM is properly configured
        if not self.llm:
            raise ValueError(
                "LLM not configured. Please set GOOGLE_API_KEY or enable MOCK_LLM."
            )
        
        # Define the system prompt for the assistant
        system_prompt = """You are a helpful assistant that helps users create diagrams. 
        You can:
        1. Explain how to create diagrams
        2. Ask clarifying questions about their requirements
        3. Provide examples of diagram types
        4. Help troubleshoot diagram issues
        
        Be conversational and helpful. If the user wants to create a diagram, 
        ask for more details about what they want to visualize."""
        
        # Combine context and message if context is provided
        full_message = message
        if context:
            full_message = f"Context: {context}\n\nUser: {message}"
        
        # Create the messages for the LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_message)
        ]
        
        try:
            # Call the LLM asynchronously
            response = await asyncio.to_thread(self.llm.invoke, messages)
            return response.content
        except Exception as e:
            # Log the error and re-raise it
            logger.error(f"Error generating assistant response: {e}")
            raise
    
    def _mock_diagram_code(self, description: str) -> str:
        """
        Generate mock diagram code for testing and development.
        
        This method provides pre-built templates for common diagram types
        when running in mock mode (without API keys).
        
        Args:
            description: Natural language description
            
        Returns:
            Pre-built Python code for the diagram
        """
        # Convert to lowercase for easier matching
        description_lower = description.lower()
        
        # Return different templates based on keywords
        if "web" in description_lower and "load balancer" in description_lower:
            return '''
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB

with Diagram("Web Application Architecture", show=False):
    with Cluster("Web Tier"):
        alb = ALB("Application Load Balancer")
        web1 = EC2("Web Server 1")
        web2 = EC2("Web Server 2")
        
        alb >> web1
        alb >> web2
    
    db = RDS("Database")
    
    web1 >> db
    web2 >> db
'''
        elif "microservices" in description_lower:
            return '''
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import APIGateway
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch

with Diagram("Microservices Architecture", show=False):
    api_gateway = APIGateway("API Gateway")
    
    with Cluster("Microservices"):
        auth_service = EC2("Auth Service")
        payment_service = EC2("Payment Service")
        order_service = EC2("Order Service")
        
        api_gateway >> auth_service
        api_gateway >> payment_service
        api_gateway >> order_service
    
    sqs = SQS("Message Queue")
    db = RDS("Shared Database")
    monitoring = Cloudwatch("Monitoring")
    
    auth_service >> sqs
    payment_service >> sqs
    order_service >> sqs
    
    auth_service >> db
    payment_service >> db
    order_service >> db
    
    monitoring >> auth_service
    monitoring >> payment_service
    monitoring >> order_service
'''
        else:
            # Generic template for other requests
            return '''
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC

with Diagram("Custom Architecture", show=False):
    with Cluster("Main Cluster"):
        service1 = EC2("Service 1")
        service2 = EC2("Service 2")
    
    database = RDS("Database")
    
    service1 >> database
    service2 >> database
'''
    
    def _mock_assistant_response(self, message: str) -> str:
        """
        Generate mock assistant responses for testing and development.
        
        This method provides pre-built responses for common user messages
        when running in mock mode.
        
        Args:
            message: User's message
            
        Returns:
            Pre-built assistant response
        """
        # Convert to lowercase for easier matching
        message_lower = message.lower()
        
        # Return different responses based on keywords
        if "diagram" in message_lower:
            return ("I'd be happy to help you create a diagram! Could you tell me more about "
                   "what you'd like to visualize? For example, are you looking to create a "
                   "system architecture, network diagram, or something else?")
        elif "help" in message_lower:
            return ("I can help you create various types of diagrams including system "
                   "architectures, network diagrams, microservices layouts, and more. "
                   "Just describe what you want to visualize and I'll help you create it!")
        else:
            return ("Hello! I'm here to help you create diagrams. "
                   "What would you like to visualize today?")

    async def get_diagram_description(self, description: str) -> str:
        # ... (use the new system_prompt above)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User: {description}")
        ]
        try:
            response = await asyncio.to_thread(self.llm.invoke, messages)
            return response.content  # This will be a structured description, not code!
        except Exception as e:
            logger.error(f"Error getting diagram description: {e}")
            raise 