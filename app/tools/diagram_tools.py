"""
Diagram generation tools for LLM agents.

This module provides tools to create diagrams using the Python 'diagrams' package.
It acts as a bridge between the LLM agent and the diagrams library.
"""

import os
import uuid
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import the diagrams library and its components
import diagrams
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB, VPC
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM
from diagrams.aws.network import APIGateway
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.network import Internet
from diagrams.programming.framework import React, FastAPI
from diagrams.programming.language import Python


class DiagramGenerator:
    """
    Tool for generating diagrams using the diagrams package.
    
    This class provides methods to:
    - Create diagrams from natural language descriptions
    - Execute generated diagram code
    - Manage temporary files
    - Support multiple output formats
    """
    
    def __init__(self, temp_dir: str = "./temp"):
        """
        Initialize the diagram generator.
        
        Args:
            temp_dir: Directory to store temporary diagram files
        """
        # Create the temporary directory if it doesn't exist
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Define available node types for diagrams
        # This maps node names to their corresponding diagram classes
        self.node_types = {
            # AWS Cloud Services
            "ec2": EC2,           # Virtual servers
            "rds": RDS,           # Managed databases
            "alb": ALB,           # Load balancer
            "vpc": VPC,           # Virtual private cloud
            "s3": S3,             # Object storage
            "sqs": SQS,           # Message queue
            "cloudwatch": Cloudwatch,  # Monitoring
            "iam": IAM,           # Identity and access management
            "apigateway": APIGateway,  # API management
            
            # On-premise infrastructure
            "server": Server,     # Physical/virtual servers
            "postgresql": PostgreSQL,  # Database
            "internet": Internet, # Internet connection
            
            # Programming frameworks
            "react": React,       # Frontend framework
            "fastapi": FastAPI,   # Backend framework
            "python": Python,     # Programming language
        }
    
    def create_diagram(
        self, 
        description: str, 
        output_format: str = "png",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a diagram based on natural language description.
        
        This method:
        1. Generates Python code for the diagram
        2. Executes the code to create the image
        3. Returns the result with file path and metadata
        
        Args:
            description: Natural language description of the diagram
            output_format: Output format (png, svg, jpg)
            filename: Optional filename for the output
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating if generation was successful
            - file_path: Path to the generated image (if successful)
            - diagram_code: Generated Python code
            - error: Error message (if unsuccessful)
        """
        # Generate a unique filename if none provided
        if not filename:
            filename = f"diagram_{uuid.uuid4().hex[:8]}"
        
        # Create the full output path
        output_path = self.temp_dir / f"{filename}.{output_format}"
        
        try:
            # Step 1: Generate Python code for the diagram
            diagram_code = self._generate_diagram_code(description)
            
            # Step 2: Execute the code to create the actual diagram
            self._execute_diagram_code(diagram_code, str(output_path))
            
            # Return success response
            return {
                "success": True,
                "file_path": str(output_path),
                "diagram_code": diagram_code,
                "format": output_format
            }
            
        except Exception as e:
            # Return error response
            return {
                "success": False,
                "error": str(e),
                "diagram_code": None
            }
    
    def _generate_diagram_code(self, description: str) -> str:
        """
        Generate Python code for the diagram based on description.
        
        This is a simplified template-based approach. In a real application,
        the LLM would generate this code dynamically.
        
        Args:
            description: Natural language description
            
        Returns:
            Python code string that creates the diagram
        """
        # Convert to lowercase for easier matching
        description_lower = description.lower()
        
        # Use different templates based on keywords in the description
        if "web application" in description_lower and "load balancer" in description_lower:
            return self._web_app_template()
        elif "microservices" in description_lower:
            return self._microservices_template()
        else:
            return self._generic_template(description)
    
    def _web_app_template(self) -> str:
        """
        Template for web application with load balancer architecture.
        
        Returns:
            Python code for a typical web application diagram
        """
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
    
    def _microservices_template(self) -> str:
        """
        Template for microservices architecture.
        
        Returns:
            Python code for a microservices diagram
        """
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
    
    def _generic_template(self, description: str) -> str:
        """
        Generic template for other types of diagrams.
        
        Args:
            description: Original description for context
            
        Returns:
            Python code for a basic diagram
        """
        return f'''
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
    
    def _execute_diagram_code(self, code: str, output_path: str) -> None:
        """
        Execute the generated diagram code to create the image.
        
        This method:
        1. Creates a temporary Python file
        2. Executes the code
        3. Moves the generated image to the desired location
        4. Cleans up temporary files
        
        Args:
            code: Python code to execute
            output_path: Where to save the generated image
        """
        # Create a temporary Python file to execute the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute the diagram code
            # This will create a PNG file in the current directory
            exec(compile(code, '<string>', 'exec'))
            
            # The diagrams package automatically saves to the current directory
            # We need to move it to our desired location
            current_files = list(Path('.').glob('*.png'))
            if current_files:
                # Move the generated file to our output path
                current_files[0].rename(output_path)
                
        finally:
            # Clean up the temporary Python file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def cleanup_temp_files(self) -> None:
        """
        Clean up temporary diagram files.
        
        This method removes all files in the temp directory.
        Useful for maintenance and freeing up disk space.
        """
        for file_path in self.temp_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink() 