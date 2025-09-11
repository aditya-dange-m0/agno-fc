"""
Unit Tests for Frontend Agent Contract Compliance and Artifact Generation
========================================================================

Tests for the contract-first frontend agent's core functionality including:
- Contract compliance validation against OpenAPI specifications
- Artifact generation and file saving
- API integration tracking
- Component extraction
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from datetime import datetime

# Import the frontend agent tools
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_v1.frontend_agent import (
    validate_contract_compliance,
    save_generated_frontend_files,
    search_project_files,
    read_project_file,
    write_project_file,
    analyze_project_structure
)


class TestFrontendAgentContractCompliance(unittest.TestCase):
    """Test contract compliance validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = Mock()
        self.mock_agent.name = "Test Frontend Agent"
        
        # Sample OpenAPI specification
        self.sample_api_spec = {
            "openapi_spec": {
                "info": {
                    "title": "Test API",
                    "version": "1.0.0"
                },
                "paths": {
                    "/users": {
                        "get": {
                            "operationId": "getUsers",
                            "summary": "Get all users"
                        },
                        "post": {
                            "operationId": "createUser",
                            "summary": "Create a user"
                        }
                    },
                    "/users/{id}": {
                        "get": {
                            "operationId": "getUserById",
                            "summary": "Get user by ID"
                        }
                    }
                },
                "components": {
                    "securitySchemes": {
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer"
                        }
                    }
                }
            }
        }
        
        # Sample React code with API calls
        self.compliant_react_code = '''
import React, { useState, useEffect } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch('/users', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const createUser = async (userData) => {
    try {
      const response = await fetch('/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(userData)
      });
      return response.json();
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Users</h1>
      {loading ? (
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      ) : (
        <ul className="space-y-2">
          {users.map(user => (
            <li key={user.id} className="bg-white p-4 rounded shadow">
              {user.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default UserList;
'''
        
        # Non-compliant React code (missing API calls)
        self.non_compliant_react_code = '''
import React from 'react';

function SimpleComponent() {
  return (
    <div>
      <h1>Hello World</h1>
    </div>
  );
}

export default SimpleComponent;
'''

    def test_validate_contract_compliance_success(self):
        """Test successful contract compliance validation"""
        api_spec_json = json.dumps(self.sample_api_spec)
        
        result = validate_contract_compliance(
            self.mock_agent,
            self.compliant_react_code,
            api_spec_json
        )
        
        compliance_report = json.loads(result)
        
        # Should pass validation
        self.assertEqual(compliance_report["status"], "pass")
        self.assertTrue(compliance_report["auth_compliance"])
        self.assertGreater(len(compliance_report["validated_api_calls"]), 0)
        self.assertEqual(len(compliance_report["missing_api_calls"]), 1)  # GET /users/{id} not implemented
        
    def test_validate_contract_compliance_failure(self):
        """Test contract compliance validation failure"""
        api_spec_json = json.dumps(self.sample_api_spec)
        
        result = validate_contract_compliance(
            self.mock_agent,
            self.non_compliant_react_code,
            api_spec_json
        )
        
        compliance_report = json.loads(result)
        
        # Should fail validation
        self.assertEqual(compliance_report["status"], "fail")
        self.assertFalse(compliance_report["auth_compliance"])
        self.assertEqual(len(compliance_report["validated_api_calls"]), 0)
        self.assertGreater(len(compliance_report["missing_api_calls"]), 0)
        self.assertGreater(len(compliance_report["schema_mismatches"]), 0)

    def test_validate_contract_compliance_invalid_json(self):
        """Test contract compliance with invalid JSON"""
        invalid_json = "{ invalid json }"
        
        result = validate_contract_compliance(
            self.mock_agent,
            self.compliant_react_code,
            invalid_json
        )
        
        compliance_report = json.loads(result)
        
        # Should return error status
        self.assertEqual(compliance_report["status"], "error")
        self.assertIn("Invalid API specification JSON", compliance_report["error"])

    def test_validate_contract_compliance_missing_react_imports(self):
        """Test validation with missing React imports"""
        api_spec_json = json.dumps(self.sample_api_spec)
        code_without_react = "function Component() { return null; }"
        
        result = validate_contract_compliance(
            self.mock_agent,
            code_without_react,
            api_spec_json
        )
        
        compliance_report = json.loads(result)
        
        # Should fail due to missing React imports
        self.assertEqual(compliance_report["status"], "fail")
        self.assertIn("Missing React imports", compliance_report["schema_mismatches"])

    def test_validate_contract_compliance_missing_tailwind(self):
        """Test validation with missing Tailwind CSS"""
        api_spec_json = json.dumps(self.sample_api_spec)
        code_without_tailwind = '''
import React from 'react';
function Component() {
  return <div>No Tailwind classes</div>;
}
'''
        
        result = validate_contract_compliance(
            self.mock_agent,
            code_without_tailwind,
            api_spec_json
        )
        
        compliance_report = json.loads(result)
        
        # Should fail due to missing Tailwind classes
        self.assertEqual(compliance_report["status"], "fail")
        self.assertIn("Missing Tailwind CSS classes", compliance_report["schema_mismatches"])


