#!/usr/bin/env python3
"""
Test script to verify playground setup and dependencies
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🔍 Testing Environment Setup")
    print("=" * 40)
    
    # Test .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✅ OPENAI_API_KEY configured")
        else:
            print("❌ OPENAI_API_KEY not found in .env")
            return False
    else:
        print("❌ .env file not found")
        return False
    
    return True

def test_imports():
    """Test required imports"""
    print("\n🔍 Testing Required Imports")
    print("=" * 40)
    
    try:
        import agno
        print("✅ agno framework imported")
    except ImportError:
        print("❌ agno framework not found - install with: pip install agno")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError:
        print("❌ FastAPI not found - install with: pip install fastapi")
        return False
    
    try:
        import uvicorn
        print("✅ uvicorn imported")
    except ImportError:
        print("❌ uvicorn not found - install with: pip install uvicorn")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported")
    except ImportError:
        print("❌ python-dotenv not found - install with: pip install python-dotenv")
        return False
    
    return True

def test_agent_imports():
    """Test agent imports"""
    print("\n🔍 Testing Agent Imports")
    print("=" * 40)
    
    try:
        from agents.planner_agent import planner_agent
        print("✅ Planner agent imported")
    except ImportError as e:
        print(f"❌ Planner agent import failed: {e}")
        return False
    
    try:
        from agents.backend_agent import backend_agent
        print("✅ Backend agent imported")
    except ImportError as e:
        print(f"❌ Backend agent import failed: {e}")
        return False
    
    try:
        from agents.frontend_agent import frontend_agent
        print("✅ Frontend agent imported")
    except ImportError as e:
        print(f"❌ Frontend agent import failed: {e}")
        return False
    
    return True

def test_team_import():
    """Test team orchestrator import"""
    print("\n🔍 Testing Team Orchestrator Import")
    print("=" * 40)
    
    try:
        from main import create_development_team
        print("✅ Team orchestrator imported")
        
        # Try creating team (without running)
        team = create_development_team()
        print("✅ Development team created successfully")
        return True
    except ImportError as e:
        print(f"❌ Team orchestrator import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Team creation failed: {e}")
        return False

def test_playground_creation():
    """Test playground creation"""
    print("\n🔍 Testing Playground Creation")
    print("=" * 40)
    
    try:
        from enhanced_playground import create_enhanced_playground
        print("✅ Playground module imported")
        
        # Try creating playground (without starting server)
        playground = create_enhanced_playground()
        print("✅ Enhanced playground created successfully")
        
        # Test app creation
        app = playground.get_app()
        print("✅ FastAPI app created successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Playground import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Playground creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Playground Setup Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Agents", test_agent_imports),
        ("Team", test_team_import),
        ("Playground", test_playground_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Playground is ready to run.")
        print("💡 Start with: python start_playground.py")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        print("💡 Check requirements.txt and install missing dependencies")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)