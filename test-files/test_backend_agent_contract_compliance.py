"""
Unit Tests for Backend Agent Contract Compliance and Artifact Generation
======================================================================

Tests for the enhanced backend agent's contract compliance validation
and artifact generation capabilities.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock the agno imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockAgent:
    """Mock agent for testing"""
    def __init__(self):
        self.name = "Test Backend Agent"
        self.team_session_state = {}

class TestBackendAgentContractCompliance(unittest.TestCase):
    """Test contract compliance functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = MockAgent()
        self.test_dir = tempfile.mkdtemp()
        
        # Sample API spec for testing
        self.sample_api_spec = {
            "revision": "1.0.0",
            "openapi_spec": {
                "info": {
                    "title": "Test API",
                    "version": "1.0.0",
                    "description": "Test API for contract compliance"
                },
                "paths": {
                    "/users": {
                        "get": {
                            "operationId": "get_users",
                            "summary": "Get all users",
                            "responses": {
                                "200": {
                                    "description": "List of users"
                                }
                            }
                        },
                        "post": {
                            "operationId": "create_user",
                            "summary": "Create a user",
                            "security": [{"bearerAuth": []}],
                            "responses": {
                                "201": {
                                    "description": "User created"
                                }
                            }
                        }
                    }
                },
                "components": {
                    "securitySchemes": {
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    },
                    "schemas": {
                        "User": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "email": {"type": "string"}
                            },
                            "required": ["name", "email"]
                        }
                    }
                }
            }
        }
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_api_spec_from_shared_state_success(self):
        """Test successful API spec retrieval"""
        # Set up mock agent with API spec
        self.mock_agent.team_session_state["api_spec"] = self.sample_api_spec
        
        # Import and test the function
        from agents_v1.backend_agent import get_api_spec_from_shared_state
        result = get_api_spec_from_shared_state(self.mock_agent)
        
        # Verify result
        self.assertIn("Test API", result)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["revision"], "1.0.0")
    
    def test_get_api_spec_from_shared_state_missing(self):
        """Test API spec retrieval when spec is missing"""
        # Import and test the function
        from agents_v1.backend_agent import get_api_spec_from_shared_state
        result = get_api_spec_from_shared_state(self.mock_agent)
        
        # Verify error message
        self.assertIn("No API specification available", result)
    
    def test_write_backend_report_to_shared_state_success(self):
        """Test successful backend report writing"""
        # Prepare test report
        test_report = {
            "implemented_endpoints": [
                {"path": "/users", "method": "GET", "status": "implemented"}
            ],
            "compliance_status": "pass"
        }
        
        # Import and test the function
        from agents_v1.backend_agent import write_backend_report_to_shared_state
        result = write_backend_report_to_shared_state(self.mock_agent, json.dumps(test_report))
        
        # Verify result
        self.assertIn("Backend report updated successfully", result)
        self.assertIn("backend_report", self.mock_agent.team_session_state)
        
        # Verify report content
        stored_report = self.mock_agent.team_session_state["backend_report"]
        self.assertEqual(stored_report["compliance_status"], "pass")
        self.assertIn("updated_at", stored_report)
        self.assertEqual(stored_report["updated_by"], "Test Backend Agent")
    
    def test_write_backend_report_invalid_json(self):
        """Test backend report writing with invalid JSON"""
        # Import and test the function
        from agents_v1.backend_agent import write_backend_report_to_shared_state
        result = write_backend_report_to_shared_state(self.mock_agent, "invalid json")
        
        # Verify error message
        self.assertIn("Invalid JSON in backend report", result)
    
    def test_validate_contract_compliance_success(self):
        """Test contract compliance validation with API spec"""
        # Set up mock agent with API spec
        self.mock_agent.team_session_state["api_spec"] = self.sample_api_spec
        
        # Import and test the function
        from agents_v1.backend_agent import validate_contract_compliance
        result = validate_contract_compliance(self.mock_agent, "Generated 3 files successfully")
        
        # Verify result
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["status"], "pass")
        self.assertEqual(parsed_result["api_spec_version"], "1.0.0")
        self.assertIn("validation_timestamp", parsed_result)
    
    def test_validate_contract_compliance_no_spec(self):
        """Test contract compliance validation without API spec"""
        # Import and test the function
        from agents_v1.backend_agent import validate_contract_compliance
        result = validate_contract_compliance(self.mock_agent, "Generated files")
        
        # Verify error result
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["status"], "error")
        self.assertIn("No API specification available", parsed_result["message"])


