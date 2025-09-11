"""
Multi-Agent Playground Integration
=================================

This file provides a unified playground that includes all agents:
- Planner Agent (high-level project planning)
- API Spec Generator Agent (detailed API contract design)
- Backend Agent (FastAPI code generation)
- Frontend Agent (React/Next.js code generation)

Usage:
    python agents/playground_integration.py

This allows testing the complete workflow:
1. Planner creates project plan
2. API Spec Generator creates detailed API contracts
3. Backend/Frontend agents implement based on specifications
"""

import os
import sys
import dotenv
from agno.playground import Playground

# Load environment variables
dotenv.load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_integrated_playground():
    """Create a playground with all available agents"""
    agents = []
    
    # Import and add Planner Agent
    try:
        from planner_agent import planner_agent
        agents.append(planner_agent)
        print("✅ Planner Agent loaded")
    except ImportError as e:
        print(f"❌ Failed to load Planner Agent: {e}")
    
    # Import and add API Spec Generator Agent
    try:
        from api_spec_agent import api_spec_agent
        agents.append(api_spec_agent)
        print("✅ API Spec Generator Agent loaded")
    except ImportError as e:
        print(f"❌ Failed to load API Spec Generator Agent: {e}")
    
    # Import and add Backend Agent
    try:
        from backend_agent import backend_agent
        agents.append(backend_agent)
        print("✅ Backend Agent loaded")
    except ImportError as e:
        print(f"❌ Failed to load Backend Agent: {e}")
    
    # Import and add Frontend Agent
    try:
        from frontend_agent import frontend_agent
        agents.append(frontend_agent)
        print("✅ Frontend Agent loaded")
    except ImportError as e:
        print(f"❌ Failed to load Frontend Agent: {e}")
    
    if not agents:
        print("❌ No agents could be loaded!")
        return None
    
    print(f"\n🚀 Creating playground with {len(agents)} agents")
    return Playground(agents=agents)

# Create the integrated playground
playground = create_integrated_playground()
app = playground.get_app() if playground else None

if __name__ == "__main__":
    if app:
        print("\n" + "="*50)
        print("🎮 MULTI-AGENT PLAYGROUND STARTED")
        print("="*50)
        print("\nWorkflow:")
        print("1. 📋 Planner Agent - Creates high-level project plan")
        print("2. 🔌 API Spec Generator - Designs detailed API contracts")
        print("3. 🐍 Backend Agent - Generates FastAPI implementation")
        print("4. ⚛️  Frontend Agent - Generates React/Next.js implementation")
        print("\nAccess the playground at: http://localhost:7777")
        print("="*50)
        
        playground.serve(app="playground_integration:app", reload=True, port=7777)
    else:
        print("❌ Failed to create playground - check agent imports")