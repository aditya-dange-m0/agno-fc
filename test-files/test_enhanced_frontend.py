#!/usr/bin/env python3
"""
Test script for the enhanced frontend agent
Demonstrates the new tools and dual generation modes
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.frontend_agent import frontend_agent

def test_project_analysis():
    """Test the project analysis tools"""
    print("🔍 Testing Frontend Project Analysis Tools")
    print("=" * 50)
    
    # Test structure analysis
    print("\n1. Analyzing project structure...")
    result = frontend_agent.run("Use analyze_project_structure to show me the current project state")
    print(result)
    
    # Test search functionality
    print("\n2. Testing search functionality...")
    result = frontend_agent.run("Use search_project_files to find any React imports in the project")
    print(result)

def test_generation_mode_detection():
    """Test generation mode detection"""
    print("\n🎯 Testing Generation Mode Detection")
    print("=" * 50)
    
    # Test first generation detection
    print("\n1. Testing first generation detection...")
    result = frontend_agent.run("Use detect_generation_mode to analyze this request: 'Create a new React dashboard for user management'")
    print(result)
    
    # Test iterative refinement detection
    print("\n2. Testing iterative refinement detection...")
    result = frontend_agent.run("Use detect_generation_mode to analyze this request: 'Add a dark mode toggle to the existing dashboard'")
    print(result)

def test_modern_frontend_optimization():
    """Test modern frontend optimization"""
    print("\n🚀 Testing Modern Frontend Optimization")
    print("=" * 50)
    
    result = frontend_agent.run("Use optimize_for_modern_frontend to analyze the current frontend for modern React/Next.js best practices")
    print(result)

def test_file_operations():
    """Test safe file operations"""
    print("\n📝 Testing Safe File Operations")
    print("=" * 50)
    
    # Test reading existing files
    print("\n1. Testing file reading...")
    result = frontend_agent.run("Use read_project_file to examine 'generated/frontend/package.json' if it exists")
    print(result)
    
    # Test backup functionality
    print("\n2. Testing backup functionality...")
    result = frontend_agent.run("Use backup_existing_files to create a backup of current files")
    print(result)

def test_iterative_workflow():
    """Test the complete iterative workflow"""
    print("\n🔄 Testing Iterative Workflow")
    print("=" * 50)
    
    # Simulate adding a new component to existing project
    request = """
    I want to add a user profile component to the existing React frontend.
    The component should:
    - Display user information (name, email, avatar)
    - Allow editing profile details
    - Include responsive design with Tailwind CSS
    
    Please follow the complete workflow:
    1. Detect generation mode
    2. Analyze current structure
    3. Search for existing user-related components
    4. Create backup if needed
    5. Add the new component functionality
    """
    
    result = frontend_agent.run(request)
    print(result)

def main():
    """Run all tests"""
    print("🧪 Enhanced Frontend Agent Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Project Analysis
        test_project_analysis()
        
        # Test 2: Generation Mode Detection
        test_generation_mode_detection()
        
        # Test 3: Modern Frontend Optimization
        test_modern_frontend_optimization()
        
        # Test 4: File Operations
        test_file_operations()
        
        # Test 5: Iterative Workflow (commented out to avoid modifying files)
        # test_iterative_workflow()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()