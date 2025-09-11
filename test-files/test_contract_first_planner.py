"""
Unit Tests for Contract-First Planner Agent
==========================================

Comprehensive test suite for the enhanced PlannerAgent with JSON-only output validation,
business requirements extraction, entity relationship mapping, and shared state management.
"""

import json
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_v1.planner_agent import (
    create_contract_first_planner,
    PROJECT_PLAN_SCHEMA,
    validate_project_plan_schema,
    extract_business_requirements,
    generate_entity_relationships
)
from tools_v1.shared_state_tools import JSONValidator


class TestContractFirstPlanner:
    """Test suite for Contract-First Planner Agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.planner = create_contract_first_planner()
        self.mock_team_state = {
            "project_plan": None,
            "api_spec": None,
            "current_phase": "planning"
        }
        
    def test_planner_agent_creation(self):
        """Test that planner agent is created with correct configuration"""
        assert self.planner.name == "Contract-First Planner"
        assert "Contract-First Planning Specialist" in self.planner.role
        assert len(self.planner.tools) >= 6  # Should have all required tools
        
        # Check that required tools are present
        tool_names = [tool.name for tool in self.planner.tools]
        required_tools = [
            "update_project_plan",
            "get_project_plan", 
            "validate_project_plan_schema",
            "validate_agent_json_output",
            "get_shared_state_summary"
        ]
        
        for required_tool in required_tools:
            assert required_tool in tool_names
    
    def test_project_plan_schema_validation(self):
        """Test project plan schema validation"""
        # Valid project plan
        valid_plan = {
            "project_name": "Todo App",
            "project_description": "A simple todo application",
            "business_goals": ["Manage tasks efficiently"],
            "features": [{
                "name": "Task Management",
                "description": "Create and manage tasks",
                "priority": "high",
                "complexity": "simple",
                "dependencies": []
            }],
            "entities": [{
                "name": "Task",
                "description": "A todo task",
                "fields": [{
                    "name": "title",
                    "type": "string",
                    "required": True,
                    "constraints": "max 100 characters"
                }],
                "relationships": [],
                "business_rules": []
            }],
            "api_surface": ["Task CRUD operations"],
            "auth_policy": "jwt_with_refresh",
            "tech_stack": {
                "frontend": "React+TS+Tailwind",
                "backend": "FastAPI",
                "database": "MongoDB"
            },
            "nonfunctional_requirements": ["Performance"],
            "environment_vars": ["MONGO_URI"],
            "deliverables_milestones": [{
                "milestone": "MVP",
                "deliverables": ["Task model"],
                "acceptance_criteria": ["Users can create tasks"]
            }]
        }
        
        # Test valid plan
        mock_agent = Mock()
        result = validate_project_plan_schema(mock_agent, json.dumps(valid_plan))
        assert "✅ Project plan schema validation passed" in result
        
        # Test invalid JSON
        result = validate_project_plan_schema(mock_agent, "invalid json")
        assert "❌ Invalid JSON" in result
        
        # Test missing required field
        invalid_plan = valid_plan.copy()
        del invalid_plan["project_name"]
        result = validate_project_plan_schema(mock_agent, json.dumps(invalid_plan))
        assert "❌ Schema validation failed" in result
    
    def test_json_validator_markdown_detection(self):
        """Test JSON validator detects markdown and comments"""
        # Test valid JSON
        valid_json = '{"test": "value"}'
        assert not JSONValidator.has_markdown_or_comments(valid_json)
        
        # Test markdown indicators
        markdown_examples = [
            '```json\n{"test": "value"}\n```',
            '## Header\n{"test": "value"}',
            '{"test": "value"} // comment',
            '<!-- comment -->{"test": "value"}',
            '**bold** {"test": "value"}',
            '[link](url) {"test": "value"}'
        ]
        
        for example in markdown_examples:
            assert JSONValidator.has_markdown_or_comments(example)
    
    def test_business_requirements_extraction(self):
        """Test business requirements extraction tool"""
        mock_agent = Mock()
        user_request = "Build a todo app where users can create and manage tasks"
        
        result = extract_business_requirements(mock_agent, user_request)
        
        # Should return structured analysis
        assert "📋 Business Requirements Analysis Template" in result
        assert "original_request" in result
        assert user_request in result
        assert "React+TS+Tailwind" in result
        assert "FastAPI" in result
        assert "MongoDB" in result
        assert "jwt_with_refresh" in result
    
    def test_entity_relationships_generation(self):
        """Test entity relationship generation tool"""
        mock_agent = Mock()
        
        entities = [
            {
                "name": "User",
                "relationships": ["one-to-many with Task"]
            },
            {
                "name": "Task", 
                "relationships": ["many-to-one with User"]
            }
        ]
        
        result = generate_entity_relationships(mock_agent, json.dumps(entities))
        
        # Should return relationship analysis
        assert "🔗 Entity Relationship Analysis" in result
        assert "entity_count" in result
        assert "relationship_patterns" in result
        
        # Test invalid JSON
        result = generate_entity_relationships(mock_agent, "invalid json")
        assert "❌ Invalid entities JSON" in result
    
    def test_tech_stack_enforcement(self):
        """Test that tech stack is properly enforced in schema"""
        # Valid tech stack
        valid_tech_stack = {
            "frontend": "React+TS+Tailwind",
            "backend": "FastAPI", 
            "database": "MongoDB"
        }
        
        # Test schema allows only valid values
        schema_tech_stack = PROJECT_PLAN_SCHEMA["properties"]["tech_stack"]
        
        assert schema_tech_stack["properties"]["frontend"]["enum"] == ["React+TS+Tailwind"]
        assert schema_tech_stack["properties"]["backend"]["enum"] == ["FastAPI"]
        assert schema_tech_stack["properties"]["database"]["enum"] == ["MongoDB"]
        
        # Test auth policy enforcement
        auth_schema = PROJECT_PLAN_SCHEMA["properties"]["auth_policy"]
        assert auth_schema["enum"] == ["jwt_with_refresh"]
    
    def test_feature_priority_and_complexity_validation(self):
        """Test feature priority and complexity validation"""
        feature_schema = PROJECT_PLAN_SCHEMA["properties"]["features"]["items"]["properties"]
        
        # Check priority enum
        assert set(feature_schema["priority"]["enum"]) == {"high", "medium", "low"}
        
        # Check complexity enum  
        assert set(feature_schema["complexity"]["enum"]) == {"simple", "moderate", "complex"}
    
    def test_shared_state_integration(self):
        """Test shared state integration with mock team state"""
        mock_agent = Mock()
        mock_agent.team_session_state = self.mock_team_state
        mock_agent.name = "Test Planner"
        
        # Test updating project plan
        from tools_v1.shared_state_tools import update_project_plan
        
        valid_plan = {"project_name": "Test Project", "description": "Test"}
        result = update_project_plan(mock_agent, json.dumps(valid_plan))
        
        assert "✅ Project plan updated successfully" in result
        assert mock_agent.team_session_state["project_plan"] == valid_plan
        assert "project_plan_updated" in mock_agent.team_session_state
        assert mock_agent.team_session_state["project_plan_agent"] == "Test Planner"
    
    def test_json_output_validation(self):
        """Test JSON output validation tool"""
        from tools_v1.shared_state_tools import validate_agent_json_output
        
        mock_agent = Mock()
        
        # Test valid JSON
        valid_json = '{"test": "value"}'
        result = validate_agent_json_output(mock_agent, valid_json)
        assert "✅ Valid JSON output" in result
        
        # Test JSON with markdown
        json_with_markdown = '```json\n{"test": "value"}\n```'
        result = validate_agent_json_output(mock_agent, json_with_markdown)
        assert "❌ Output contains markdown" in result
        
        # Test invalid JSON
        invalid_json = '{"test": value}'  # Missing quotes
        result = validate_agent_json_output(mock_agent, invalid_json)
        assert "❌ Invalid JSON output" in result
    
    def test_agent_instructions_compliance(self):
        """Test that agent instructions enforce contract-first principles"""
        instructions = self.planner.instructions
        
        # Check for key contract-first principles
        instructions_text = " ".join(instructions)
        
        assert "JSON" in instructions_text
        assert "React+TS+Tailwind" in instructions_text
        assert "FastAPI" in instructions_text
        assert "MongoDB" in instructions_text
        assert "jwt_with_refresh" in instructions_text
        assert "NEVER generate OpenAPI" in instructions_text or "never generate API" in instructions_text.lower()
        assert "shared state" in instructions_text.lower()
    
    def test_separation_of_concerns(self):
        """Test that planner doesn't overstep into other agent responsibilities"""
        instructions = self.planner.instructions
        instructions_text = " ".join(instructions).lower()
        
        # Should NOT include API specification details
        forbidden_terms = [
            "openapi specification",
            "api paths", 
            "http methods",
            "request schemas",
            "response schemas",
            "status codes"
        ]
        
        # Check that planner is instructed NOT to do these things
        for term in forbidden_terms:
            # Should either not mention it, or explicitly say not to do it
            if term in instructions_text:
                # If mentioned, should be in context of "don't do this"
                assert any(negative in instructions_text for negative in ["never", "not", "don't", "avoid"])