class TestArtifactGeneration(unittest.TestCase):
    """Test artifact generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_generated_files_with_artifacts(self):
        """Test saving files from response text with code artifacts"""
        # Sample response text with code artifacts
        response_text = '''
Here's your FastAPI application:

<codeartifact type="python" filename="app.py" purpose="Main FastAPI application" complexity="moderate">
from fastapi import FastAPI

app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
</codeartifact>

<codeartifact type="text" filename="requirements.txt" purpose="Python dependencies" complexity="simple">
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
</codeartifact>
        '''
        
        # Import and test the function
        from agents_v1.backend_agent import save_generated_files
        result = save_generated_files(response_text, "generated/backend")
        
        # Verify result
        self.assertIn("Successfully saved 2 files", result)
        self.assertIn("app.py", result)
        self.assertIn("requirements.txt", result)
        
        # Verify files were created
        self.assertTrue(os.path.exists("generated/backend/app.py"))
        self.assertTrue(os.path.exists("generated/backend/requirements.txt"))
        
        # Verify file contents
        with open("generated/backend/app.py", "r") as f:
            app_content = f.read()
            self.assertIn("from fastapi import FastAPI", app_content)
            self.assertIn("Hello World", app_content)
        
        with open("generated/backend/requirements.txt", "r") as f:
            req_content = f.read()
            self.assertIn("fastapi==0.104.1", req_content)
            self.assertIn("motor==3.3.2", req_content)
    
    def test_save_generated_files_no_artifacts(self):
        """Test saving files when no artifacts are found"""
        response_text = "This is just plain text with no code artifacts."
        
        # Import and test the function
        from agents_v1.backend_agent import save_generated_files
        result = save_generated_files(response_text)
        
        # Verify result
        self.assertIn("No code artifacts found", result)
    
    @patch('os.path.exists')
    @patch('builtins.open')
    @patch('os.makedirs')
    def test_write_project_file_create_mode(self, mock_makedirs, mock_open, mock_exists):
        """Test write_project_file in create mode"""
        mock_exists.return_value = False
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Import and test the function
        from agents_v1.backend_agent import write_project_file
        result = write_project_file("backend/test.py", "print('hello')", "create")
        
        # Verify result
        self.assertIn("Created generated/backend/test.py successfully", result)
        mock_makedirs.assert_called_once()
        mock_file.write.assert_called_once_with("print('hello')")
    
    @patch('os.path.exists')
    @patch('builtins.open')
    @patch('os.makedirs')
    @patch('shutil.copy2')
    def test_write_project_file_update_mode(self, mock_copy, mock_makedirs, mock_open, mock_exists):
        """Test write_project_file in update mode with backup"""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Import and test the function
        from agents_v1.backend_agent import write_project_file
        result = write_project_file("backend/test.py", "print('updated')", "update")
        
        # Verify result
        self.assertIn("Updated generated/backend/test.py successfully", result)
        mock_copy.assert_called_once()  # Backup was created
        mock_file.write.assert_called_once_with("print('updated')")


class TestProjectStructureAnalysis(unittest.TestCase):
    """Test project structure analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create sample project structure
        os.makedirs("generated/backend", exist_ok=True)
        os.makedirs("generated/frontend", exist_ok=True)
        
        with open("generated/backend/app.py", "w") as f:
            f.write("# FastAPI app")
        
        with open("generated/backend/requirements.txt", "w") as f:
            f.write("fastapi==0.104.1")
            
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_analyze_project_structure(self):
        """Test project structure analysis"""
        # Import and test the function
        from agents_v1.backend_agent import analyze_project_structure
        result = analyze_project_structure()
        
        # Verify result contains expected information
        self.assertIn("Current Project Structure", result)
        self.assertIn("Generated Files", result)
        self.assertIn("app.py", result)
        self.assertIn("requirements.txt", result)
        self.assertIn("Configuration Status", result)
        self.assertIn("FastAPI main application", result)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)