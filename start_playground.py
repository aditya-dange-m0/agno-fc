#!/usr/bin/env python3
"""
Quick Start Script for Enhanced Development Playground
====================================================

This script provides an easy way to start the enhanced playground
with proper error handling and environment setup.
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if the environment is properly set up."""
    
    print("🔍 Checking environment setup...")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found")
        print("   Create a .env file with your OPENAI_API_KEY")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("   Add OPENAI_API_KEY=your_key_here to your .env file")
        return False
    
    print("✅ Environment setup looks good!")
    return True

def start_playground():
    """Start the enhanced playground with proper setup."""
    
    print("🚀 Enhanced Development Playground Startup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment setup failed. Please fix the issues above.")
        return False
    
    try:
        # Import and start the playground
        from enhanced_playground import main
        
        print("\n🎮 Starting playground...")
        print("📍 Location: http://localhost:7777")
        print("🔄 Auto-reload enabled for development")
        print("\n💡 Usage Tips:")
        print("   • Use individual agents for specific tasks")
        print("   • Use the team for complete project workflows")
        print("   • Try commands like 'Create a todo app' or '/workflow Build a blog'")
        print("   • All generated code is saved to the ./generated/ directory")
        print("\n" + "=" * 50)
        
        # Start the main playground
        main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting playground: {e}")
        return False
    
    return True

def main():
    """Main entry point."""
    
    try:
        success = start_playground()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Playground stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()