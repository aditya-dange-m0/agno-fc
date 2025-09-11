"""
Run Test for ApiSpecGenerator Agent
=================================

Test the agent by actually running it with a query.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_agent_run():
    """Test running the agent with a simple query"""
    print("🚀 Testing ApiSpecGenerator Agent Run")
    print("=" * 50)
    
    try:
        from agents_v1.api_spec_generator_agent import api_spec_generator_agent
        
        # Create a simple project plan for testing
        project_plan = {
            "project_name": "Simple Todo API",
            "project_description": "A basic todo management API",
            "auth_policy": "jwt_with_refresh",
            "entities": [
                {
                    "name": "Todo",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "completed", "type": "boolean", "required": True}
                    ]
                }
            ]
        }
        
        # Set up the agent's team session state
        api_spec_generator_agent.team_session_state = {
            "project_plan": project_plan
        }
        
        print("✅ Project plan set in agent's team session state")
        
        # Test query to generate API specification
        query = """
        Please generate an OpenAPI 3.1 specification from the project plan in shared state.
        Use the create_api_spec_with_validation tool to create a complete API specification
        with validation report and store it in shared state.
        """
        
        print("🔄 Running agent with query...")
        
        # Run the agent
        result = api_spec_generator_agent.run(query)
        
        print("✅ Agent execution completed")
        print(f"📄 Result type: {type(result)}")
        
        # Check if API spec was created in shared state
        if hasattr(api_spec_generator_agent, 'team_session_state'):
            if "api_spec" in api_spec_generator_agent.team_session_state:
                api_spec = api_spec_generator_agent.team_session_state["api_spec"]
                print("✅ API specification created in shared state")
                
                # Basic validation
                if isinstance(api_spec, dict):
                    if "openapi_spec" in api_spec:
                        openapi_spec = api_spec["openapi_spec"]
                        print(f"   - OpenAPI version: {openapi_spec.get('openapi', 'Unknown')}")
                        print(f"   - API title: {openapi_spec.get('info', {}).get('title', 'Unknown')}")
                        
                        if "components" in openapi_spec and "schemas" in openapi_spec["components"]:
                            schemas = list(openapi_spec["components"]["schemas"].keys())
                            print(f"   - Schemas: {schemas}")
                        
                        if "paths" in openapi_spec:
                            paths = list(openapi_spec["paths"].keys())
                            print(f"   - Paths: {paths}")
                        
                        print("✅ API specification structure looks correct")
                        return True
                    else:
                        print("❌ API specification missing openapi_spec field")
                        return False
                else:
                    print("❌ API specification is not a dictionary")
                    return False
            else:
                print("❌ No API specification found in shared state")
                return False
        else:
            print("❌ No team session state found")
            return False
            
    except Exception as e:
        print(f"❌ Error during agent run test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_tools_individually():
    """Test individual agent tools"""
    print("\n🔧 Testing Individual Agent Tools")
    print("=" * 50)
    
    try:
        from agents_v1.api_spec_generator_agent import api_spec_generator_agent
        
        # Set up project plan
        project_plan = {
            "project_name": "Test API",
            "entities": [{"name": "Item", "fields": [{"name": "name", "type": "string", "required": True}]}]
        }
        
        api_spec_generator_agent.team_session_state = {"project_plan": project_plan}
        
        # Test get_project_plan tool
        get_plan_query = "Use the get_project_plan tool to retrieve the current project plan from shared state."
        
        print("🔄 Testing get_project_plan tool...")
        result = api_spec_generator_agent.run(get_plan_query)
        print("✅ get_project_plan tool executed")
        
        # Test get_shared_state_summary tool
        summary_query = "Use the get_shared_state_summary tool to show the current shared state status."
        
        print("🔄 Testing get_shared_state_summary tool...")
        result = api_spec_generator_agent.run(summary_query)
        print("✅ get_shared_state_summary tool executed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during individual tools test: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 ApiSpecGenerator Agent Run Tests")
    print("=" * 60)
    
    tests = [
        ("Individual Tools", test_agent_tools_individually),
        ("Full Agent Run", test_agent_run)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All run tests PASSED!")
        return True
    else:
        print("💥 Some run tests FAILED!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)