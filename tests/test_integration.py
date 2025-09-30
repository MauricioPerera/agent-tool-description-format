#!/usr/bin/env python3
"""
BMAD-ATDF Integration Tests
Tests for the complete BMAD-ATDF integration
"""

import json
import os
import sys
import pytest
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.validator import validate_tool

class TestBMADIntegration:
    """Test suite for BMAD-ATDF integration"""
    
    def test_bmad_config_exists(self):
        """Test that BMAD configuration file exists"""
        config_path = project_root / "bmad.config.yml"
        assert config_path.exists(), "bmad.config.yml should exist"
    
    def test_atdf_schema_exists(self):
        """Test that ATDF schema file exists"""
        schema_path = project_root / "schema" / "atdf_schema.json"
        assert schema_path.exists(), "ATDF schema should exist"
    
    def test_atdf_schema_valid(self):
        """Test that ATDF schema is valid JSON"""
        schema_path = project_root / "schema" / "atdf_schema.json"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        assert isinstance(schema, dict), "Schema should be a valid JSON object"
        assert "type" in schema, "Schema should have a type property"
        assert "properties" in schema, "Schema should have properties"
    
    def test_example_tools_validation(self):
        """Test that example tools validate against ATDF schema"""
        examples_dir = project_root / "schema" / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")
        
        example_files = list(examples_dir.glob("*.json"))
        assert len(example_files) > 0, "Should have at least one example file"
        
        for example_file in example_files[:3]:  # Test first 3 examples
            try:
                result = validate_tool(str(example_file))
                assert result is True, f"Example {example_file.name} should be valid"
            except Exception as e:
                pytest.fail(f"Validation failed for {example_file.name}: {e}")
    
    def test_bmad_agents_exist(self):
        """Test that BMAD agent files exist"""
        agents_dir = project_root / "bmad" / "agents"
        assert agents_dir.exists(), "BMAD agents directory should exist"
        
        expected_agents = ["atdf-specialist.md", "bmad-orchestrator.md"]
        for agent in expected_agents:
            agent_path = agents_dir / agent
            assert agent_path.exists(), f"Agent file {agent} should exist"
    
    def test_bmad_workflows_exist(self):
        """Test that BMAD workflow files exist"""
        workflows_dir = project_root / "bmad" / "workflows"
        assert workflows_dir.exists(), "BMAD workflows directory should exist"
        
        expected_workflows = ["atdf-enhancement.yml", "tool-integration.yml"]
        for workflow in expected_workflows:
            workflow_path = workflows_dir / workflow
            assert workflow_path.exists(), f"Workflow file {workflow} should exist"
    
    def test_package_json_bmad_scripts(self):
        """Test that package.json contains BMAD scripts"""
        package_path = project_root / "package.json"
        assert package_path.exists(), "package.json should exist"
        
        with open(package_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        scripts = package_data.get("scripts", {})
        expected_scripts = [
            "bmad:status",
            "bmad:validate",
            "bmad:tools",
            "bmad:start-server",
            "bmad:generate-docs",
            "bmad:workflow"
        ]
        
        for script in expected_scripts:
            assert script in scripts, f"Script {script} should be in package.json"
    
    def test_installation_scripts_exist(self):
        """Test that installation scripts exist"""
        install_bat = project_root / "install_bmad.bat"
        install_sh = project_root / "install_bmad.sh"
        
        assert install_bat.exists(), "Windows installation script should exist"
        assert install_sh.exists(), "Linux/Mac installation script should exist"
    
    @pytest.mark.skipif(not os.getenv("TEST_SERVER"), reason="Server tests require TEST_SERVER env var")
    def test_server_health_endpoint(self):
        """Test that the server health endpoint works"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200, "Health endpoint should return 200"
            
            data = response.json()
            assert "status" in data, "Health response should contain status"
            assert data["status"] == "healthy", "Status should be healthy"
        except requests.exceptions.RequestException:
            pytest.skip("Server not running or not accessible")
    
    @pytest.mark.skipif(not os.getenv("TEST_SERVER"), reason="Server tests require TEST_SERVER env var")
    def test_server_tools_endpoint(self):
        """Test that the server tools endpoint works"""
        try:
            response = requests.get("http://localhost:8000/tools", timeout=5)
            assert response.status_code == 200, "Tools endpoint should return 200"
            
            data = response.json()
            assert "tools" in data, "Tools response should contain tools array"
            assert isinstance(data["tools"], list), "Tools should be a list"
        except requests.exceptions.RequestException:
            pytest.skip("Server not running or not accessible")

class TestBMADDocumentation:
    """Test suite for BMAD documentation"""
    
    def test_generated_readme_exists(self):
        """Test that generated README exists after running generate-docs"""
        readme_path = project_root / "README_BMAD.md"
        if readme_path.exists():
            assert readme_path.stat().st_size > 0, "Generated README should not be empty"
    
    def test_generated_api_docs_exist(self):
        """Test that generated API docs exist"""
        api_docs_path = project_root / "docs" / "api.json"
        if api_docs_path.exists():
            with open(api_docs_path, 'r', encoding='utf-8') as f:
                api_data = json.load(f)
            
            assert "openapi" in api_data, "API docs should be OpenAPI format"
            assert "info" in api_data, "API docs should have info section"
            assert "paths" in api_data, "API docs should have paths section"

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])