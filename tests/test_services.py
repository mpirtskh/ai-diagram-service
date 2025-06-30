"""Unit tests for the services."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from app.services.llm_service import LLMService
from app.services.agent_service import AgentService
from app.tools.diagram_tools import DiagramGenerator


class TestLLMService:
    """Test cases for LLMService."""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLMService instance for testing."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.mock_llm = True
            mock_settings.google_api_key = None
            return LLMService()
    
    @pytest.mark.asyncio
    async def test_generate_diagram_code_mock_mode(self, llm_service):
        """Test diagram code generation in mock mode."""
        description = "Create a web application with load balancer"
        result = await llm_service.generate_diagram_code(description)
        
        assert result is not None
        assert "from diagrams import Diagram" in result
        assert "ALB" in result
    
    @pytest.mark.asyncio
    async def test_assistant_response_mock_mode(self, llm_service):
        """Test assistant response in mock mode."""
        message = "Help me create a diagram"
        result = await llm_service.assistant_response(message)
        
        assert result is not None
        assert "diagram" in result.lower()


class TestDiagramGenerator:
    """Test cases for DiagramGenerator."""
    
    @pytest.fixture
    def diagram_generator(self, tmp_path):
        """Create DiagramGenerator instance for testing."""
        return DiagramGenerator(str(tmp_path))
    
    def test_init(self, diagram_generator):
        """Test DiagramGenerator initialization."""
        assert diagram_generator.temp_dir.exists()
        assert len(diagram_generator.node_types) > 0
    
    def test_create_diagram_web_app(self, diagram_generator):
        """Test creating web application diagram."""
        description = "Create a web application with load balancer and database"
        result = diagram_generator.create_diagram(description)
        
        assert result["success"] is True
        assert result["diagram_code"] is not None
        assert "ALB" in result["diagram_code"]
    
    def test_create_diagram_microservices(self, diagram_generator):
        """Test creating microservices diagram."""
        description = "Create a microservices architecture"
        result = diagram_generator.create_diagram(description)
        
        assert result["success"] is True
        assert result["diagram_code"] is not None
        assert "APIGateway" in result["diagram_code"]
    
    def test_cleanup_temp_files(self, diagram_generator, tmp_path):
        """Test cleanup of temporary files."""
        # Create a test file
        test_file = tmp_path / "test.png"
        test_file.write_text("test")
        
        diagram_generator.cleanup_temp_files()
        
        # Check that files are cleaned up
        assert not test_file.exists()


class TestAgentService:
    """Test cases for AgentService."""
    
    @pytest.fixture
    def agent_service(self, tmp_path):
        """Create AgentService instance for testing."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.temp_dir = str(tmp_path)
            mock_settings.mock_llm = True
            return AgentService()
    
    @pytest.mark.asyncio
    async def test_generate_diagram(self, agent_service):
        """Test diagram generation through agent service."""
        description = "Create a web application with load balancer"
        result = await agent_service.generate_diagram(description)
        
        assert result["success"] is True
        assert result["image_url"] is not None
        assert result["diagram_code"] is not None
    
    @pytest.mark.asyncio
    async def test_assistant_chat_with_diagram(self, agent_service):
        """Test assistant chat that generates a diagram."""
        message = "Create a diagram for a web application"
        result = await agent_service.assistant_chat(message)
        
        assert result["message"] is not None
        assert result["conversation_id"] is not None
        assert result["has_diagram"] is True
        assert result["diagram_url"] is not None
    
    @pytest.mark.asyncio
    async def test_assistant_chat_without_diagram(self, agent_service):
        """Test assistant chat without diagram generation."""
        message = "Hello, how are you?"
        result = await agent_service.assistant_chat(message)
        
        assert result["message"] is not None
        assert result["conversation_id"] is not None
        assert result["has_diagram"] is False
    
    def test_cleanup_conversation(self, agent_service):
        """Test conversation cleanup."""
        # Add a conversation
        conversation_id = "test-conversation"
        agent_service.conversations[conversation_id] = "test context"
        
        # Clean it up
        agent_service.cleanup_conversation(conversation_id)
        
        # Check it's gone
        assert conversation_id not in agent_service.conversations


@pytest.mark.asyncio
async def test_integration_flow():
    """Test the complete integration flow."""
    with patch('app.config.settings') as mock_settings:
        mock_settings.temp_dir = "./temp"
        mock_settings.mock_llm = True
        
        # Create services
        agent_service = AgentService()
        
        # Test complete flow
        description = "Create a microservices architecture with API gateway"
        result = await agent_service.generate_diagram(description)
        
        assert result["success"] is True
        assert result["image_url"] is not None
        assert result["diagram_code"] is not None
        
        # Clean up
        agent_service.cleanup_temp_files() 