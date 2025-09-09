"""
Enhanced Playground App for Development Agents
==============================================

This playground includes both individual agents and the team orchestrator
for comprehensive testing and debugging.
"""

import os
from dotenv import load_dotenv
from agno.playground import Playground

# Import agents and team
from agents.planner_agent import planner_agent
from agents.backend_agent import backend_agent
from agents.frontend_agent import frontend_agent
from main import create_development_team

# Load environment variables
load_dotenv()

def create_enhanced_playground():
    """Create playground with individual agents and the development team."""
    
    print("🔧 Creating development team...")
    dev_team = create_development_team()
    
    print("✅ Setting up playground with agents and team...")
    
    # Create playground with both individual agents and team
    playground = Playground(
        agents=[planner_agent, backend_agent, frontend_agent],
        teams=[dev_team],
        name="Enhanced Development Playground",
        description="""Interactive playground for testing:
• Individual agents (Planner, Backend, Frontend)
• Full-Stack Development Team orchestrator
• Team coordination and artifact generation""",
    )
    
    return playground

def main():
    """Main function to start the enhanced playground server."""
    
    print("🚀 Starting Enhanced Development Playground")
    print("=" * 60)
    print("📋 Features:")
    print("  • Test individual agents separately")
    print("  • Test team orchestrator coordination")
    print("  • Generate and save code artifacts")
    print("  • Memory persistence across sessions")
    print("=" * 60)
    
    try:
        # Create the playground
        playground = create_enhanced_playground()
        
        # Get the FastAPI app
        app = playground.get_app()
        
        print("✅ Enhanced playground created successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser to: http://localhost:7777")
        print("💡 Try commands like:")
        print("   - 'Create a todo app'")
        print("   - '/plan Build a blog website'")
        print("   - '/workflow Create an e-commerce site'")
        print("=" * 60)
        
        # Start the server
        playground.serve(
            app="enhanced_playground:app",
            host="0.0.0.0",
            port=7777,
            reload=True
        )
        
    except Exception as e:
        print(f"❌ Error starting enhanced playground: {e}")
        raise

# Create the app instance for uvicorn
enhanced_playground_instance = create_enhanced_playground()
app = enhanced_playground_instance.get_app()

if __name__ == "__main__":
    main()