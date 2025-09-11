#!/usr/bin/env python3
"""
Test script for the enhanced backend agent
Demonstrates the new tools and dual generation modes
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.backend_agent import backend_agent

def test_project_analysis():
    """Test the project analysis tools"""
    print("🔍 Testing Project Analysis Tools")
    print("=" * 50)
    
    # Test structure analysis
    print("\n1. Analyzing project structure...")
    result = backend_agent.run("Use analyze_project_structure to show me the current project state")
    print(result)
    
    # Test search functionality
    print("\n2. Testing search functionality...")
    result = backend_agent.run("Use search_project_files to find any FastAPI imports in the project")
    print(result)

def test_generation_mode_detection():
    """Test generation mode detection"""
    print("\n🎯 Testing Generation Mode Detection")
    print("=" * 50)
    
    # Test first generation detection
    print("\n1. Testing first generation detection...")
    result = backend_agent.run("Use detect_generation_mode to analyze this request: 'Create a new FastAPI app for user management'")
    print(result)
    
    # Test iterative refinement detection
    print("\n2. Testing iterative refinement detection...")
    result = backend_agent.run("Use detect_generation_mode to analyze this request: 'Add a new endpoint to update user profiles'")
    print(result)

def test_edge_optimization():
    """Test edge deployment optimization"""
    print("\n🚀 Testing Edge Deployment Optimization")
    print("=" * 50)
    
    result = backend_agent.run("Use optimize_for_edge_deployment to analyze the current backend for edge function deployment")
    print(result)

def test_iterative_workflow():
    """Test the complete iterative workflow"""
    print("\n🔄 Testing Iterative Workflow")
    print("=" * 50)
    
    # Simulate adding a new endpoint to existing project
    request = """
    I want to add a new endpoint to the existing FastAPI backend for handling user preferences.
    The endpoint should:
    - GET /users/{user_id}/preferences - Get user preferences
    - PUT /users/{user_id}/preferences - Update user preferences
    
    Please follow the complete workflow:
    1. Detect generation mode
    2. Analyze current structure
    3. Search for existing user-related code
    4. Create backup if needed
    5. Add the new functionality
    """
    
    result = backend_agent.run(request)
    print(result)

def main():
    """Run all tests"""
    print("🧪 Enhanced Backend Agent Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Project Analysis
        test_project_analysis()
        
        # Test 2: Generation Mode Detection
        test_generation_mode_detection()
        
        # Test 3: Edge Optimization
        test_edge_optimization()
        
        # Test 4: Iterative Workflow (commented out to avoid modifying files)
        # test_iterative_workflow()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()