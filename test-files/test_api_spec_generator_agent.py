"""
Unit Tests for ApiSpecGenerator Agent
===================================

This test suite validates the ApiSpecGenerator Agent's functionality including:
- OpenAPI 3.1 specification generation
- JWT bearer authentication schema generation
- Specification validation using swagger-parser
- Revision management with semantic versioning
- JSON-only output validation
- Contract compliance validation

Test Categories:
1. OpenAPI Specification Generation Tests
2. JWT Authentication Schema Tests
3. Specification Validation Tests
4. Revision Management Tests
5. JSON Output Validation Tests
6. Integration Tests with Shared State
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agents_v1.api_spec_generator_agent as api_agent
from agents_v1.api_spec_generator_agent import (
    api_spec_generator_agent,
    OpenAPIValidator
)
from tools_v1.shared_state_tools import JSONValidator, RevisionManager


class TestOpenAPIValidator(unittest.TestCase):
    """Test OpenAPI validation utilities"""
    
    def test_validate_openapi_spec_valid(self):
        """Test validation of a valid OpenAPI 3.1 specification"""
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
    
    def test_validate_openapi_spec_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_spec = {
            "openapi": "3.1.0"
            # Missing info and paths
        }
        
        result = OpenAPIValidator.validate_openapi_spec(invalid_spec)
        
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(issue["rule"] == "required_field" for issue in result["issues"]))
    
    def test_validate_openapi_spec_wrong_version(self):
        """Test validation with wrong OpenAPI version"""
        invalid_spec = {
            "openapi": "3.0.0",  # Should be 3.1.x
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }
        
        result = OpenAPIValidator.validate_openapi_spec(invalid_spec)
        
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(issue["rule"] == "openapi_version" for issue in result["issues"]))
    
    def test_create_jwt_security_scheme(self):
        """Test JWT security scheme creation"""
        jwt_scheme = OpenAPIValidator.create_jwt_security_scheme()
        
        self.assertIn("bearerAuth", jwt_scheme)
        self.assertEqual(jwt_scheme["bearerAuth"]["type"], "http")
        self.assertEqual(jwt_scheme["bearerAuth"]["scheme"], "bearer")
        self.assertEqual(jwt_scheme["bearerAuth"]["bearerFormat"], "JWT")
    
    def test_create_standard_responses(self):
        """Test standard HTTP response creation"""
        responses = OpenAPIValidator.create_standard_responses()
        
        required_codes = ["201", "400", "401", "404"]
        for code in required_codes:
            self.assertIn(code, responses)
            self.assertIn("description", responses[code])
            self.assertIn("content", responses[code])


class TestJSONValidator(unittest.TestCase):
    """Test JSON validation utilities"""
    
    def test_validate_json_string_valid(self):
        """Test validation of valid JSON string"""
        valid_json = '{"test": "value", "number": 123}'
        
        result = JSONValidator.validate_json_string(valid_json)
        
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["test"], "value")
        self.assertEqual(result["data"]["number"], 123)
        self.assertIsNone(result["error"])
    
    def test_validate_json_string_invalid(self):
        """Test validation of invalid JSON string"""
        invalid_json = '{"test": "value", "number": 123'  # Missing closing brace
        
        result = JSONValidator.validate_json_string(invalid_json)
        
        self.assertFalse(result["valid"])
        self.assertIsNone(result["data"])
        self.assertIsNotNone(result["error"])
    
    def test_has_markdown_or_comments_true(self):
        """Test detection of markdown and comments"""
        test_cases = [
            "```json\n{\"test\": \"value\"}\n```",
            "## Header\n{\"test\": \"value\"}",
            "// Comment\n{\"test\": \"value\"}",
            "<!-- HTML comment -->{\"test\": \"value\"}",
            "**Bold text** {\"test\": \"value\"}"
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                self.assertTrue(JSONValidator.has_markdown_or_comments(test_case))
    
    def test_has_markdown_or_comments_false(self):
        """Test clean JSON without markdown or comments"""
        clean_json = '{"test": "value", "array": [1, 2, 3], "nested": {"key": "value"}}'
        
        self.assertFalse(JSONValidator.has_markdown_or_comments(clean_json))


class TestRevisionManager(unittest.TestCase):
    """Test revision management utilities"""
    
    def test_parse_version_valid(self):
        """Test parsing valid semantic version"""
        version = "2.5.3"
        
        result = RevisionManager.parse_version(version)
        
        self.assertEqual(result["major"], 2)
        self.assertEqual(result["minor"], 5)
        self.assertEqual(result["patch"], 3)
    
    def test_parse_version_partial(self):
        """Test parsing partial version strings"""
        test_cases = [
            ("1.2", {"major": 1, "minor": 2, "patch": 0}),
            ("3", {"major": 3, "minor": 0, "patch": 0}),
            ("invalid", {"major": 1, "minor": 0, "patch": 0})
        ]
        
        for version, expected in test_cases:
            with self.subTest(version=version):
                result = RevisionManager.parse_version(version)
                self.assertEqual(result, expected)
    
    def test_increment_version_major(self):
        """Test major version increment"""
        current = "1.5.3"
        
        result = RevisionManager.increment_version(current, "major")
        
        self.assertEqual(result, "2.0.0")
    
    def test_increment_version_minor(self):
        """Test minor version increment"""
        current = "1.5.3"
        
        result = RevisionManager.increment_version(current, "minor")
        
        self.assertEqual(result, "1.6.0")
    
    def test_increment_version_patch(self):
        """Test patch version increment"""
        current = "1.5.3"
        
        result = RevisionManager.increment_version(current, "patch")
        
        self.assertEqual(result, "1.5.4")
    
    def test_increment_version_special_types(self):
        """Test special change types"""
        current = "1.5.3"
        
        # planner_regen should increment major
        result1 = RevisionManager.increment_version(current, "planner_regen")
        self.assertEqual(result1, "2.0.0")
        
        # spec_regen should increment minor
        result2 = RevisionManager.increment_version(current, "spec_regen")
        self.assertEqual(result2, "1.6.0")
    
    def test_create_revision_metadata(self):
        """Test revision metadata creation"""
        metadata = RevisionManager.create_revision_metadata(
            "TestAgent", "minor", "Added new feature"
        )
        
        self.assertEqual(metadata["agent"], "TestAgent")
        self.assertEqual(metadata["change_type"], "minor")
        self.assertEqual(metadata["description"], "Added new feature")
        self.assertIn("timestamp", metadata)
        self.assertIn("revision_id", metadata)


class TestOpenAPISpecificationGeneration(unittest.TestCase):
    """Test OpenAPI specification generation from project plans"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = Mock()
        self.mock_agent.name = "TestAgent"
        
        self.sample_project_plan = {
            "project_name": "Todo App",
            "project_description": "A simple todo application",
            "auth_policy": "jwt_with_refresh",
            "entities": [
                {
                    "name": "Task",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "description", "type": "string", "required": False},
                        {"name": "completed", "type": "boolean", "required": True},
                        {"name": "priority", "type": "integer", "required": False}
                    ]
                },
                {
                    "name": "User",
                    "fields": [
                        {"name": "email", "type": "string", "required": True},
                        {"name": "username", "type": "string", "required": True}
                    ]
                }
            ]
        }
    
    def test_generate_openapi_specification_basic(self):
        """Test basic OpenAPI specification generation"""
        project_plan_json = json.dumps(self.sample_project_plan)
        
        result = api_agent.generate_openapi_specification(self.mock_agent, project_plan_json)
        
        self.assertFalse(result.startswith("❌"))
        
        # Parse the result
        spec = json.loads(result)
        
        # Validate basic structure
        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertEqual(spec["info"]["title"], "Todo App API")
        self.assertIn("paths", spec)
        self.assertIn("components", spec)
    
    def test_generate_openapi_specification_entities(self):
        """Test entity schema generation"""
        project_plan_json = json.dumps(self.sample_project_plan)
        
        result = generate_openapi_specification(self.mock_agent, project_plan_json)
        spec = json.loads(result)
        
        # Check entity schemas
        self.assertIn("Task", spec["components"]["schemas"])
        self.assertIn("TaskCreate", spec["components"]["schemas"])
        self.assertIn("User", spec["components"]["schemas"])
        self.assertIn("UserCreate", spec["components"]["schemas"])
        
        # Check Task schema structure
        task_schema = spec["components"]["schemas"]["Task"]
        self.assertEqual(task_schema["type"], "object")
        self.assertIn("title", task_schema["properties"])
        self.assertIn("completed", task_schema["properties"])
        self.assertIn("_id", task_schema["properties"])
        
        # Check required fields
        self.assertIn("title", task_schema["required"])
        self.assertIn("completed", task_schema["required"])
        
        # Check TaskCreate schema (should not have _id)
        task_create_schema = spec["components"]["schemas"]["TaskCreate"]
        self.assertNotIn("_id", task_create_schema["properties"])
    
    def test_generate_openapi_specification_paths(self):
        """Test API path generation"""
        project_plan_json = json.dumps(self.sample_project_plan)
        
        result = generate_openapi_specification(self.mock_agent, project_plan_json)
        spec = json.loads(result)
        
        # Check generated paths
        expected_paths = ["/tasks", "/tasks/{id}", "/users", "/users/{id}"]
        for path in expected_paths:
            self.assertIn(path, spec["paths"])
        
        # Check CRUD operations for tasks
        tasks_path = spec["paths"]["/tasks"]
        self.assertIn("get", tasks_path)
        self.assertIn("post", tasks_path)
        
        task_by_id_path = spec["paths"]["/tasks/{id}"]
        self.assertIn("get", task_by_id_path)
        self.assertIn("put", task_by_id_path)
        self.assertIn("delete", task_by_id_path)
    
    def test_generate_openapi_specification_jwt_auth(self):
        """Test JWT authentication schema generation"""
        project_plan_json = json.dumps(self.sample_project_plan)
        
        result = generate_openapi_specification(self.mock_agent, project_plan_json)
        spec = json.loads(result)
        
        # Check JWT security scheme
        self.assertIn("bearerAuth", spec["components"]["securitySchemes"])
        bearer_auth = spec["components"]["securitySchemes"]["bearerAuth"]
        self.assertEqual(bearer_auth["type"], "http")
        self.assertEqual(bearer_auth["scheme"], "bearer")
        self.assertEqual(bearer_auth["bearerFormat"], "JWT")
        
        # Check authentication endpoints
        auth_endpoints = ["/auth/register", "/auth/login", "/auth/refresh"]
        for endpoint in auth_endpoints:
            self.assertIn(endpoint, spec["paths"])
        
        # Check authentication schemas
        auth_schemas = ["LoginRequest", "TokenResponse", "UserCreate"]
        for schema in auth_schemas:
            self.assertIn(schema, spec["components"]["schemas"])
    
    def test_generate_openapi_specification_security_applied(self):
        """Test that JWT security is applied to endpoints"""
        project_plan_json = json.dumps(self.sample_project_plan)
        
        result = generate_openapi_specification(self.mock_agent, project_plan_json)
        spec = json.loads(result)
        
        # Check that CRUD endpoints have security
        tasks_get = spec["paths"]["/tasks"]["get"]
        self.assertIn("security", tasks_get)
        self.assertEqual(tasks_get["security"], [{"bearerAuth": []}])
        
        # Check that auth endpoints don't have security (except refresh)
        register_post = spec["paths"]["/auth/register"]["post"]
        self.assertNotIn("security", register_post)
        
        login_post = spec["paths"]["/auth/login"]["post"]
        self.assertNotIn("security", login_post)
    
    def test_generate_openapi_specification_invalid_json(self):
        """Test handling of invalid project plan JSON"""
        invalid_json = '{"project_name": "Test"'  # Missing closing brace
        
        result = generate_openapi_specification(self.mock_agent, invalid_json)
        
        self.assertTrue(result.startswith("❌"))
        self.assertIn("Invalid project plan JSON", result)


