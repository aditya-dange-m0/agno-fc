"""
Simple test for Contract-First Planner Agent
===========================================

Direct test without complex imports to verify the planner implementation.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test basic imports
try:
    import agents_v1.planner_agent as planner_module
    import tools_v1.shared_state_tools as tools_module
    print("✅ Direct imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing basic functionality...")
    
    # Test planner creation
    try:
        planner = planner_module.create_contract_first_planner()
        print(f"✅ Planner created: {planner.name}")
    except Exception as e:
        print(f"❌ Planner creation failed: {e}")
        return False
    
    # Test JSON validation
    try:
        validator = tools_module.JSONValidator()
        result = validator.validate_json_string('{"test": "value"}')
        assert result["valid"] == True
        print("✅ JSON validation works")
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False
    
    # Test schema validation
    try:
        # Test the JSONValidator directly first
        validator = tools_module.JSONValidator
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
        
        # Test schema validation against the schema
        schema_result = validator.validate_against_schema(valid_plan, planner_module.PROJECT_PLAN_SCHEMA)
        if schema_result["valid"]:
            print("✅ Direct schema validation works")
        else:
            print(f"❌ Direct schema validation failed: {schema_result['errors']}")
            return False
            
        print("✅ Schema validation test passed")
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    
    # Test shared state tools
    try:
        mock_agent = Mock()
        mock_agent.team_session_state = {}
        mock_agent.name = "Test Agent"
        
        test_plan = {"project_name": "Test", "description": "Test plan"}
        
        # Debug what's in the module
        print(f"Debug: update_project_plan type: {type(getattr(tools_module, 'update_project_plan'))}")
        
        # Try to call the core function directly
        core_func = getattr(tools_module, '_update_project_plan_core')
        result = core_func(mock_agent, json.dumps(test_plan))
        print(f"✅ Shared state update result: {result}")
    except Exception as e:
        print(f"❌ Shared state test failed: {e}")
        return False
    
    return True

def test_agent_tools():
    """Test that agent has all required tools"""
    print("\n🔧 Testing agent tools...")
    
    try:
        planner = planner_module.create_contract_first_planner()
        tool_names = [tool.name for tool in planner.tools]
        
        required_tools = [
            "update_project_plan",
            "get_project_plan", 
            "validate_project_plan_schema",
            "validate_agent_json_output",
            "get_shared_state_summary"
        ]
        
        for required_tool in required_tools:
            if required_tool in tool_names:
                print(f"✅ Tool found: {required_tool}")
            else:
                print(f"❌ Missing tool: {required_tool}")
                return False
        
        print(f"✅ All {len(required_tools)} required tools found")
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def test_tech_stack_enforcement():
    """Test tech stack enforcement"""
    print("\n⚙️ Testing tech stack enforcement...")
    
    try:
        schema = planner_module.PROJECT_PLAN_SCHEMA
        tech_stack_props = schema["properties"]["tech_stack"]["properties"]
        
        # Check frontend
        frontend_enum = tech_stack_props["frontend"]["enum"]
        assert frontend_enum == ["React+TS+Tailwind"]
        print("✅ Frontend tech stack enforced: React+TS+Tailwind")
        
        # Check backend
        backend_enum = tech_stack_props["backend"]["enum"]
        assert backend_enum == ["FastAPI"]
        print("✅ Backend tech stack enforced: FastAPI")
        
        # Check database
        database_enum = tech_stack_props["database"]["enum"]
        assert database_enum == ["MongoDB"]
        print("✅ Database tech stack enforced: MongoDB")
        
        # Check auth policy
        auth_enum = schema["properties"]["auth_policy"]["enum"]
        assert auth_enum == ["jwt_with_refresh"]
        print("✅ Auth policy enforced: jwt_with_refresh")
        
        return True
        
    except Exception as e:
        print(f"❌ Tech stack enforcement test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Contract-First Planner Agent - Simple Test Suite")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_agent_tools,
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
    
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Planner agent implementation is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)