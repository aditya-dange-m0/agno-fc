"""
Simple Unit Tests for ApiSpecGenerator Agent
==========================================

Basic tests to verify the ApiSpecGenerator Agent functionality.
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_v1.api_spec_generator_agent import OpenAPIValidator
from tools_v1.shared_state_tools import JSONValidator, RevisionManager


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the ApiSpecGenerator components"""
    
    def test_openapi_validator_jwt_scheme(self):
        """Test JWT security scheme creation"""
        jwt_scheme = OpenAPIValidator.create_jwt_security_scheme()
        
        self.assertIn("bearerAuth", jwt_scheme)
        self.assertEqual(jwt_scheme["bearerAuth"]["type"], "http")
        self.assertEqual(jwt_scheme["bearerAuth"]["scheme"], "bearer")
        self.assertEqual(jwt_scheme["bearerAuth"]["bearerFormat"], "JWT")
    
    def test_openapi_validator_responses(self):
        """Test standard response creation"""
        responses = OpenAPIValidator.create_standard_responses()
        
        required_codes = ["201", "400", "401", "404"]
        for code in required_codes:
            self.assertIn(code, responses)
            self.assertIn("description", responses[code])
    
    def test_json_validator_valid_json(self):
        """Test JSON validation with valid input"""
        valid_json = '{"test": "value", "number": 123}'
        
        result = JSONValidator.validate_json_string(valid_json)
        
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["test"], "value")
        self.assertIsNone(result["error"])
    
    def test_json_validator_invalid_json(self):
        """Test JSON validation with invalid input"""
        invalid_json = '{"test": "value"'  # Missing closing brace
        
        result = JSONValidator.validate_json_string(invalid_json)
        
        self.assertFalse(result["valid"])
        self.assertIsNone(result["data"])
        self.assertIsNotNone(result["error"])
    
    def test_revision_manager_increment(self):
        """Test version increment functionality"""
        # Test major increment
        result = RevisionManager.increment_version("1.2.3", "major")
        self.assertEqual(result, "2.0.0")
        
        # Test minor increment
        result = RevisionManager.increment_version("1.2.3", "minor")
        self.assertEqual(result, "1.3.0")
        
        # Test patch increment
        result = RevisionManager.increment_version("1.2.3", "patch")
        self.assertEqual(result, "1.2.4")
    
    def test_openapi_spec_validation(self):
        """Test OpenAPI specification validation"""
        valid_spec = {
            "openapi": "3.1.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "responses": {
                            "200": {"description": "Success"}
                        }
                    }
                }
            }
        }
        
        result = OpenAPIValidator.validate_openapi_spec(valid_spec)
        
        self.assertEqual(result["status"], "pass")
        self.assertEqual(len(result["issues"]), 0)
    
    def test_openapi_spec_validation_missing_fields(self):
        """Test OpenAPI validation with missing required fields"""
        invalid_spec = {
            "openapi": "3.1.0"
            # Missing info and paths
        }
        
        result = OpenAPIValidator.validate_openapi_spec(invalid_spec)
        
        self.assertEqual(result["status"], "fail")
        self.assertTrue(len(result["issues"]) > 0)
        
        # Check for specific missing field errors
        missing_fields = [issue for issue in result["issues"] if issue["rule"] == "required_field"]
        self.assertTrue(len(missing_fields) > 0)


class TestAgentCreation(unittest.TestCase):
    """Test that the agent can be created successfully"""
    
    def test_agent_creation(self):
        """Test that the ApiSpecGenerator agent can be imported and created"""
        try:
            from agents_v1.api_spec_generator_agent import api_spec_generator_agent
            
            # Check basic agent properties
            self.assertEqual(api_spec_generator_agent.name, "ApiSpecGenerator Agent")
            self.assertEqual(api_spec_generator_agent.role, "OpenAPI 3.1 Contract Specification Expert")
            
            # Check that agent has required tools
            tool_names = [tool.name for tool in api_spec_generator_agent.tools]
            required_tools = [
                "get_project_plan",
                "generate_openapi_specification", 
                "validate_openapi_specification",
                "create_api_spec_with_validation"
            ]
            
            for required_tool in required_tools:
                self.assertIn(required_tool, tool_names)
                
        except ImportError as e:
            self.fail(f"Failed to import ApiSpecGenerator agent: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)