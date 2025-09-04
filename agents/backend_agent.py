from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.playground import Playground
from fastapi import FastAPI
from pydantic import BaseModel
import dotenv
import sys
import os

# Load environment variables
dotenv.load_dotenv()

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.artifact_parser import save_artifacts_to_files, extract_code_artifacts

@tool
def save_generated_files(response_text: str, base_path: str = "generated/backend") -> str:
    """
    Extract code artifacts from response text and save them to files
    
    Args:
        response_text: The response text containing <codeartifact> tags
        base_path: Base directory to save files (default: "generated/backend")
    
    Returns:
        String summary of saved files
    """
    # Extract artifacts using the utility function
    artifacts = extract_code_artifacts(response_text)
    
    if not artifacts:
        return "No code artifacts found in response text"
    
    # Save to files using the utility function
    created_files = save_artifacts_to_files(artifacts, base_path)
    
    # Create summary
    file_summaries = []
    for i, artifact in enumerate(artifacts):
        if i < len(created_files):
            file_summaries.append(f"{artifact.filename} ({artifact.purpose})")
    
    summary = f"Successfully saved {len(created_files)} files:\n" + "\n".join([f"- {file}" for file in file_summaries])
    return summary

# Team coordination tools for backend agent
@tool
def get_project_plan(agent: Agent) -> str:
    """Get the current project plan from shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        plan = agent.team_session_state.get("project_plan", "No project plan available")
        return f"📋 Current project plan: {plan}"
    else:
        return "📋 No team session state available"

@tool
def update_backend_status(agent: Agent, status: str, files: str = None) -> str:
    """Update backend development status.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        status: Status message for backend development
        files: Optional comma-separated string of generated file paths
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        agent.team_session_state["backend_status"] = status
        if files:
            # Convert comma-separated string to list
            file_list = [f.strip() for f in files.split(',') if f.strip()]
            agent.team_session_state["backend_files"] = file_list
        return f"✅ Backend status updated: {status}"
    else:
        return f"✅ Backend status: {status}"

@tool
def get_development_status(agent: Agent) -> str:
    """Get overall development status of the project.
    
    Args:
        agent: The agent calling this tool (automatically passed)
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        backend_status = agent.team_session_state.get("backend_status", "Not started")
        frontend_status = agent.team_session_state.get("frontend_status", "Not started")
        backend_files = agent.team_session_state.get("backend_files", [])
        frontend_files = agent.team_session_state.get("frontend_files", [])
        
        status = f"""📊 Development Status:
- Backend: {backend_status} ({len(backend_files)} files)
- Frontend: {frontend_status} ({len(frontend_files)} files)
"""
        return status
    else:
        return "📊 No team session state available"

"""
Backend Agent Prompt Configuration
Exports prompts in two formats: description and instructions
"""

# Description format: A description that guides the overall behaviour of the agent
BACKEND_DESCRIPTION = """
The Backend Code Generation Agent is an expert Python/FastAPI developer specializing in creating robust, scalable, and production-ready backend applications. The agent focuses on generating clean, efficient, and secure FastAPI applications using MongoDB with the Motor async driver as the exclusive database solution. It ensures proper authentication, validation, error handling, and logging while adhering to FastAPI best practices and modern architectural principles. The agent scales solutions from simple to complex based on project requirements, prioritizing reliability, security, and maintainability for seamless frontend integration.

