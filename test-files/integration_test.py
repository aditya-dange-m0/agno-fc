"""
Integration Test for Contract-First Planner Agent
================================================

Comprehensive integration test that validates the complete planner agent functionality
including JSON output validation, schema compliance, and shared state management.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agents_v1.planner_agent as planner_module
import tools_v1.shared_state_tools as tools_module

def create_valid_project_plan():
    """Create a valid project plan for testing"""
    return {
        "project_name": "Todo Application",
        "project_description": "A comprehensive task management application with user authentication",
        "business_goals": [
            "Enable users to manage their daily tasks efficiently",
            "Provide secure user authentication and data isolation",
            "Offer intuitive task organization and filtering capabilities"
        ],
        "features": [
            {
                "name": "User Authentication",
                "description": "Complete user registration, login, and JWT-based authentication system",
                "priority": "high",
                "complexity": "moderate",
                "dependencies": []
            },
            {
                "name": "Task Management",
                "description": "Full CRUD operations for tasks with user ownership validation",
                "priority": "high",
                "complexity": "simple",
                "dependencies": ["User Authentication"]
            },
            {
                "name": "Task Filtering and Search",
                "description": "Filter tasks by status, priority, and search by title/description",
                "priority": "medium",
                "complexity": "moderate",
                "dependencies": ["Task Management"]
            }
        ],
        "entities": [
            {
                "name": "User",
                "description": "Application user with authentication credentials and profile information",
                "fields": [
                    {"name": "id", "type": "ObjectId", "required": True, "constraints": "MongoDB ObjectId, primary key"},
                    {"name": "email", "type": "string", "required": True, "constraints": "unique, valid email format"},
                    {"name": "password_hash", "type": "string", "required": True, "constraints": "bcrypt hashed password"},
                    {"name": "first_name", "type": "string", "required": True, "constraints": "max 50 characters"},
                    {"name": "last_name", "type": "string", "required": True, "constraints": "max 50 characters"},
                    {"name": "created_at", "type": "datetime", "required": True, "constraints": "ISO 8601 format"},
                    {"name": "updated_at", "type": "datetime", "required": True, "constraints": "ISO 8601 format"}
                ],
                "relationships": ["one-to-many with Task"],
                "business_rules": [
                    "Email must be unique across all users",
                    "Password must be hashed using bcrypt",
                    "Users can only access their own tasks",
                    "User deletion should cascade to associated tasks"
                ]
            },
            {
                "name": "Task",
                "description": "Individual task item with status tracking and user ownership",
                "fields": [
                    {"name": "id", "type": "ObjectId", "required": True, "constraints": "MongoDB ObjectId, primary key"},
                    {"name": "user_id", "type": "ObjectId", "required": True, "constraints": "Foreign key to User"},
                    {"name": "title", "type": "string", "required": True, "constraints": "max 100 characters"},
                    {"name": "description", "type": "string", "required": False, "constraints": "max 500 characters"},
                    {"name": "completed", "type": "boolean", "required": True, "constraints": "default false"},
                    {"name": "priority", "type": "string", "required": True, "constraints": "enum: low, medium, high"},
                    {"name": "due_date", "type": "datetime", "required": False, "constraints": "ISO 8601 format"},
                    {"name": "created_at", "type": "datetime", "required": True, "constraints": "ISO 8601 format"},
                    {"name": "updated_at", "type": "datetime", "required": True, "constraints": "ISO 8601 format"}
                ],
                "relationships": ["many-to-one with User"],
                "business_rules": [
                    "Tasks must belong to a valid user",
                    "Users can only modify their own tasks",
                    "Completed tasks cannot have due dates in the past",
                    "Priority must be one of: low, medium, high"
                ]
            }
        ],
        "api_surface": [
            "User authentication endpoints (register, login, refresh token)",
            "User profile management endpoints",
            "Task CRUD operations with user ownership validation",
            "Task filtering and search endpoints",
            "Task status update endpoints"
        ],
        "auth_policy": "jwt_with_refresh",
        "tech_stack": {
            "frontend": "React+TS+Tailwind",
            "backend": "FastAPI",
            "database": "MongoDB"
        },
        "nonfunctional_requirements": [
            "Response times under 200ms for task operations",
            "Secure password hashing with bcrypt",
            "JWT token expiration and refresh mechanism",
            "Input validation and sanitization",
            "CORS configuration for frontend integration",
            "Error handling with appropriate HTTP status codes"
        ],
        "environment_vars": [
            "MONGO_URI",
            "JWT_SECRET_KEY",
            "JWT_ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "REFRESH_TOKEN_EXPIRE_DAYS",
            "BCRYPT_ROUNDS"
        ],
        "deliverables_milestones": [
            {
                "milestone": "Authentication System",
                "deliverables": [
                    "User model with validation",
                    "Registration endpoint with email validation",
                    "Login endpoint with JWT token generation",
                    "Token refresh endpoint",
                    "Password hashing utilities"
                ],
                "acceptance_criteria": [
                    "Users can register with valid email and password",
                    "Users can login and receive JWT access and refresh tokens",
                    "JWT tokens are properly validated on protected endpoints",
                    "Refresh tokens can be used to obtain new access tokens"
                ]
            },
            {
                "milestone": "Task Management Core",
                "deliverables": [
                    "Task model with user relationship",
                    "Task CRUD endpoints with authentication",
                    "User ownership validation middleware",
                    "Task status update functionality"
                ],
                "acceptance_criteria": [
                    "Authenticated users can create tasks",
                    "Users can view only their own tasks",
                    "Users can update and delete their own tasks",
                    "Task operations are properly validated and secured"
                ]
            },
            {
                "milestone": "Frontend Integration",
                "deliverables": [
                    "React components for authentication",
                    "Task list and task form components",
                    "API integration with error handling",
                    "Responsive design with Tailwind CSS"
                ],
                "acceptance_criteria": [
                    "Users can register and login through the UI",
                    "Task management is fully functional in the browser",
                    "Application is responsive on mobile and desktop",
                    "Error messages are displayed appropriately"
                ]
            }
        ],
        "notes_for_spec": [
            "Implement proper JWT refresh token rotation for security",
            "Add rate limiting for authentication endpoints",
            "Consider implementing task categories or tags in future iterations",
            "Ensure proper error handling and user feedback throughout the application",
            "Add comprehensive input validation on both frontend and backend"
        ]
    }

def test_complete_workflow():
    """Test the complete planner workflow"""
    print("🔄 Testing Complete Planner Workflow")
    print("=" * 50)
    
    # 1. Create planner agent
    try:
        planner = planner_module.create_contract_first_planner()
        print("✅ Planner agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create planner: {e}")
        return False
    
    # 2. Test JSON validation utilities
    try:
        validator = tools_module.JSONValidator
        
        # Test valid JSON
        valid_json = '{"test": "value"}'
        result = validator.validate_json_string(valid_json)
        assert result["valid"] == True
        
        # Test markdown detection
        markdown_json = '```json\n{"test": "value"}\n```'
        assert validator.has_markdown_or_comments(markdown_json) == True
        
        clean_json = '{"test": "value"}'
        assert validator.has_markdown_or_comments(clean_json) == False
        
        print("✅ JSON validation utilities working correctly")
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False
    
    # 3. Test project plan schema validation
    try:
        valid_plan = create_valid_project_plan()
        
        # Validate against schema
        schema_result = validator.validate_against_schema(valid_plan, planner_module.PROJECT_PLAN_SCHEMA)
        if not schema_result["valid"]:
            print(f"❌ Schema validation failed: {schema_result['errors']}")
            return False
        
        print("✅ Project plan schema validation passed")
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    
    # 4. Test shared state management
    try:
        mock_agent = Mock()
        mock_agent.team_session_state = {}
        mock_agent.name = "Integration Test Agent"
        
        # Test updating project plan
        core_func = getattr(tools_module, '_update_project_plan_core')
        result = core_func(mock_agent, json.dumps(valid_plan))
        
        if "✅ Project plan updated successfully" not in result:
            print(f"❌ Shared state update failed: {result}")
            return False
        
        # Verify the plan was stored
        if mock_agent.team_session_state.get("project_plan") != valid_plan:
            print("❌ Project plan not properly stored in shared state")
            return False
        
        print("✅ Shared state management working correctly")
    except Exception as e:
        print(f"❌ Shared state test failed: {e}")
        return False
    
    # 5. Test tech stack enforcement
    try:
        schema = planner_module.PROJECT_PLAN_SCHEMA
        tech_stack_props = schema["properties"]["tech_stack"]["properties"]
        
        # Verify all required tech stack constraints
        assert tech_stack_props["frontend"]["enum"] == ["React+TS+Tailwind"]
        assert tech_stack_props["backend"]["enum"] == ["FastAPI"]
        assert tech_stack_props["database"]["enum"] == ["MongoDB"]
        assert schema["properties"]["auth_policy"]["enum"] == ["jwt_with_refresh"]
        
        print("✅ Tech stack enforcement verified")
    except Exception as e:
        print(f"❌ Tech stack enforcement failed: {e}")
        return False
    
    # 6. Test agent tools configuration
    try:
        tool_names = [tool.name for tool in planner.tools]
        required_tools = [
            "update_project_plan",
            "get_project_plan", 
            "validate_project_plan_schema",
            "validate_agent_json_output",
            "get_shared_state_summary",
            "extract_business_requirements",
            "generate_entity_relationships"
        ]
        
        for required_tool in required_tools:
            if required_tool not in tool_names:
                print(f"❌ Missing required tool: {required_tool}")
                return False
        
        print(f"✅ All {len(required_tools)} required tools configured")
    except Exception as e:
        print(f"❌ Tool configuration test failed: {e}")
        return False
    
    print("\n🎉 Complete workflow test passed!")
    return True

def test_business_requirements_extraction():
    """Test business requirements extraction functionality"""
    print("\n📋 Testing Business Requirements Extraction")
    print("=" * 50)
    
    try:
        mock_agent = Mock()
        user_request = "Build a todo app where users can register, login, and manage their personal tasks with priorities and due dates"
        
        # Test the extraction function
        extract_func = getattr(planner_module, 'extract_business_requirements')
        result = extract_func(mock_agent, user_request)
        
        # Verify the result contains expected elements
        assert "📋 Business Requirements Analysis Template" in result
        assert user_request in result
        assert "React+TS+Tailwind" in result
        assert "FastAPI" in result
        assert "MongoDB" in result
        assert "jwt_with_refresh" in result
        
        print("✅ Business requirements extraction working correctly")
        return True
    except Exception as e:
        print(f"❌ Business requirements extraction failed: {e}")
        return False

def test_entity_relationships():
    """Test entity relationship generation"""
    print("\n🔗 Testing Entity Relationship Generation")
    print("=" * 50)
    
    try:
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
        
        # Test the relationship generation function
        relationship_func = getattr(planner_module, 'generate_entity_relationships')
        result = relationship_func(mock_agent, json.dumps(entities))
        
        # Verify the result contains expected elements
        assert "🔗 Entity Relationship Analysis" in result
        assert "entity_count" in result
        assert "relationship_patterns" in result
        
        print("✅ Entity relationship generation working correctly")
        return True
    except Exception as e:
        print(f"❌ Entity relationship generation failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Contract-First Planner Agent - Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_complete_workflow,
        test_business_requirements_extraction,
        test_entity_relationships
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
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        print("✅ Contract-First Planner Agent is fully functional and ready for use")
        return True
    else:
        print("⚠️ Some integration tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)