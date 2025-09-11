"""
Simple test runner for Contract-First Planner Agent
==================================================

Basic test runner without pytest dependency to validate the planner implementation.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import using importlib for hyphenated module names
    import importlib.util
    
    # Load planner agent module
    planner_spec = importlib.util.spec_from_file_location(
        "planner_agent", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents-v1", "planner_agent.py")
    )
    planner_module = importlib.util.module_from_spec(planner_spec)
    planner_spec.loader.exec_module(planner_module)
    
    # Load shared state tools module
    tools_spec = importlib.util.spec_from_file_location(
        "shared_state_tools",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools_v1", "shared_state_tools.py")
    )
    tools_module = importlib.util.module_from_spec(tools_spec)
    tools_spec.loader.exec_module(tools_module)
    
    # Extract needed functions and classes
    create_contract_first_planner = planner_module.create_contract_first_planner
    PROJECT_PLAN_SCHEMA = planner_module.PROJECT_PLAN_SCHEMA
    validate_project_plan_schema = planner_module.validate_project_plan_schema
    extract_business_requirements = planner_module.extract_business_requirements
    generate_entity_relationships = planner_module.generate_entity_relationships
    
    JSONValidator = tools_module.JSONValidator
    update_project_plan = tools_module.update_project_plan
    validate_agent_json_output = tools_module.validate_agent_json_output
    
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_planner_creation():
    """Test planner agent creation"""
    try:
        planner = create_contract_first_planner()
        assert planner.name == "Contract-First Planner"
        assert len(planner.tools) >= 6
        print("✅ Planner creation test passed")
        return True
    except Exception as e:
        print(f"❌ Planner creation test failed: {e}")
        return False


def test_json_validation():
    """Test JSON validation utilities"""
    try:
        # Test valid JSON
        valid_json = '{"test": "value"}'
        result = JSONValidator.validate_json_string(valid_json)
        assert result["valid"] == True
        
        # Test invalid JSON
        invalid_json = '{"test": value}'
        result = JSONValidator.validate_json_string(invalid_json)
        assert result["valid"] == False
        
        # Test markdown detection
        markdown_json = '```json\n{"test": "value"}\n```'
        assert JSONValidator.has_markdown_or_comments(markdown_json) == True
        
        clean_json = '{"test": "value"}'
        assert JSONValidator.has_markdown_or_comments(clean_json) == False
        
        print("✅ JSON validation test passed")
        return True
    except Exception as e:
        print(f"❌ JSON validation test failed: {e}")
        return False


def test_project_plan_schema():
    """Test project plan schema validation"""
    try:
        # Create a valid project plan
        valid_plan = {
            "project_name": "Test App",
            "project_description": "A test application",
            "business_goals": ["Test goal"],
            "features": [{
                "name": "Test Feature",
                "description": "A test feature",
                "priority": "high",
                "complexity": "simple",
                "dependencies": []
            }],
            "entities": [{
                "name": "TestEntity",
                "description": "A test entity",
                "fields": [{
                    "name": "id",
                    "type": "string",
                    "required": True,
                    "constraints": "unique"
                }],
                "relationships": [],
                "business_rules": []
            }],
            "api_surface": ["Test API"],
            "auth_policy": "jwt_with_refresh",
            "tech_stack": {
                "frontend": "React+TS+Tailwind",
                "backend": "FastAPI",
                "database": "MongoDB"
            },
            "nonfunctional_requirements": ["Performance"],
            "environment_vars": ["TEST_VAR"],
            "deliverables_milestones": [{
                "milestone": "Test Milestone",
                "deliverables": ["Test Deliverable"],
                "acceptance_criteria": ["Test Criteria"]
            }]
        }
        
        # Test schema validation
        mock_agent = Mock()
        result = validate_project_plan_schema(mock_agent, json.dumps(valid_plan))
        assert "✅ Project plan schema validation passed" in result
        
        print("✅ Project plan schema test passed")
        return True
    except Exception as e:
        print(f"❌ Project plan schema test failed: {e}")
        return False


def test_business_requirements_extraction():
    """Test business requirements extraction"""
    try:
        mock_agent = Mock()
        user_request = "Build a todo app"
        
        result = extract_business_requirements(mock_agent, user_request)
        assert "📋 Business Requirements Analysis Template" in result
        assert "todo app" in result
        assert "React+TS+Tailwind" in result
        
        print("✅ Business requirements extraction test passed")
        return True
    except Exception as e:
        print(f"❌ Business requirements extraction test failed: {e}")
        return False


def test_entity_relationships():
    """Test entity relationships generation"""
    try:
        mock_agent = Mock()
        entities = [{"name": "User", "relationships": ["one-to-many with Task"]}]
        
        result = generate_entity_relationships(mock_agent, json.dumps(entities))
        assert "🔗 Entity Relationship Analysis" in result
        
        print("✅ Entity relationships test passed")
        return True
    except Exception as e:
        print(f"❌ Entity relationships test failed: {e}")
        return False


def test_shared_state_integration():
    """Test shared state integration"""
    try:
        mock_agent = Mock()
        mock_agent.team_session_state = {}
        mock_agent.name = "Test Agent"
        
        # Test updating project plan
        test_plan = {"project_name": "Test", "description": "Test plan"}
        result = update_project_plan(mock_agent, json.dumps(test_plan))
        
        assert "✅ Project plan updated successfully" in result
        assert mock_agent.team_session_state["project_plan"] == test_plan
        
        print("✅ Shared state integration test passed")
        return True
    except Exception as e:
        print(f"❌ Shared state integration test failed: {e}")
        return False


def test_tech_stack_enforcement():
    """Test tech stack enforcement in schema"""
    try:
        schema = PROJECT_PLAN_SCHEMA
        tech_stack_schema = schema["properties"]["tech_stack"]["properties"]
        
        # Verify only allowed values
        assert tech_stack_schema["frontend"]["enum"] == ["React+TS+Tailwind"]
        assert tech_stack_schema["backend"]["enum"] == ["FastAPI"]
        assert tech_stack_schema["database"]["enum"] == ["MongoDB"]
        
        # Verify auth policy
        auth_schema = schema["properties"]["auth_policy"]
        assert auth_schema["enum"] == ["jwt_with_refresh"]
        
        print("✅ Tech stack enforcement test passed")
        return True
    except Exception as e:
        print(f"❌ Tech stack enforcement test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Running Contract-First Planner Agent Tests")
    print("=" * 50)
    
    tests = [
        test_planner_creation,
        test_json_validation,
        test_project_plan_schema,
        test_business_requirements_extraction,
        test_entity_relationships,
        test_shared_state_integration,
        test_tech_stack_enforcement
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)