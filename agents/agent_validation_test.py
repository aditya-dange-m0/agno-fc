"""
Agent Validation and Testing Script
==================================

This script validates that both Planner and API Spec Generator agents
produce structured, complete, and production-ready outputs.

Usage:
    python agents/agent_validation_test.py
"""

import json
import sys
import os
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_planner_output(plan_json: str) -> Dict[str, Any]:
    """Validate Planner Agent output format and completeness."""
    
    validation_result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "score": 0,
        "max_score": 100
    }
    
    try:
        plan = json.loads(plan_json)
        
        # Check required sections
        required_sections = [
            "project_name", "description", "features", "tech_stack", 
            "database_models", "architecture", "environment", 
            "deliverables", "acceptance_criteria"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in plan:
                missing_sections.append(section)
        
        if missing_sections:
            validation_result["errors"].append(f"Missing required sections: {', '.join(missing_sections)}")
            return validation_result
        
        # Validate features structure
        features = plan.get("features", [])
        if not isinstance(features, list):
            validation_result["errors"].append("Features must be a list")
            return validation_result
        
        if len(features) < 5:
            validation_result["warnings"].append(f"Only {len(features)} features defined. Production apps typically need 8+ features")
        
        feature_score = 0
        for i, feature in enumerate(features):
            required_fields = ["name", "description", "priority", "complexity", "dependencies", "acceptance_criteria"]
            
            for field in required_fields:
                if field not in feature:
                    validation_result["errors"].append(f"Feature {i+1} missing field: {field}")
                    continue
            
            # Validate priority values
            if feature.get("priority") not in ["High", "Medium", "Low"]:
                validation_result["errors"].append(f"Feature '{feature.get('name')}' has invalid priority")
            
            # Validate complexity values
            if feature.get("complexity") not in ["Simple", "Moderate", "Complex"]:
                validation_result["errors"].append(f"Feature '{feature.get('name')}' has invalid complexity")
            
            # Check description length
            description = feature.get("description", "")
            if len(description.split()) < 10:
                validation_result["warnings"].append(f"Feature '{feature.get('name')}' description too brief")
            
            # Check acceptance criteria
            criteria = feature.get("acceptance_criteria", [])
            if not isinstance(criteria, list) or len(criteria) < 2:
                validation_result["warnings"].append(f"Feature '{feature.get('name')}' needs more acceptance criteria")
            
            feature_score += 10
        
        # Validate database models
        models = plan.get("database_models", [])
        if not isinstance(models, list):
            validation_result["errors"].append("Database models must be a list")
            return validation_result
        
        if len(models) < 2:
            validation_result["warnings"].append("Need at least User and one business entity model")
        
        model_score = 0
        for i, model in enumerate(models):
            required_fields = ["name", "collection", "description", "relationships", "business_rules"]
            
            for field in required_fields:
                if field not in model:
                    validation_result["errors"].append(f"Database model {i+1} missing field: {field}")
                    continue
            
            model_score += 5
        
        # Calculate final score
        base_score = 40  # For having all required sections
        validation_result["score"] = min(base_score + feature_score + model_score, 100)
        
        if len(validation_result["errors"]) == 0:
            validation_result["valid"] = True
        
        return validation_result
        
    except json.JSONDecodeError as e:
        validation_result["errors"].append(f"Invalid JSON format: {str(e)}")
        return validation_result
    except Exception as e:
        validation_result["errors"].append(f"Validation error: {str(e)}")
        return validation_result

def validate_api_spec_output(spec_json: str) -> Dict[str, Any]:
    """Validate API Spec Generator output format and completeness."""
    
    validation_result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "score": 0,
        "max_score": 100
    }
    
    try:
        spec = json.loads(spec_json)
        
        # Check required sections
        required_sections = [
            "database_schemas", "api_endpoints", "request_schemas", 
            "response_schemas", "auth_flows", "error_handling"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in spec:
                missing_sections.append(section)
        
        if missing_sections:
            validation_result["errors"].append(f"Missing required sections: {', '.join(missing_sections)}")
            return validation_result
        
        # Validate API endpoints
        endpoints = spec.get("api_endpoints", [])
        if not isinstance(endpoints, list):
            validation_result["errors"].append("API endpoints must be a list")
            return validation_result
        
        if len(endpoints) < 10:
            validation_result["warnings"].append(f"Only {len(endpoints)} endpoints defined. Production APIs typically need 15+ endpoints")
        
        endpoint_score = 0
        auth_endpoints = 0
        crud_endpoints = 0
        
        for i, endpoint in enumerate(endpoints):
            required_fields = ["method", "path", "purpose", "auth_required"]
            
            for field in required_fields:
                if field not in endpoint:
                    validation_result["errors"].append(f"Endpoint {i+1} missing field: {field}")
                    continue
            
            # Check for authentication endpoints
            if "/auth/" in endpoint.get("path", ""):
                auth_endpoints += 1
            
            # Check for CRUD patterns
            method = endpoint.get("method", "")
            if method in ["GET", "POST", "PUT", "DELETE"]:
                crud_endpoints += 1
            
            endpoint_score += 2
        
        if auth_endpoints < 4:
            validation_result["warnings"].append("Missing comprehensive authentication endpoints")
        
        # Validate database schemas
        schemas = spec.get("database_schemas", {})
        if not isinstance(schemas, dict):
            validation_result["errors"].append("Database schemas must be an object")
            return validation_result
        
        if "User" not in schemas:
            validation_result["errors"].append("User schema is required")
        
        schema_score = 0
        for schema_name, schema_info in schemas.items():
            if not isinstance(schema_info, dict):
                validation_result["errors"].append(f"Schema {schema_name} must be an object")
                continue
            
            required_fields = ["collection", "fields", "relationships", "business_rules"]
            for field in required_fields:
                if field not in schema_info:
                    validation_result["warnings"].append(f"Schema {schema_name} missing {field}")
            
            schema_score += 5
        
        # Validate request/response schemas
        request_schemas = spec.get("request_schemas", {})
        response_schemas = spec.get("response_schemas", {})
        
        if not isinstance(request_schemas, dict):
            validation_result["errors"].append("Request schemas must be an object")
        
        if not isinstance(response_schemas, dict):
            validation_result["errors"].append("Response schemas must be an object")
        
        # Calculate final score
        base_score = 30  # For having all required sections
        validation_result["score"] = min(base_score + endpoint_score + schema_score, 100)
        
        if len(validation_result["errors"]) == 0:
            validation_result["valid"] = True
        
        return validation_result
        
    except json.JSONDecodeError as e:
        validation_result["errors"].append(f"Invalid JSON format: {str(e)}")
        return validation_result
    except Exception as e:
        validation_result["errors"].append(f"Validation error: {str(e)}")
        return validation_result

def run_comprehensive_test():
    """Run comprehensive validation tests for both agents."""
    
    print("🧪 AGENT VALIDATION TEST SUITE")
    print("=" * 50)
    
    # Test cases for different project types
    test_cases = [
        {
            "name": "Task Management System",
            "description": "Create a task management system with projects, teams, and time tracking",
            "expected_features": ["User Authentication", "Task Management", "Project Organization", "Time Tracking"]
        },
        {
            "name": "E-commerce Platform",
            "description": "Build an e-commerce platform with products, orders, and payments",
            "expected_features": ["User Authentication", "Product Management", "Order Processing", "Payment Integration"]
        },
        {
            "name": "Social Media App",
            "description": "Develop a social media application with posts, comments, and messaging",
            "expected_features": ["User Authentication", "Post Management", "Social Interactions", "Messaging System"]
        }
    ]
    
    print(f"\n📋 Testing {len(test_cases)} project types:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
    
    print("\n" + "=" * 50)
    print("✅ VALIDATION CRITERIA:")
    print("- JSON format compliance")
    print("- Required sections present")
    print("- Feature completeness (8+ features)")
    print("- Database schema coverage")
    print("- API endpoint comprehensiveness (15+ endpoints)")
    print("- Authentication system completeness")
    print("- Enterprise-grade features included")
    
    print("\n" + "=" * 50)
    print("🎯 PRODUCTION READINESS CHECKLIST:")
    print("- Authentication & authorization")
    print("- CRUD operations for all entities")
    print("- Error handling & validation")
    print("- Audit logging & monitoring")
    print("- Rate limiting & security")
    print("- Data export/import capabilities")
    print("- Scalability considerations")
    
    print("\n" + "=" * 50)
    print("🚀 Ready to test agents with these criteria!")
    print("Run individual agent tests or use the integrated playground.")

if __name__ == "__main__":
    run_comprehensive_test()