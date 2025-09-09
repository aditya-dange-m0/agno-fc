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

@tool
def search_project_files(query: str, file_types: str = "py,js,jsx,ts,tsx,json,md") -> str:
    """
    Search across all generated project files (frontend + backend) for specific content.
    
    Args:
        query: Search term or pattern to look for
        file_types: Comma-separated file extensions to search (default: py,js,jsx,ts,tsx,json,md)
    
    Returns:
        Search results with file paths and matching lines
    """
    import os
    import re
    from pathlib import Path
    
    results = []
    search_dirs = ["generated/backend", "generated/frontend"]
    extensions = [ext.strip() for ext in file_types.split(",")]
    
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
            
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                file_ext = file.split('.')[-1] if '.' in file else ''
                if file_ext in extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                        # Search for query in content
                        matches = []
                        for i, line in enumerate(lines, 1):
                            if re.search(query, line, re.IGNORECASE):
                                matches.append(f"  Line {i}: {line.strip()}")
                        
                        if matches:
                            results.append(f"\n📄 {file_path}:")
                            results.extend(matches[:5])  # Limit to 5 matches per file
                            if len(matches) > 5:
                                results.append(f"  ... and {len(matches) - 5} more matches")
                                
                    except Exception as e:
                        results.append(f"❌ Error reading {file_path}: {str(e)}")
    
    if not results:
        return f"🔍 No matches found for '{query}' in project files"
    
    return f"🔍 Search results for '{query}':\n" + "\n".join(results)

@tool
def read_project_file(file_path: str) -> str:
    """
    Safely read a file from the project (generated or source files).
    
    Args:
        file_path: Path to the file (relative to project root or absolute)
    
    Returns:
        File content or error message
    """
    import os
    
    # Normalize path and ensure it's safe
    if not file_path.startswith(('generated/', 'utils/', 'agents/')):
        file_path = f"generated/{file_path}"
    
    try:
        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"📄 Content of {file_path}:\n\n{content}"
        
    except Exception as e:
        return f"❌ Error reading {file_path}: {str(e)}"

@tool
def write_project_file(file_path: str, content: str, mode: str = "create") -> str:
    """
    Safely write content to a project file with backup support.
    
    Args:
        file_path: Path to the file (relative to generated/ directory)
        content: Content to write
        mode: 'create' (new file), 'update' (replace existing), 'append' (add to end)
    
    Returns:
        Success message or error
    """
    import os
    import shutil
    from datetime import datetime
    
    # Ensure file is in generated directory for safety
    if not file_path.startswith('generated/'):
        file_path = f"generated/{file_path}"
    
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create backup if file exists and we're updating
        if mode == "update" and os.path.exists(file_path):
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
        
        # Write content based on mode
        if mode == "append":
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
        else:  # create or update
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        action = "Created" if mode == "create" else "Updated" if mode == "update" else "Appended to"
        return f"✅ {action} {file_path} successfully"
        
    except Exception as e:
        return f"❌ Error writing {file_path}: {str(e)}"

@tool
def analyze_project_structure() -> str:
    """
    Analyze the current project structure and identify existing files.
    
    Returns:
        Detailed project structure analysis
    """
    import os
    from pathlib import Path
    
    structure = []
    structure.append("📁 Current Project Structure:")
    structure.append("=" * 40)
    
    # Analyze generated directory
    if os.path.exists("generated"):
        structure.append("\n🏗️ Generated Files:")
        
        for root, dirs, files in os.walk("generated"):
            level = root.replace("generated", "").count(os.sep)
            indent = "  " * level
            structure.append(f"{indent}📂 {os.path.basename(root)}/")
            
            subindent = "  " * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    structure.append(f"{subindent}📄 {file} ({size} bytes)")
                except:
                    structure.append(f"{subindent}📄 {file}")
    
    # Check for key configuration files
    structure.append("\n🔧 Configuration Status:")
    config_files = [
        ("generated/backend/requirements.txt", "Backend dependencies"),
        ("generated/frontend/package.json", "Frontend dependencies"),
        ("generated/backend/app.py", "FastAPI main application"),
        ("generated/backend/models.py", "Database models"),
        ("generated/frontend/index.jsx", "Frontend entry point")
    ]
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            structure.append(f"  ✅ {description}: {file_path}")
        else:
            structure.append(f"  ❌ Missing {description}: {file_path}")
    
    return "\n".join(structure)

@tool
def detect_generation_mode(user_query: str) -> str:
    """
    Detect whether the user wants first generation or iterative refinement.
    
    Args:
        user_query: The user's request/query
    
    Returns:
        Analysis of generation mode and recommendations
    """
    import os
    
    # Check if generated files exist
    has_backend = os.path.exists("generated/backend") and len(os.listdir("generated/backend")) > 0
    has_frontend = os.path.exists("generated/frontend") and len(os.listdir("generated/frontend")) > 0
    
    # Keywords that suggest first generation
    first_gen_keywords = [
        "create", "build", "generate", "scaffold", "new project", 
        "from scratch", "start", "initialize", "setup"
    ]
    
    # Keywords that suggest iterative refinement
    iterative_keywords = [
        "update", "modify", "change", "add", "extend", "improve", 
        "fix", "refactor", "enhance", "adjust", "edit"
    ]
    
    query_lower = user_query.lower()
    
    # Count keyword matches
    first_gen_score = sum(1 for keyword in first_gen_keywords if keyword in query_lower)
    iterative_score = sum(1 for keyword in iterative_keywords if keyword in query_lower)
    
    # Determine mode
    if has_backend or has_frontend:
        if iterative_score > first_gen_score:
            mode = "iterative_refinement"
            recommendation = "🔄 Iterative Refinement Mode - Update existing project files"
        else:
            mode = "first_generation"
            recommendation = "⚠️ First Generation Mode - Will overwrite existing files"
    else:
        mode = "first_generation"
        recommendation = "🆕 First Generation Mode - Create new project structure"
    
    analysis = f"""🎯 Generation Mode Analysis:
- Mode Detected: {mode}
- Existing Backend: {'✅ Yes' if has_backend else '❌ No'}
- Existing Frontend: {'✅ Yes' if has_frontend else '❌ No'}
- First Gen Keywords: {first_gen_score}
- Iterative Keywords: {iterative_score}

💡 Recommendation: {recommendation}

📋 Query Analysis: "{user_query[:100]}{'...' if len(user_query) > 100 else ''}"
"""
    
    return analysis

