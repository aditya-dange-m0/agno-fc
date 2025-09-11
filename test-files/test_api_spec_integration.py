"""
Integration Test for ApiSpecGenerator Agent
=========================================

Test the complete workflow of the ApiSpecGenerator Agent.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_v1.api_spec_generator_agent import api_spec_generator_agent


def test_agent_workflow():
    """Test the complete agent workflow"""
    print("🧪 Testing ApiSpecGenerator Agent Workflow")
    print("=" * 50)
    
    # Create a mock agent with team session state
    mock_agent = Mock()
    mock_agent.name = "ApiSpecGeneratorAgent"
    mock_agent.team_session_state = {}
    
    # Sample project plan
    project_plan = {
        "project_name": "Task Manager API",
        "project_description": "A simple task management application",
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
    
    # Store project plan in mock team state
    mock_agent.team_session_state["project_plan"] = project_plan
    project_plan_json = json.dumps(project_plan)
    
    print("✅ Project plan created")
    
    # Test OpenAPI specification generation
    try:
        from agents_v1.api_spec_generator_agent import generate_openapi_specification
        
        # Get the actual function from the tool
        generate_tool = None
        for tool in api_spec_generator_agent.tools:
            if tool.name == "generate_openapi_specification":
                generate_tool = tool
                break
        
        if generate_tool:
            # Call the tool function directly
            result = generate_tool.func(mock_agent, project_plan_json)
            
            if result.startswith("❌"):
                print(f"❌ OpenAPI generation failed: {result}")
                return False
            
            # Parse and validate the result
            try:
                spec = json.loads(result)
                print("✅ OpenAPI specification generated successfully")
                
                # Basic validation
                assert spec["openapi"] == "3.1.0"
                assert spec["info"]["title"] == "Task Manager API API"
                assert "paths" in spec
                assert "components" in spec
                
                # Check entities were converted to schemas
                assert "Task" in spec["components"]["schemas"]
                assert "TaskCreate" in spec["components"]["schemas"]
                assert "User" in spec["components"]["schemas"]
                assert "UserCreate" in spec["components"]["schemas"]
                
                # Check JWT authentication
                assert "bearerAuth" in spec["components"]["securitySchemes"]
                bearer_auth = spec["components"]["securitySchemes"]["bearerAuth"]
                assert bearer_auth["type"] == "http"
                assert bearer_auth["scheme"] == "bearer"
                
                # Check authentication endpoints
                assert "/auth/register" in spec["paths"]
                assert "/auth/login" in spec["paths"]
                assert "/auth/refresh" in spec["paths"]
                
                # Check CRUD endpoints for entities
                assert "/tasks" in spec["paths"]
                assert "/tasks/{id}" in spec["paths"]
                assert "/users" in spec["paths"]
                assert "/users/{id}" in spec["paths"]
                
                print("✅ All OpenAPI validation checks passed")
                
                # Test specification validation
                validate_tool = None
                for tool in api_spec_generator_agent.tools:
                    if tool.name == "validate_openapi_specification":
                        validate_tool = tool
                        break
                
                if validate_tool:
                    validation_result = validate_tool.func(mock_agent, result)
                    
                    if validation_result.startswith("❌"):
                        print(f"❌ Specification validation failed: {validation_result}")
                        return False
                    
                    validation_report = json.loads(validation_result)
                    
                    if validation_report["status"] == "pass":
                        print("✅ OpenAPI specification validation passed")
                    else:
                        print(f"❌ Specification validation failed: {validation_report}")
                        return False
                else:
                    print("❌ Validation tool not found")
                    return False
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Generated specification is not valid JSON: {e}")
                return False
            except AssertionError as e:
                print(f"❌ Specification validation failed: {e}")
                return False
        else:
            print("❌ Generate OpenAPI specification tool not found")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def test_agent_tools():
    """Test that all required tools are present"""
    print("\n🔧 Testing Agent Tools")
    print("=" * 30)
    
    required_tools = [
        "get_project_plan",
        "generate_openapi_specification",
        "validate_openapi_specification", 
        "create_api_spec_with_validation",
        "update_api_spec",
        "get_api_spec",
        "get_api_spec_revision_history",
        "increment_api_spec_revision",
        "validate_agent_json_output",
        "get_shared_state_summary"
    ]
    
    agent_tools = [tool.name for tool in api_spec_generator_agent.tools]
    
    missing_tools = []
    for required_tool in required_tools:
        if required_tool in agent_tools:
            print(f"✅ {required_tool}")
        else:
            print(f"❌ {required_tool} - MISSING")
            missing_tools.append(required_tool)
    
    if missing_tools:
        print(f"\n❌ Missing tools: {missing_tools}")
        return False
    else:
        print("\n✅ All required tools are present")
        return True


def main():
    """Run all integration tests"""
    print("🚀 ApiSpecGenerator Agent Integration Tests")
    print("=" * 60)
    
    # Test 1: Agent tools
    tools_test = test_agent_tools()
    
    # Test 2: Agent workflow
    workflow_test = test_agent_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Agent Tools", tools_test),
        ("Agent Workflow", workflow_test)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests PASSED!")
        return True
    else:
        print("💥 Some integration tests FAILED!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)