class TestProjectPlanGeneration:
    """Test suite for project plan generation scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.planner = create_contract_first_planner()
    
    def test_todo_app_plan_structure(self):
        """Test project plan structure for a todo app scenario"""
        # This would be the expected structure for a todo app
        expected_entities = ["User", "Task"]
        expected_features = ["User Authentication", "Task Management", "Task Filtering"]
        expected_api_surface = ["Authentication endpoints", "Task CRUD operations", "User management"]
        
        # Validate that our schema supports these requirements
        mock_plan = {
            "project_name": "Todo Application",
            "project_description": "A task management application",
            "business_goals": ["Enable users to manage their daily tasks efficiently"],
            "features": [
                {
                    "name": "User Authentication",
                    "description": "User registration and login system",
                    "priority": "high",
                    "complexity": "moderate",
                    "dependencies": []
                },
                {
                    "name": "Task Management", 
                    "description": "Create, read, update, delete tasks",
                    "priority": "high",
                    "complexity": "simple",
                    "dependencies": ["User Authentication"]
                }
            ],
            "entities": [
                {
                    "name": "User",
                    "description": "Application user with authentication",
                    "fields": [
                        {"name": "email", "type": "string", "required": True, "constraints": "unique, valid email"},
                        {"name": "password_hash", "type": "string", "required": True, "constraints": "bcrypt hashed"}
                    ],
                    "relationships": ["one-to-many with Task"],
                    "business_rules": ["Email must be unique", "Password must be hashed"]
                },
                {
                    "name": "Task",
                    "description": "A todo task item",
                    "fields": [
                        {"name": "title", "type": "string", "required": True, "constraints": "max 100 chars"},
                        {"name": "completed", "type": "boolean", "required": True, "constraints": "default false"}
                    ],
                    "relationships": ["many-to-one with User"],
                    "business_rules": ["Users can only access their own tasks"]
                }
            ],
            "api_surface": expected_api_surface,
            "auth_policy": "jwt_with_refresh",
            "tech_stack": {
                "frontend": "React+TS+Tailwind",
                "backend": "FastAPI",
                "database": "MongoDB"
            },
            "nonfunctional_requirements": ["Responsive design", "Fast task loading", "Secure authentication"],
            "environment_vars": ["MONGO_URI", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"],
            "deliverables_milestones": [
                {
                    "milestone": "Authentication System",
                    "deliverables": ["User model", "Auth endpoints", "JWT implementation"],
                    "acceptance_criteria": ["Users can register and login", "JWT tokens are issued and validated"]
                },
                {
                    "milestone": "Task Management",
                    "deliverables": ["Task model", "Task CRUD endpoints", "Task UI components"],
                    "acceptance_criteria": ["Users can create, view, edit, and delete tasks"]
                }
            ],
            "notes_for_spec": [
                "Implement proper JWT refresh token rotation",
                "Ensure task ownership validation on all operations",
                "Include task filtering and sorting capabilities"
            ]
        }
        
        # Validate against schema
        validation_result = JSONValidator.validate_against_schema(mock_plan, PROJECT_PLAN_SCHEMA)
        assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"
    
    def test_e_commerce_plan_structure(self):
        """Test project plan structure for an e-commerce scenario"""
        mock_plan = {
            "project_name": "E-Commerce Platform",
            "project_description": "Online shopping platform with product catalog and order management",
            "business_goals": ["Enable online product sales", "Manage inventory", "Process customer orders"],
            "features": [
                {
                    "name": "Product Catalog",
                    "description": "Browse and search products",
                    "priority": "high",
                    "complexity": "moderate",
                    "dependencies": []
                },
                {
                    "name": "Shopping Cart",
                    "description": "Add products to cart and checkout",
                    "priority": "high", 
                    "complexity": "complex",
                    "dependencies": ["Product Catalog", "User Authentication"]
                }
            ],
            "entities": [
                {
                    "name": "Product",
                    "description": "Product in the catalog",
                    "fields": [
                        {"name": "name", "type": "string", "required": True, "constraints": "max 200 chars"},
                        {"name": "price", "type": "decimal", "required": True, "constraints": "positive value"}
                    ],
                    "relationships": ["many-to-many with Order"],
                    "business_rules": ["Price must be positive", "Name must be unique per category"]
                }
            ],
            "api_surface": ["Product catalog endpoints", "Order management endpoints", "User authentication"],
            "auth_policy": "jwt_with_refresh",
            "tech_stack": {
                "frontend": "React+TS+Tailwind",
                "backend": "FastAPI",
                "database": "MongoDB"
            },
            "nonfunctional_requirements": ["High availability", "Payment security", "Scalable product search"],
            "environment_vars": ["MONGO_URI", "JWT_SECRET_KEY", "PAYMENT_GATEWAY_KEY"],
            "deliverables_milestones": [
                {
                    "milestone": "Product Catalog MVP",
                    "deliverables": ["Product model", "Catalog API", "Product listing UI"],
                    "acceptance_criteria": ["Users can browse and search products"]
                }
            ],
            "notes_for_spec": ["Integrate with payment gateway", "Implement inventory tracking"]
        }
        
        # Validate against schema
        validation_result = JSONValidator.validate_against_schema(mock_plan, PROJECT_PLAN_SCHEMA)
        assert validation_result["valid"], f"Schema validation failed: {validation_result['errors']}"


class TestJSONOutputValidation:
    """Test suite specifically for JSON output validation"""
    
    def test_strict_json_validation(self):
        """Test strict JSON validation without markdown"""
        # Valid JSON examples
        valid_examples = [
            '{"simple": "object"}',
            '{"nested": {"object": "value"}}',
            '{"array": ["item1", "item2"]}',
            '{"number": 123, "boolean": true, "null": null}'
        ]
        
        for example in valid_examples:
            result = JSONValidator.validate_json_string(example)
            assert result["valid"], f"Should be valid JSON: {example}"
            assert not JSONValidator.has_markdown_or_comments(example)
    
    def test_markdown_detection(self):
        """Test detection of various markdown formats"""
        markdown_examples = [
            '```json\n{"test": "value"}\n```',
            '## Project Plan\n{"test": "value"}',
            '**Important:** {"test": "value"}',
            '{"test": "value"}\n\n*Note: This is a comment*',
            '<!-- HTML comment -->{"test": "value"}',
            '// JavaScript comment\n{"test": "value"}',
            '# Python comment\n{"test": "value"}'
        ]
        
        for example in markdown_examples:
            assert JSONValidator.has_markdown_or_comments(example), f"Should detect markdown: {example}"
    
    def test_json_parsing_edge_cases(self):
        """Test JSON parsing with edge cases"""
        # Invalid JSON examples
        invalid_examples = [
            '{"missing": quote}',
            '{"trailing": "comma",}',
            '{unquoted: "key"}',
            '{"unclosed": "string}',
            '{"duplicate": "key", "duplicate": "key2"}'  # This is actually valid JSON, last value wins
        ]
        
        for example in invalid_examples[:-1]:  # Skip the last one as it's valid
            result = JSONValidator.validate_json_string(example)
            assert not result["valid"], f"Should be invalid JSON: {example}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])