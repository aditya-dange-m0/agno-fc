"""
Unit Tests for Contract-First Shared State Management Tools
=========================================================

Comprehensive test suite for shared state tools and JSON validation utilities.
"""

import unittest
import json
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Import the tools and utilities to test
from shared_state_tools import (
    JSONValidator,
    RevisionManager,
    _update_project_plan_core,
    _get_project_plan_core,
    update_api_spec,
    get_api_spec,
    get_api_spec_revision_history,
    update_backend_report,
    get_backend_report,
    update_frontend_report,
    get_frontend_report,
    validate_agent_json_output,
    get_shared_state_summary
)


class TestJSONValidator(unittest.TestCase):
    """Test cases for JSONValidator utility class"""
    
    def test_validate_json_string_valid(self):
        """Test validation of valid JSON string"""
        valid_json = '{"name": "test", "value": 123}'
        result = JSONValidator.validate_json_string(valid_json)
        
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["name"], "test")
        self.assertEqual(result["data"]["value"], 123)
        self.assertIsNone(result["error"])
    
    def test_validate_json_string_invalid(self):
        """Test validation of invalid JSON string"""
        invalid_json = '{"name": "test", "value": 123'  # Missing closing brace
        result = JSONValidator.validate_json_string(invalid_json)
        
        self.assertFalse(result["valid"])
        self.assertIsNone(result["data"])
        self.assertIsNotNone(result["error"])
        self.assertIn("Invalid JSON", result["error"])
    
    def test_validate_against_schema_valid(self):
        """Test schema validation with valid data"""
        data = {"name": "test", "age": 25}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        
        result = JSONValidator.validate_against_schema(data, schema)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_validate_against_schema_invalid(self):
        """Test schema validation with invalid data"""
        data = {"name": "test", "age": "twenty-five"}  # age should be number
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        
        result = JSONValidator.validate_against_schema(data, schema)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)
    
    def test_has_markdown_or_comments_with_markdown(self):
        """Test detection of markdown formatting"""
        markdown_text = "```json\n{\"test\": true}\n```"
        result = JSONValidator.has_markdown_or_comments(markdown_text)
        self.assertTrue(result)
        
        markdown_text2 = "## Header\n{\"test\": true}"
        result2 = JSONValidator.has_markdown_or_comments(markdown_text2)
        self.assertTrue(result2)
    
    def test_has_markdown_or_comments_with_comments(self):
        """Test detection of comments"""
        comment_text = "// This is a comment\n{\"test\": true}"
        result = JSONValidator.has_markdown_or_comments(comment_text)
        self.assertTrue(result)
        
        comment_text2 = "<!-- HTML comment -->\n{\"test\": true}"
        result2 = JSONValidator.has_markdown_or_comments(comment_text2)
        self.assertTrue(result2)
    
    def test_has_markdown_or_comments_clean_json(self):
        """Test clean JSON without markdown or comments"""
        clean_json = '{"name": "test", "value": 123, "nested": {"key": "value"}}'
        result = JSONValidator.has_markdown_or_comments(clean_json)
        self.assertFalse(result)


class TestRevisionManager(unittest.TestCase):
    """Test cases for RevisionManager utility class"""
    
    def test_parse_version_valid(self):
        """Test parsing valid version strings"""
        result = RevisionManager.parse_version("1.2.3")
        self.assertEqual(result["major"], 1)
        self.assertEqual(result["minor"], 2)
        self.assertEqual(result["patch"], 3)
        
        result2 = RevisionManager.parse_version("2.0")
        self.assertEqual(result2["major"], 2)
        self.assertEqual(result2["minor"], 0)
        self.assertEqual(result2["patch"], 0)
    
    def test_parse_version_invalid(self):
        """Test parsing invalid version strings"""
        result = RevisionManager.parse_version("invalid")
        self.assertEqual(result["major"], 1)
        self.assertEqual(result["minor"], 0)
        self.assertEqual(result["patch"], 0)
    
    def test_increment_version_major(self):
        """Test major version increment"""
        result = RevisionManager.increment_version("1.2.3", "major")
        self.assertEqual(result, "2.0.0")
        
        result2 = RevisionManager.increment_version("1.2.3", "planner_regen")
        self.assertEqual(result2, "2.0.0")
    
    def test_increment_version_minor(self):
        """Test minor version increment"""
        result = RevisionManager.increment_version("1.2.3", "minor")
        self.assertEqual(result, "1.3.0")
        
        result2 = RevisionManager.increment_version("1.2.3", "spec_regen")
        self.assertEqual(result2, "1.3.0")
    
    def test_increment_version_patch(self):
        """Test patch version increment"""
        result = RevisionManager.increment_version("1.2.3", "patch")
        self.assertEqual(result, "1.2.4")
        
        result2 = RevisionManager.increment_version("1.2.3", "bug_fix")
        self.assertEqual(result2, "1.2.4")
    
    def test_create_revision_metadata(self):
        """Test creation of revision metadata"""
        result = RevisionManager.create_revision_metadata(
            "TestAgent", "minor", "Test change"
        )
        
        self.assertEqual(result["agent"], "TestAgent")
        self.assertEqual(result["change_type"], "minor")
        self.assertEqual(result["description"], "Test change")
        self.assertIn("timestamp", result)
        self.assertIn("revision_id", result)


class TestSharedStateTools(unittest.TestCase):
    """Test cases for shared state management tools"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = Mock()
        self.mock_agent.name = "TestAgent"
        self.mock_agent.team_session_state = {}
        # Ensure hasattr works correctly
        self.mock_agent.team_session_state = {}
    
    def test_update_project_plan_valid_json(self):
        """Test updating project plan with valid JSON"""
        valid_plan = '{"project_name": "Test Project", "description": "Test description"}'
        
        result = _update_project_plan_core(self.mock_agent, valid_plan)
        
        # Debug what we got
        print(f"Result: {result}")
        
        self.assertIn("✅", result)
        self.assertIn("successfully", result)
        self.assertIn("project_plan", self.mock_agent.team_session_state)
        self.assertEqual(
            self.mock_agent.team_session_state["project_plan"]["project_name"],
            "Test Project"
        )
    
    def test_update_project_plan_invalid_json(self):
        """Test updating project plan with invalid JSON"""
        invalid_plan = '{"project_name": "Test Project", "description": "Test description"'  # Missing brace
        
        result = _update_project_plan_core(self.mock_agent, invalid_plan)
        
        self.assertIn("❌", result)
        self.assertIn("Invalid JSON", result)
        self.assertNotIn("project_plan", self.mock_agent.team_session_state)
    
    def test_update_project_plan_with_markdown(self):
        """Test updating project plan with markdown content"""
        markdown_plan = '```json\n{"project_name": "Test Project"}\n```'
        
        result = _update_project_plan_core(self.mock_agent, markdown_plan)
        
        self.assertIn("❌", result)
        self.assertIn("markdown", result)
        self.assertNotIn("project_plan", self.mock_agent.team_session_state)
    
    def test_get_project_plan_exists(self):
        """Test getting existing project plan"""
        test_plan = {"project_name": "Test Project", "description": "Test description"}
        self.mock_agent.team_session_state["project_plan"] = test_plan
        
        result = _get_project_plan_core(self.mock_agent)
        
        # Should return JSON string
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["project_name"], "Test Project")
    
    def test_get_project_plan_missing(self):
        """Test getting project plan when none exists"""
        result = _get_project_plan_core(self.mock_agent)
        
        self.assertIn("❌", result)
        self.assertIn("No project plan", result)


if __name__ == '__main__':
    unittest.main()