class TestFrontendAgentFileOperations(unittest.TestCase):
    """Test file operation functionality"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test directory structure
        os.makedirs("generated/frontend/src", exist_ok=True)
        
        # Create sample files
        with open("generated/frontend/package.json", "w") as f:
            json.dump({"name": "test-app", "version": "1.0.0"}, f)
        
        with open("generated/frontend/src/App.tsx", "w") as f:
            f.write('''import React from 'react';
function App() {
  return <div className="container">Hello World</div>;
}
export default App;''')

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_analyze_project_structure(self):
        """Test project structure analysis"""
        result = analyze_project_structure()
        
        # Should detect generated files
        self.assertIn("Generated Files", result)
        self.assertIn("package.json", result)
        self.assertIn("App.tsx", result)
        self.assertIn("Configuration Status", result)

    def test_read_project_file_success(self):
        """Test successful file reading"""
        result = read_project_file("frontend/src/App.tsx")
        
        # Should return file content
        self.assertIn("Content of", result)
        self.assertIn("import React", result)
        self.assertIn("Hello World", result)

    def test_read_project_file_not_found(self):
        """Test reading non-existent file"""
        result = read_project_file("frontend/src/NonExistent.tsx")
        
        # Should return error message
        self.assertIn("File not found", result)

    def test_write_project_file_create(self):
        """Test creating new file"""
        content = "export const API_URL = 'http://localhost:8000';"
        result = write_project_file("frontend/src/config.ts", content, "create")
        
        # Should create file successfully
        self.assertIn("Created", result)
        self.assertTrue(os.path.exists("generated/frontend/src/config.ts"))
        
        # Verify content
        with open("generated/frontend/src/config.ts", "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_project_file_update(self):
        """Test updating existing file"""
        new_content = '''import React from 'react';
function App() {
  return <div className="container mx-auto">Updated App</div>;
}
export default App;'''
        
        result = write_project_file("frontend/src/App.tsx", new_content, "update")
        
        # Should update file successfully
        self.assertIn("Updated", result)
        
        # Verify content was updated
        with open("generated/frontend/src/App.tsx", "r") as f:
            content = f.read()
            self.assertIn("Updated App", content)
            self.assertIn("mx-auto", content)

    def test_write_project_file_append(self):
        """Test appending to existing file"""
        append_content = "\n// Additional comment"
        result = write_project_file("frontend/src/App.tsx", append_content, "append")
        
        # Should append successfully
        self.assertIn("Appended to", result)
        
        # Verify content was appended
        with open("generated/frontend/src/App.tsx", "r") as f:
            content = f.read()
            self.assertIn("Hello World", content)  # Original content
            self.assertIn("Additional comment", content)  # Appended content

    def test_search_project_files(self):
        """Test searching project files"""
        result = search_project_files("Hello World", "tsx,json")
        
        # Should find matches
        self.assertIn("Search results", result)
        self.assertIn("App.tsx", result)
        self.assertIn("Hello World", result)

    def test_search_project_files_no_matches(self):
        """Test searching with no matches"""
        result = search_project_files("NonExistentPattern", "tsx")
        
        # Should return no matches message
        self.assertIn("No matches found", result)


class TestFrontendAgentArtifactGeneration(unittest.TestCase):
    """Test artifact generation and saving functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Sample response with code artifacts
        self.sample_response = '''
Here's your React application:

<codeartifact type="react" filename="src/App.tsx" purpose="Main React application component" framework="react" complexity="moderate">
import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Hello World</h1>
        <p className="text-gray-600">Welcome to your React app!</p>
      </div>
    </div>
  );
}

export default App;
</codeartifact>

<codeartifact type="json" filename="package.json" purpose="NPM package configuration" framework="react" complexity="simple">
{
  "name": "my-react-app",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^4.9.5"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
</codeartifact>
'''

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_save_generated_frontend_files(self):
        """Test saving generated frontend files"""
        result = save_generated_frontend_files(self.sample_response)
        
        # Should save files successfully
        self.assertIn("Successfully saved", result)
        self.assertIn("frontend files", result)
        
        # Verify files were created
        self.assertTrue(os.path.exists("generated/frontend/src/App.tsx"))
        self.assertTrue(os.path.exists("generated/frontend/package.json"))
        
        # Verify content
        with open("generated/frontend/src/App.tsx", "r") as f:
            content = f.read()
            self.assertIn("import React", content)
            self.assertIn("Hello World", content)
            self.assertIn("className=", content)
        
        with open("generated/frontend/package.json", "r") as f:
            package_data = json.load(f)
            self.assertEqual(package_data["name"], "my-react-app")
            self.assertIn("react", package_data["dependencies"])

    def test_save_generated_frontend_files_no_artifacts(self):
        """Test saving with no artifacts found"""
        empty_response = "No code artifacts in this response."
        result = save_generated_frontend_files(empty_response)
        
        # Should return no artifacts message
        self.assertIn("No frontend code artifacts found", result)

    def test_save_generated_frontend_files_custom_path(self):
        """Test saving to custom path"""
        custom_path = "custom/frontend/path"
        result = save_generated_frontend_files(self.sample_response, custom_path)
        
        # Should save to custom path
        self.assertIn("Successfully saved", result)
        self.assertTrue(os.path.exists(f"{custom_path}/src/App.tsx"))
        self.assertTrue(os.path.exists(f"{custom_path}/package.json"))


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)