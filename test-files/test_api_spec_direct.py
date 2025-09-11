"""
Direct Test for ApiSpecGenerator Agent Functions
==============================================

Test the agent functions directly without the tool wrapper.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_openapi_generation():
    """Test OpenAPI specification generation directly"""
    print("🧪 Testing OpenAPI Generation")
    print("=" * 40)
    
    # Import the function directly
    from agents_v1.api_spec_generator_agent import OpenAPIValidator
    
    # Create mock agent
    mock_agent = Mock()
    mock_agent.name = "TestAgent"
    
    # Sample project plan
    project_plan = {
        "project_name": "Test API",
        "project_description": "A test API",
        "auth_policy": "jwt_with_refresh",
        "entities": [
            {
                "name": "Task",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "completed", "type": "boolean", "required": True}
                ]
            }
        ]
    }
    
    project_plan_json = json.dumps(project_plan)
    
    try:
        # Import and test the generation function
        import agents_v1.api_spec_generator_agent as api_module
        
        # Find the generate function in the module
        generate_func = None
        for name in dir(api_module):
            obj = getattr(api_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'generate_openapi_specification':
                generate_func = obj
                break
        
        if generate_func is None:
            print("❌ Could not find generate_openapi_specification function")
            return False
        
        # Test the function
        result = generate_func(mock_agent, project_plan_json)
        
        if result.startswith("❌"):
            print(f"❌ Generation failed: {result}")
            return False
        
        # Parse and validate
        try:
            spec = json.loads(result)
            
            # Basic checks
            assert spec["openapi"] == "3.1.0"
            assert spec["info"]["title"] == "Test API API"
            assert "Task" in spec["components"]["schemas"]
            assert "/tasks" in spec["paths"]
            assert "bearerAuth" in spec["components"]["securitySchemes"]
            
            print("✅ OpenAPI specification generated successfully")
            print(f"   - OpenAPI version: {spec['openapi']}")
            print(f"   - API title: {spec['info']['title']}")
            print(f"   - Schemas: {list(spec['components']['schemas'].keys())}")
            print(f"   - Paths: {list(spec['paths'].keys())}")
            
            return True
            
        except (json.JSONDecodeError, AssertionError, KeyError) as e:
            print(f"❌ Specification validation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation test: {e}")
        return False


def test_validation_utilities():
    """Test the validation utility classes"""
    print("\n🔍 Testing Validation Utilities")
    print("=" * 40)
    
    try:
        from agents_v1.api_spec_generator_agent import OpenAPIValidator
        from tools_v1.shared_state_tools import JSONValidator, RevisionManager
        
        # Test JWT security scheme
        jwt_scheme = OpenAPIValidator.create_jwt_security_scheme()
        assert "bearerAuth" in jwt_scheme
        assert jwt_scheme["bearerAuth"]["type"] == "http"
        print("✅ JWT security scheme creation works")
        
        # Test standard responses
        responses = OpenAPIValidator.create_standard_responses()
        assert "201" in responses
        assert "400" in responses
        assert "401" in responses
        assert "404" in responses
        print("✅ Standard responses creation works")
        
        # Test JSON validation
        valid_json = '{"test": "value"}'
        result = JSONValidator.validate_json_string(valid_json)
        assert result["valid"] == True
        print("✅ JSON validation works")
        
        # Test revision management
        new_version = RevisionManager.increment_version("1.0.0", "minor")
        assert new_version == "1.1.0"
        print("✅ Revision management works")
        
        # Test OpenAPI validation
        valid_spec = {
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }
        validation_result = OpenAPIValidator.validate_openapi_spec(valid_spec)
        assert validation_result["status"] == "pass"
        print("✅ OpenAPI specification validation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation utilities test failed: {e}")
        return False


def test_agent_properties():
    """Test agent properties and configuration"""
    print("\n🤖 Testing Agent Properties")
    print("=" * 40)
    
    try:
        from agents_v1.api_spec_generator_agent import api_spec_generator_agent
        
        # Check basic properties
        assert api_spec_generator_agent.name == "ApiSpecGenerator Agent"
        assert api_spec_generator_agent.role == "OpenAPI 3.1 Contract Specification Expert"
        print(f"✅ Agent name: {api_spec_generator_agent.name}")
        print(f"✅ Agent role: {api_spec_generator_agent.role}")
        
        # Check tools count
        tool_count = len(api_spec_generator_agent.tools)
        assert tool_count >= 10  # Should have at least 10 tools
        print(f"✅ Agent has {tool_count} tools")
        
        # Check model configuration
        assert api_spec_generator_agent.model is not None
        print("✅ Agent has model configured")
        
        # Check instructions
        assert len(api_spec_generator_agent.instructions) > 0
        print(f"✅ Agent has {len(api_spec_generator_agent.instructions)} instructions")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent properties test failed: {e}")
        return False


def main():
    """Run all direct tests"""
    print("🚀 ApiSpecGenerator Agent Direct Tests")
    print("=" * 60)
    
    tests = [
        ("Validation Utilities", test_validation_utilities),
        ("Agent Properties", test_agent_properties),
        ("OpenAPI Generation", test_openapi_generation)
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
        print("🎉 All direct tests PASSED!")
        return True
    else:
        print("💥 Some direct tests FAILED!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)