class TestSpecificationValidation(unittest.TestCase):
    """Test OpenAPI specification validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = Mock()
        self.mock_agent.name = "TestAgent"
        
        self.valid_spec = {
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
            },
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
    
    def test_validate_openapi_specification_valid(self):
        """Test validation of valid specification"""
        spec_json = json.dumps(self.valid_spec)
        
        result = validate_openapi_specification(self.mock_agent, spec_json)
        
        self.assertFalse(result.startswith("❌"))
        
        validation_report = json.loads(result)
        self.assertEqual(validation_report["status"], "pass")
        self.assertEqual(len(validation_report["issues"]), 0)
    
    def test_validate_openapi_specification_invalid_json(self):
        """Test validation with invalid JSON"""
        invalid_json = '{"openapi": "3.1.0"'  # Missing closing brace
        
        result = validate_openapi_specification(self.mock_agent, invalid_json)
        
        validation_report = json.loads(result)
        self.assertEqual(validation_report["status"], "fail")
        self.assertTrue(any(issue["rule"] == "json_format" for issue in validation_report["issues"]))
    
    def test_validate_openapi_specification_missing_fields(self):
        """Test validation with missing required fields"""
        invalid_spec = {"openapi": "3.1.0"}  # Missing info and paths
        spec_json = json.dumps(invalid_spec)
        
        result = validate_openapi_specification(self.mock_agent, spec_json)
        
        validation_report = json.loads(result)
        self.assertEqual(validation_report["status"], "fail")
        self.assertTrue(len(validation_report["issues"]) > 0)


class TestAgentIntegration(unittest.TestCase):
    """Test agent integration with shared state tools"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = Mock()
        self.mock_agent.name = "ApiSpecGeneratorAgent"
        self.mock_agent.team_session_state = {}
        
        self.sample_project_plan = {
            "project_name": "Test API",
            "project_description": "Test API description",
            "auth_policy": "jwt_with_refresh",
            "entities": [
                {
                    "name": "Item",
                    "fields": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "value", "type": "integer", "required": False}
                    ]
                }
            ]
        }
    
    @patch('agents_v1.api_spec_generator_agent.get_project_plan')
    @patch('agents_v1.api_spec_generator_agent.update_api_spec')
    def test_create_api_spec_with_validation_success(self, mock_update_api_spec, mock_get_project_plan):
        """Test successful API spec creation with validation"""
        # Mock project plan retrieval
        mock_get_project_plan.return_value = json.dumps(self.sample_project_plan)
        
        # Mock successful update
        mock_update_api_spec.return_value = "✅ API specification updated to revision 1.0.0 in shared team state"
        
        result = create_api_spec_with_validation(self.mock_agent, "minor")
        
        self.assertTrue(result.startswith("✅"))
        self.assertIn("API specification created successfully", result)
        
        # Verify tools were called
        mock_get_project_plan.assert_called_once_with(self.mock_agent)
        mock_update_api_spec.assert_called_once()
    
    @patch('agents_v1.api_spec_generator_agent.get_project_plan')
    def test_create_api_spec_with_validation_no_project_plan(self, mock_get_project_plan):
        """Test API spec creation when no project plan exists"""
        # Mock missing project plan
        mock_get_project_plan.return_value = "❌ No project plan available in shared state"
        
        result = create_api_spec_with_validation(self.mock_agent, "minor")
        
        self.assertTrue(result.startswith("❌"))
        self.assertIn("Cannot create API spec", result)
    
    @patch('agents_v1.api_spec_generator_agent.get_api_spec')
    @patch('agents_v1.api_spec_generator_agent.update_api_spec')
    def test_increment_api_spec_revision_success(self, mock_update_api_spec, mock_get_api_spec):
        """Test successful API spec revision increment"""
        # Mock current spec
        current_spec = {
            "revision": "1.2.3",
            "api_version": "v1",
            "spec_version": "3.1.0"
        }
        mock_get_api_spec.return_value = json.dumps(current_spec)
        
        # Mock successful update
        mock_update_api_spec.return_value = "✅ API specification updated to revision 1.3.0 in shared team state"
        
        result = increment_api_spec_revision(self.mock_agent, "minor", "Added new feature")
        
        self.assertTrue(result.startswith("✅"))
        self.assertIn("revision incremented to 1.3.0", result)
        
        # Verify tools were called
        mock_get_api_spec.assert_called_once_with(self.mock_agent)
        mock_update_api_spec.assert_called_once()


class TestAgentJSONOutput(unittest.TestCase):
    """Test agent JSON-only output validation"""
    
    def test_agent_produces_json_only(self):
        """Test that agent tools produce JSON-only output"""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        
        # Test project plan JSON
        project_plan = {
            "project_name": "Test",
            "entities": [{"name": "Item", "fields": []}]
        }
        project_plan_json = json.dumps(project_plan)
        
        # Generate specification
        result = generate_openapi_specification(mock_agent, project_plan_json)
        
        # Should not start with error
        self.assertFalse(result.startswith("❌"))
        
        # Should be valid JSON
        try:
            parsed = json.loads(result)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Agent output is not valid JSON")
        
        # Should not contain markdown
        self.assertFalse(JSONValidator.has_markdown_or_comments(result))


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOpenAPIValidator,
        TestJSONValidator,
        TestRevisionManager,
        TestOpenAPISpecificationGeneration,
        TestSpecificationValidation,
        TestAgentIntegration,
        TestAgentJSONOutput
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"API SPEC GENERATOR AGENT TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    print(f"\nTest suite {'PASSED' if exit_code == 0 else 'FAILED'}")
    exit(exit_code)