#!/usr/bin/env python3
"""
Test script for the enhanced orchestrator with iteration support
Demonstrates the new team coordination and dual generation modes
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_development_team

def test_team_analysis_tools():
    """Test the enhanced team analysis tools"""
    print("🔍 Testing Enhanced Team Analysis Tools")
    print("=" * 60)
    
    team = create_development_team()
    
    # Test project mode detection
    print("\n1. Testing project mode detection...")
    result = team.run("Use detect_project_mode to analyze this request: 'Create a new task management API'")
    print(result)
    
    # Test project structure analysis
    print("\n2. Testing project structure analysis...")
    result = team.run("Use analyze_team_project_structure to show the current project state")
    print(result)

def test_iterative_workflow():
    """Test the iterative refinement workflow"""
    print("\n🔄 Testing Iterative Workflow Detection")
    print("=" * 60)
    
    team = create_development_team()
    
    # Simulate iterative request
    iterative_request = """
    I want to add user profile management to the existing backend.
    
    Please:
    1. Detect if this is first generation or iterative refinement
    2. Analyze the current project structure
    3. Create a backup if needed
    4. Plan the changes needed
    """
    
    result = team.run(iterative_request)
    print(result)

def test_backup_functionality():
    """Test the backup functionality"""
    print("\n💾 Testing Backup Functionality")
    print("=" * 60)
    
    team = create_development_team()
    
    result = team.run("Use backup_team_project to create a backup of the current project")
    print(result)

def test_enhanced_coordination():
    """Test enhanced team coordination"""
    print("\n🤝 Testing Enhanced Team Coordination")
    print("=" * 60)
    
    team = create_development_team()
    
    coordination_request = """
    I need to add real-time notifications to my existing app.
    
    Please coordinate the team to:
    1. Analyze what exists currently
    2. Determine what needs to be added
    3. Plan the implementation
    4. Show me the recommended approach
    """
    
    result = team.run(coordination_request)
    print(result)

def test_mode_switching():
    """Test automatic mode switching based on project state"""
    print("\n🎯 Testing Automatic Mode Switching")
    print("=" * 60)
    
    team = create_development_team()
    
    # Test first generation detection
    print("\nTesting first generation detection:")
    result = team.run("Use detect_project_mode to analyze: 'Build a new e-commerce platform from scratch'")
    print(result)
    
    # Test iterative detection
    print("\nTesting iterative refinement detection:")
    result = team.run("Use detect_project_mode to analyze: 'Add payment processing to the existing e-commerce site'")
    print(result)

def main():
    """Run all enhanced orchestrator tests"""
    print("🧪 Enhanced Orchestrator Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Team Analysis Tools
        test_team_analysis_tools()
        
        # Test 2: Iterative Workflow
        test_iterative_workflow()
        
        # Test 3: Backup Functionality
        test_backup_functionality()
        
        # Test 4: Enhanced Coordination
        test_enhanced_coordination()
        
        # Test 5: Mode Switching
        test_mode_switching()
        
        print("\n✅ All enhanced orchestrator tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()