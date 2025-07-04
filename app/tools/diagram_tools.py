"""
This file handles the actual creation of diagrams.

I'm using the 'diagrams' Python library, which is really cool! It lets you create
architecture diagrams just by writing Python code. The library automatically:
- Draws the boxes and arrows
- Uses nice AWS-style icons
- Handles the layout for you

This is much easier than trying to draw diagrams by hand!
"""

import os
import uuid
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import the diagrams library - this is the magic that makes it all work
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
    This class is responsible for creating the actual diagram images.
    
    When someone wants a diagram, this class:
    1. Takes their description and converts it to Python code
    2. Runs that code to create the diagram
    3. Saves it as an image file (PNG, SVG, etc.)
    
    It's like having a robot artist that draws diagrams for you!
    """
    
    def __init__(self, temp_dir: str = "./temp"):
        """
        Set up our diagram generator.
        
        Args:
            temp_dir: Where to save the diagram files
        """
        # Create a folder to store our diagrams
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
        # This dictionary maps common terms to the right diagram components
        # For example, when someone says "database", we know to use the RDS icon
        self.node_types = {
            # AWS Cloud Services (the most common ones)
            "ec2": EC2,           # Virtual servers in the cloud
            "rds": RDS,           # Managed databases
            "alb": ALB,           # Load balancer (distributes traffic)
            "vpc": VPC,           # Virtual private cloud (network isolation)
            "s3": S3,             # Object storage (like a file cabinet in the cloud)
            "sqs": SQS,           # Message queue (for communication between services)
            "cloudwatch": Cloudwatch,  # Monitoring and logging
            "iam": IAM,           # Identity and access management (who can do what)
            "apigateway": APIGateway,  # API management (front door to your services)
            
            # On-premise infrastructure (stuff you own)
            "server": Server,     # Physical or virtual servers
            "postgresql": PostgreSQL,  # Database
            "internet": Internet, # Internet connection
            
            # Programming frameworks
            "react": React,       # Frontend framework (what users see)
            "fastapi": FastAPI,   # Backend framework (what runs on the server)
            "python": Python,     # Programming language
        }
    
    def create_diagram(
        self, 
        description: str, 
        output_format: str = "png",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a diagram from a text description.
        
        This is the main function that does all the work:
        1. Takes what the user wants (like "web app with database")
        2. Converts it to Python code
        3. Runs the code to create the diagram
        4. Saves it as an image file
        
        Args:
            description: What they want (e.g., "Create a web app with a database")
            output_format: What type of image (png, svg, jpg)
            filename: What to call the file (optional)
            
        Returns:
            A dictionary telling us if it worked and where the file is
        """
        # If they didn't give us a filename, make one up
        if not filename:
            filename = f"diagram_{uuid.uuid4().hex[:8]}"
        
        # Figure out the full path where we'll save the file
        output_path = self.temp_dir / f"{filename}.{output_format}"
        
        try:
            # Step 1: Convert their description into Python code
            diagram_code = self._generate_diagram_code(description)
            
            # Step 2: Run the code to create the actual diagram
            self._execute_diagram_code(diagram_code, str(output_path))
            
            # Step 3: Tell them it worked!
            return {
                "success": True,
                "file_path": str(output_path),
                "diagram_code": diagram_code,
                "format": output_format
            }
            
        except Exception as e:
            # If something went wrong, tell them what happened
            return {
                "success": False,
                "error": str(e),
                "diagram_code": None
            }
    
    def _generate_diagram_code(self, description: str) -> str:
        """
        Convert a text description into Python code that creates a diagram.
        
        This is where the magic happens! We look at what they want and
        generate the right Python code to create that diagram.
        
        For now, I'm using simple templates based on keywords.
        In a real app, you might use AI to generate this code dynamically.
        
        Args:
            description: What they want (e.g., "web app with database")
            
        Returns:
            Python code that will create the diagram
        """
        # Make it lowercase so we can easily search for keywords
        description_lower = description.lower()
        
        # Choose the right template based on what they want
        if "web application" in description_lower and "load balancer" in description_lower:
            return self._web_app_template()
        elif "microservices" in description_lower:
            return self._microservices_template()
        else:
            return self._generic_template(description)
    
    def _web_app_template(self) -> str:
        """
        Template for a typical web application with load balancer.
        
        This creates a diagram showing:
        - A load balancer that distributes traffic
        - Multiple web servers (for reliability)
        - A database for storing data
        
        Returns:
            Python code for a web application diagram
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
        Template for a microservices architecture.
        
        This creates a diagram showing:
        - Multiple small services that work together
        - API Gateway as the front door
        - Message queues for communication
        - Monitoring and logging
        
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
from diagrams.aws.security import IAM

with Diagram("Microservices Architecture", show=False):
    gateway = APIGateway("API Gateway")
    
    with Cluster("Services"):
        service1 = EC2("User Service")
        service2 = EC2("Order Service")
        service3 = EC2("Payment Service")
    
    with Cluster("Data Layer"):
        db1 = RDS("User Database")
        db2 = RDS("Order Database")
        db3 = RDS("Payment Database")
    
    queue = SQS("Message Queue")
    monitoring = Cloudwatch("Monitoring")
    
    gateway >> service1
    gateway >> service2
    gateway >> service3
    
    service1 >> db1
    service2 >> db2
    service3 >> db3
    
    service1 >> queue
    service2 >> queue
    service3 >> queue
    
    service1 >> monitoring
    service2 >> monitoring
    service3 >> monitoring
'''
    
    def _generic_template(self, description: str) -> str:
        """
        A simple template for when we don't know exactly what they want.
        
        This creates a basic diagram with a few common components.
        It's like a fallback option when the other templates don't match.
        
        Args:
            description: What they want (we'll use this for the title)
            
        Returns:
            Python code for a simple diagram
        """
        return f'''
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB

with Diagram("{description[:50]}", show=False):
    alb = ALB("Load Balancer")
    web = EC2("Web Server")
    db = RDS("Database")
    
    alb >> web
    web >> db
'''
    
    def _execute_diagram_code(self, code: str, output_path: str) -> None:
        """
        Actually run the Python code to create the diagram.
        
        This is the scary part! We take the Python code we generated
        and actually run it to create the diagram file.
        
        Args:
            code: The Python code to run
            output_path: Where to save the diagram
            
        Raises:
            Exception: If something goes wrong
        """
        try:
            # Create a temporary file to hold our code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Set the output path as an environment variable
            # The diagrams library will use this to know where to save the file
            os.environ['DIAGRAM_OUTPUT_PATH'] = output_path
            
            # Run the code! This is where the diagram actually gets created
            exec(compile(code, '<string>', 'exec'))
            
            # Clean up our temporary file
            os.unlink(temp_file_path)
            
        except Exception as e:
            # If something went wrong, clean up and raise the error
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise e
    
    def cleanup_temp_files(self) -> None:
        """
        Remove old diagram files to save disk space.
        
        Over time, we create a lot of diagram files. This function
        removes old ones so our server doesn't run out of space.
        """
        try:
            # Remove all diagram files in our temp directory
            for file_path in self.temp_dir.glob("diagram_*"):
                file_path.unlink()
        except Exception as e:
            # If something goes wrong, just log it and continue
            print(f"Error cleaning up temp files: {e}")
    
    def create_diagram_from_description(
        self,
        components: list[str],
        connections: list[str],
        output_format: str = "png",
        filename: str | None = None
    ) -> dict:
        """
        Create a diagram from a list of components and connections.
        
        This is a more advanced function that lets you specify exactly
        what components you want and how they connect.
        
        Args:
            components: List of component names (e.g., ["Web Server", "Database"])
            connections: List of connections (e.g., ["Web Server -> Database"])
            output_format: What type of image to create
            filename: What to call the file
            
        Returns:
            Dictionary with success status and file path
        """
        try:
            # Generate a filename if none provided
            if not filename:
                filename = f"diagram_{uuid.uuid4().hex[:8]}"
            
            # Create the output path
            output_path = self.temp_dir / f"{filename}.{output_format}"
            
            # Build the Python code from the components and connections
            code_lines = [
                "from diagrams import Diagram, Cluster",
                "from diagrams.aws.compute import EC2",
                "from diagrams.aws.database import RDS",
                "from diagrams.aws.network import ALB",
                "",
                "with Diagram(\"Custom Architecture\", show=False):"
            ]
            
            # Add components
            component_vars = {}
            for i, component in enumerate(components):
                var_name = f"component_{i}"
                component_vars[component] = var_name
                
                # Try to pick the right icon based on the component name
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
            
            # Combine all the code
            diagram_code = "\n".join(code_lines)
            
            # Create the diagram
            self._execute_diagram_code(diagram_code, str(output_path))
            
            return {
                "success": True,
                "file_path": str(output_path),
                "diagram_code": diagram_code,
                "format": output_format
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "diagram_code": None
            }


def parse_llm_diagram_response(response: str):
    """
    Parse the response from the LLM to extract components and connections.
    
    This function takes the AI's response and tries to figure out:
    - What components they want in the diagram
    - How those components should be connected
    
    Args:
        response: The AI's response (should be structured)
        
    Returns:
        Tuple of (components list, connections list)
    """
    components = []
    connections = []
    
    # Split the response into lines and look for patterns
    lines = response.split('\n')
    in_components = False
    in_connections = False
    
    for line in lines:
        line = line.strip()
        
        # Look for section headers
        if "components:" in line.lower():
            in_components = True
            in_connections = False
            continue
        elif "connections:" in line.lower():
            in_components = False
            in_connections = True
            continue
        
        # Extract components
        if in_components and line and not line.startswith('-'):
            if ':' in line:
                component = line.split(':')[1].strip()
            else:
                component = line.strip()
            if component:
                components.append(component)
        
        # Extract connections
        elif in_connections and line and not line.startswith('-'):
            if '->' in line or 'connects' in line.lower():
                connections.append(line.strip())
    
    # If we didn't find anything, use some defaults
    if not components:
        components = ["Web Server", "Database"]
    if not connections:
        connections = ["Web Server -> Database"]
    
    return components, connections 