CRITICAL WORKFLOW: After generating any code artifacts wrapped in <codeartifact> tags, the agent MUST immediately call the save_generated_files tool to save all files to the filesystem. This ensures all generated code is physically created and ready for use.
"""

# Instructions format: A list of precise, task-specific instructions
BACKEND_INSTRUCTIONS = [
    "Generate FastAPI Applications: Create complete, runnable FastAPI applications with MongoDB integration using the Motor async driver.",
    "Use Python 3.9+ and FastAPI with proper dependency injection for database connections.",
    "Include comprehensive API documentation via FastAPI's auto-docs.",
    "Database Operations: Exclusively use MongoDB with the Motor async driver for all database operations.",
    "Implement async/await patterns for all I/O operations.",
    "Include proper ObjectId validation and conversion using Pydantic models.",
    "Handle MongoDB connection errors gracefully with try-catch blocks.",
    "Use MongoDB aggregation pipelines for complex queries and include indexing suggestions in comments.",
    "File Structure and Complexity: For simple backends (1-3 endpoints): Generate app.py (main FastAPI application with embedded MongoDB setup) and requirements.txt.",
    "For moderate backends (4-8 endpoints): Add models.py (Pydantic models with MongoDB ObjectId support) and database.py (MongoDB connection and configuration).",
    "For complex backends (9+ endpoints or advanced features): Create a modular structure with app.py, routers/ (API route modules), models/ (Pydantic models), database.py (MongoDB utilities), auth.py (authentication logic), and utils/ (helper functions).",
    "Code Artifacts Generation Process:",
    "1. Generate complete, non-truncated code files with all necessary imports.",
    "2. Wrap each file in a <codeartifact> tag with attributes: type, filename, purpose, dependencies (if applicable), and complexity.",
    "3. IMMEDIATELY after generating code artifacts, you MUST call the save_generated_files tool.",
    "4. Pass your complete response text (including all <codeartifact> tags) to the save_generated_files tool.",
    "5. The tool will extract and save all files to the filesystem automatically.",
    "6. Confirm the files were saved by showing the tool's response to the user.",
    "Tool Usage Requirements:",
    "- MANDATORY: Call save_generated_files after every code generation response.",
    "- The save_generated_files tool expects the full response text containing <codeartifact> tags.",
    "- Always verify files were saved successfully before completing your response.",
    "Security and Authentication: Implement JWT-based authentication when user management is required.",
    "Configure CORS middleware to support frontend integration, allowing appropriate origins, methods, and headers.",
    "Follow security best practices, including proper input validation and secure environment variable usage.",
    "Validation and Error Handling: Use Pydantic models for request/response validation with MongoDB ObjectId support.",
    "Implement proper HTTP status codes and raise HTTPException for error cases.",
    "Include comprehensive error handling for database operations and API endpoints.",
    "Logging and Monitoring: Implement structured logging for debugging and monitoring.",
    "Include a /health endpoint to check application status.",
    "Performance Optimization: Use async/await for all I/O operations to ensure non-blocking performance.",
    "Implement database connection pooling and request/response compression.",
    "Add caching for frequently accessed data and use background tasks for heavy operations.",
    "Dependencies: Generate a requirements.txt file with necessary dependencies, including fastapi, uvicorn, motor, pymongo, pydantic, python-jose[cryptography], passlib[bcrypt], python-multipart, and python-dotenv.",
    "Ensure version compatibility for production readiness.",
    "Best Practices: Follow FastAPI conventions for routing, dependency injection, and API documentation.",
    "Use environment variables for configuration (e.g., MONGODB_URL, DATABASE_NAME).",
    "Ensure proper separation of concerns and maintainable code structure.",
    "Make applications runnable with uvicorn app:app --reload.",
    "Mandatory Requirements: Never use SQL databases (e.g., SQLite, PostgreSQL); always use MongoDB with Motor.",
    "Always include proper ObjectId handling and async/await for database operations.",
    "Ensure all generated files are complete, production-ready, and integrate seamlessly with frontend applications.",
    "CRITICAL: Every response with code artifacts must end with calling save_generated_files tool."
]

# Export functions for easy access
def get_backend_description():
    """Returns the backend agent description"""
    return BACKEND_DESCRIPTION

def get_backend_instructions():
    """Returns the backend agent instructions as a list"""
    return BACKEND_INSTRUCTIONS


# Create the Backend Agent
backend_agent = Agent(
    name="Backend Developer",
    role="Expert Python/FastAPI developer",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=get_backend_description(),
    instructions=get_backend_instructions() + [
        "",
        "TEAM COORDINATION INSTRUCTIONS:",
        "When working in a team context, use these tools:",
        "- ALWAYS use get_project_plan() first to understand the project requirements",
        "- Generate complete backend code with proper <file> tags for artifact extraction",
        "- Use update_backend_status() to report completion with status and file list",
        "- Use get_development_status() to check what has been completed",
        "- Follow the project plan exactly and create production-ready code",
        "- Generate all files with complete implementations - no placeholders or TODOs",
    ],
    tools=[save_generated_files, get_project_plan, update_backend_status, get_development_status],
    show_tool_calls=True,
)

# playground = Playground(agents=[backend_agent])
# app = playground.get_app()

# FastAPI server for testing backend agent
app = FastAPI(title="Backend Agent API", version="1.0.0")

class BackendRequest(BaseModel):
    query: str

@app.post("/backend")
async def run_backend_agent(request: BackendRequest):
    """Test endpoint for backend agent"""
    try:
        result = backend_agent.run(request.query)
        return {
            "query": request.query,
            "response": str(result),
            "success": True
        }
    except Exception as e:
        return {
            "query": request.query,
            "response": "",
            "error": str(e),
            "success": False
        }

if __name__ == "__main__":
    import uvicorn
    # playground.serve(app="backend_agent:app", reload=True)
    print("🚀 Starting Backend Agent API...")
    uvicorn.run("backend_agent:app", host="0.0.0.0", port=8001, reload=True)