@tool
def backup_existing_files() -> str:
    """
    Create backups of existing generated files before making changes.
    
    Returns:
        Backup status and file list
    """
    import os
    import shutil
    from datetime import datetime
    
    if not os.path.exists("generated"):
        return "📁 No generated files to backup"
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"generated_backup_{timestamp}"
    
    try:
        shutil.copytree("generated", backup_dir)
        
        # Count backed up files
        file_count = 0
        for root, dirs, files in os.walk(backup_dir):
            file_count += len(files)
        
        return f"✅ Backup created: {backup_dir} ({file_count} files backed up)"
        
    except Exception as e:
        return f"❌ Backup failed: {str(e)}"

@tool
def optimize_for_edge_deployment() -> str:
    """
    Analyze and optimize the current backend project for edge function deployment.
    
    Returns:
        Comprehensive optimization report and recommendations
    """
    # Import the edge optimizer
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.edge_function_optimizer import optimize_project_for_edge
    
    return optimize_project_for_edge("generated/backend")

"""
Enhanced Backend Agent with Advanced Tools
==========================================

This backend agent now supports:

1. 🔍 SEARCH & ANALYSIS TOOLS:
   - search_project_files() - Search across all generated files
   - read_project_file() - Safely read any project file
   - analyze_project_structure() - Get complete project overview

2. 📝 SAFE FILE OPERATIONS:
   - write_project_file() - Write files with backup support
   - backup_existing_files() - Create timestamped backups

3. 🎯 DUAL GENERATION MODES:
   - detect_generation_mode() - Auto-detect first gen vs iterative
   - First Generation: Complete project scaffolding
   - Iterative Refinement: Targeted updates without breaking existing code

4. 🚀 EDGE DEPLOYMENT OPTIMIZATION:
   - optimize_for_edge_deployment() - Full edge function analysis
   - Cold start optimization, minimal dependencies, production configs

WORKFLOW:
1. detect_generation_mode() → Understand the request type
2. analyze_project_structure() → Check current state
3. For iterative: search_project_files() + read_project_file()
4. backup_existing_files() → Safety first for updates
5. Generate/modify code appropriately
6. optimize_for_edge_deployment() → Production readiness

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
    "GENERATION MODE DETECTION: Always start by using detect_generation_mode() to understand if this is first generation or iterative refinement.",
    "FIRST GENERATION MODE (New Projects):",
    "- Use analyze_project_structure() to confirm no existing files",
    "- Generate complete, runnable FastAPI applications with MongoDB integration using the Motor async driver",
    "- Create full project structure based on complexity (simple/moderate/complex)",
    "- Use save_generated_files() to create all files at once",
    "ITERATIVE REFINEMENT MODE (Existing Projects):",
    "- Use analyze_project_structure() to understand current project state",
    "- Use search_project_files() to find relevant existing code",
    "- Use read_project_file() to examine specific files before making changes",
    "- Use backup_existing_files() before making significant changes",
    "- Use write_project_file() with 'update' mode to modify existing files",
    "- Only modify/extend specific parts without breaking existing functionality",
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
    "WORKFLOW FOR ALL REQUESTS:",
    "1. Call detect_generation_mode() to determine first generation vs iterative refinement",
    "2. Call analyze_project_structure() to understand current state",
    "3. For iterative refinement: Use search_project_files() and read_project_file() as needed",
    "4. For significant changes: Call backup_existing_files() first",
    "5. Generate or modify code using appropriate method:",
    "   - First generation: Use <codeartifact> tags + save_generated_files()",
    "   - Iterative refinement: Use write_project_file() for targeted updates",
    "6. Always verify files were saved successfully before completing response",
    "MANDATORY TOOL CALLS:",
    "- detect_generation_mode() - ALWAYS call first",
    "- analyze_project_structure() - ALWAYS call to understand current state",
    "- save_generated_files() - Call after generating <codeartifact> tags (first generation)",
    "- write_project_file() - Use for targeted updates (iterative refinement)",
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
    "EDGE FUNCTION OPTIMIZATION:",
    "- Use optimize_for_edge_deployment() to analyze and optimize for edge deployment",
    "- Minimize dependencies and use async/await for all I/O operations",
    "- Implement proper connection pooling and cold start optimization",
    "- Configure environment-specific settings (debug mode, docs, etc.)",
    "- Include health check endpoints and proper error handling",
    "- Generate deployment configurations for Vercel, Netlify, Railway, etc.",
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
    tools=[
        save_generated_files, 
        get_project_plan, 
        update_backend_status, 
        get_development_status,
        search_project_files,
        read_project_file,
        write_project_file,
        analyze_project_structure,
        detect_generation_mode,
        backup_existing_files,
        optimize_for_edge_deployment
    ],
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