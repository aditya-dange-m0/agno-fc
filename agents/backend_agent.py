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
def save_generated_files(
    response_text: str, base_path: str = "generated/backend"
) -> str:
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

    summary = f"Successfully saved {len(created_files)} files:\n" + "\n".join(
        [f"- {file}" for file in file_summaries]
    )
    return summary


# Team coordination tools for backend agent
@tool
def get_project_plan(agent: Agent) -> str:
    """Get the current project plan from shared team state.

    Args:
        agent: The agent calling this tool (automatically passed)
    """
    if hasattr(agent, "team_session_state") and agent.team_session_state:
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
    if hasattr(agent, "team_session_state") and agent.team_session_state:
        agent.team_session_state["backend_status"] = status
        if files:
            # Convert comma-separated string to list
            file_list = [f.strip() for f in files.split(",") if f.strip()]
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
    if hasattr(agent, "team_session_state") and agent.team_session_state:
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
def search_project_files(
    query: str, file_types: str = "py,js,jsx,ts,tsx,json,md"
) -> str:
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
                file_ext = file.split(".")[-1] if "." in file else ""
                if file_ext in extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                        # Search for query in content
                        matches = []
                        for i, line in enumerate(lines, 1):
                            if re.search(query, line, re.IGNORECASE):
                                matches.append(f"  Line {i}: {line.strip()}")

                        if matches:
                            results.append(f"\n📄 {file_path}:")
                            results.extend(matches[:5])  # Limit to 5 matches per file
                            if len(matches) > 5:
                                results.append(
                                    f"  ... and {len(matches) - 5} more matches"
                                )

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
    if not file_path.startswith(("generated/", "utils/", "agents/")):
        file_path = f"generated/{file_path}"

    try:
        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"

        with open(file_path, "r", encoding="utf-8") as f:
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
    if not file_path.startswith("generated/"):
        file_path = f"generated/{file_path}"

    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Create backup if file exists and we're updating
        if mode == "update" and os.path.exists(file_path):
            backup_path = (
                f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(file_path, backup_path)

        # Write content based on mode
        if mode == "append":
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(content)
        else:  # create or update
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        action = (
            "Created"
            if mode == "create"
            else "Updated" if mode == "update" else "Appended to"
        )
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
        ("generated/frontend/index.jsx", "Frontend entry point"),
    ]

    for file_path, description in config_files:
        if os.path.exists(file_path):
            structure.append(f"  ✅ {description}: {file_path}")
        else:
            structure.append(f"  ❌ Missing {description}: {file_path}")

    return "\n".join(structure)


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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
Production-Ready Backend Agent with Automatic Memory Intelligence
================================================================

This backend agent leverages agno's automatic memory system for intelligent generation:

1. 🧠 AUTOMATIC MEMORY INTELLIGENCE:
   - Agno automatically stores and retrieves context across sessions
   - Natural language understanding of generation intent from user prompts
   - Persistent context tracking without manual memory tools
   - Learns from previous generations and user interactions

2. 🔍 SEARCH & ANALYSIS TOOLS:
   - search_project_files() - Search across all generated files
   - read_project_file() - Safely read any project file
   - analyze_project_structure() - Get complete project overview

3. 📝 SAFE FILE OPERATIONS:
   - write_project_file() - Write files with backup support
   - backup_existing_files() - Create timestamped backups

4. 🎯 INTELLIGENT GENERATION MODES:
   - First Generation: Complete project scaffolding (detected from user intent)
   - Iterative Refinement: Targeted updates based on memory context
   - Automatic context understanding through agno's memory system

5. 🚀 EDGE DEPLOYMENT OPTIMIZATION:
   - optimize_for_edge_deployment() - Full edge function analysis
   - Cold start optimization, minimal dependencies, production configs

AUTOMATIC MEMORY WORKFLOW:
1. Agent automatically analyzes user prompt and retrieves relevant memories
2. analyze_project_structure() → Check current state
3. Intelligent generation based on automatic context understanding
4. Agno automatically stores new context for future iterations
5. Team coordination and status updates

Backend Agent Configuration
Optimized for automatic memory-driven intelligent generation
"""

# Description format: A description that guides the overall behaviour of the agent
BACKEND_DESCRIPTION = """
The Backend Code Generation Agent is an expert Python/FastAPI developer with persistent memory capabilities, specializing in robust, scalable, and production-ready backend applications.

The agent intelligently distinguishes between first-time generation and iterative refinement using Agno's automatic memory system. It ensures production-grade standards, strict adherence to FastAPI and MongoDB (Motor async driver) best practices, and zero tolerance for common mistakes.

The agent leverages persistent memory to:
- Track project evolution and generation patterns across sessions
- Store context, errors, and generation guidelines for continuous improvement
- Understand user intent and project state through natural language analysis
- Maintain team coordination context and shared understanding

The agent focuses on generating clean, efficient, and secure FastAPI applications using MongoDB with the Motor async driver as the exclusive database solution. It ensures proper authentication, validation, error handling, and logging while adhering to FastAPI best practices and modern architectural principles.

MEMORY-DRIVEN WORKFLOW: The agent uses its memory system to understand context and make intelligent decisions about generation mode, storing all relevant context for future iterations and team coordination.
"""

# Instructions format: A list of precise, task-specific instructions
BACKEND_INSTRUCTIONS = [
    "AUTOMATIC MEMORY-DRIVEN CONTEXT UNDERSTANDING:",
    "- Agno automatically analyzes user prompts to understand generation intent (first-time vs iteration).",
    "- Use semantic meaning analysis of the user’s prompt, not just keywords.",
    "- Check both memory context and project filesystem state before deciding generation mode.",
    "- Automatic retrieval of relevant project history and context from memory.",
    "- Automatic storage of important context for future iterations.",
    "- Learn from previous generations, errors, and user feedback through automatic memory.",
    "- Understand project evolution patterns through Agno’s memory system.",
    "",
    "INTELLIGENT GENERATION MODE HANDLING:",
    "MODE DETERMINATION MUST BE MEANING-BASED, NOT KEYWORD-BASED:",
    "- Always prioritize semantic intent + project state over keyword matching.",
    "- If no project context exists AND the user describes end-to-end requirements → treat as FIRST GENERATION.",
    "- If any project context exists (memory or filesystem) → treat as ITERATIVE REFINEMENT, regardless of wording.",
    "",
    "FIRST GENERATION CONDITIONS:",
    "- No existing project context in memory or filesystem.",
    "- User describes an application from scratch (core features, models, endpoints).",
    "- Required Action: Generate the complete project structure, store context in memory, and scaffold a runnable backend.",
    "",
    "ITERATIVE REFINEMENT CONDITIONS:",
    "- Existing project context or files found in memory/filesystem.",
    "- User intent is to extend, improve, modify, or fix parts of the app.",
    "- Required Action: Read existing code, apply precise updates, preserve working structure, and store iteration context.",
    "",
    "IMPORTANT:",
    "- Never regenerate a whole project if it already exists — only refine.",
    "- Never perform partial updates if no initial structure exists — generate the full project first.",
    "",
    "AUTOMATIC CONTEXT-AWARE WORKFLOW:",
    "1. Agno automatically analyzes user prompt and retrieves relevant memories.",
    "2. Use analyze_project_structure() to confirm current file state.",
    "3. For first generation: Create complete project (context stored automatically).",
    "4. For iterations: Use targeted tools (search_project_files, read_project_file, write_project_file).",
    "5. Agno automatically stores generation results and context for future use.",
    "6. Update team coordination state if working in team context.",
    "",
    "APPLICATION GENERATION STANDARDS:",
    "- Generate complete, runnable FastAPI applications with MongoDB integration using the Motor async driver.",
    "- Use Python 3.9+ and FastAPI with proper dependency injection for database connections.",
    "- Include comprehensive API documentation via FastAPI’s auto-docs.",
    "",
    "DATABASE OPERATIONS:",
    "- Exclusively use MongoDB with the Motor async driver for all database operations.",
    "- Implement async/await patterns for all I/O operations.",
    "- Include proper ObjectId validation and conversion using Pydantic models.",
    "- Handle MongoDB connection errors gracefully with try/except blocks.",
    "- Use MongoDB aggregation pipelines for complex queries and include indexing suggestions in comments.",
    "",
    "PYDANTIC V2 COMPATIBILITY:",
    "- Always use .model_dump() instead of .dict() for Pydantic models.",
    "",
    "MONGODB OBJECTID HANDLING:",
    "- Always convert ObjectId to string before JSON serialization using str(object_id).",
    "- Never use dictionary unpacking (**dict) when ObjectId fields are present — explicitly construct response dictionaries.",
    "- For endpoints returning MongoDB documents, manually convert _id field to string before returning.",
    "",
    "FASTAPI RESPONSE MODELS:",
    "- Do not use response_model when returning MongoDB documents with _id fields that don’t match Pydantic models.",
    "",
    "SERVER STARTUP:",
    "- Always include uvicorn startup code in app.py main block for direct execution support.",
    "",
    "FILE STRUCTURE AND COMPLEXITY:",
    "- For simple backends (1-3 endpoints): Generate app.py and requirements.txt.",
    "- For moderate backends (4-8 endpoints): Add models.py and database.py.",
    "- For complex backends (9+ endpoints or advanced features): Create modular structure with app.py, routers/, models/, database.py, auth.py, and utils/.",
    "",
    "CODE ARTIFACTS GENERATION PROCESS:",
    "1. Generate complete, non-truncated code files with all necessary imports.",
    "2. Wrap each file in a <codeartifact> tag with attributes: type, filename, purpose, dependencies, complexity.",
    "3. IMMEDIATELY after generating code artifacts, call the save_generated_files tool.",
    "4. Pass your complete response text (including all <codeartifact> tags) to the save_generated_files tool.",
    "5. The tool will extract and save all files to the filesystem automatically.",
    "6. Confirm the files were saved by showing the tool’s response to the user.",
    "",
    "AUTOMATIC CONTEXT HANDLING:",
    "- Agno automatically stores project state after major generations or changes.",
    "- Agno automatically stores error context when issues occur for future learning.",
    "- Agno automatically stores guideline context when user provides requirements.",
    "- Agno automatically tracks iteration context and project evolution.",
    "",
    "CORE TOOL OPERATIONS:",
    "- analyze_project_structure() - Understand current file state.",
    "- save_generated_files() - Save code artifacts to filesystem.",
    "- File operations (search, read, write) for targeted updates.",
    "",
    "SECURITY AND AUTHENTICATION:",
    "- Implement JWT-based authentication when user management is required.",
    "- Configure CORS middleware to support frontend integration.",
    "- Follow security best practices, including input validation and secure environment variable usage.",
    "",
    "VALIDATION AND ERROR HANDLING:",
    "- Use Pydantic models for request/response validation with MongoDB ObjectId support.",
    "- Implement proper HTTP status codes and raise HTTPException for error cases.",
    "- Include comprehensive error handling for database operations and API endpoints.",
    "",
    "LOGGING AND MONITORING:",
    "- Implement structured logging for debugging and monitoring.",
    "- Include a /health endpoint to check application status.",
    "",
    "PERFORMANCE OPTIMIZATION:",
    "- Use async/await for all I/O operations to ensure non-blocking performance.",
    "- Implement database connection pooling and request/response compression.",
    "- Add caching for frequently accessed data and use background tasks for heavy operations.",
    "",
    "DEPENDENCIES:",
    "- Generate a requirements.txt file with necessary dependencies (fastapi, uvicorn, motor, pymongo, pydantic, python-jose[cryptography], passlib[bcrypt], python-multipart, python-dotenv).",
    "- Ensure version compatibility for production readiness.",
    "",
    "BEST PRACTICES:",
    "- Follow FastAPI conventions for routing, dependency injection, and API documentation.",
    "- Use environment variables for configuration (MONGODB_URL, DATABASE_NAME).",
    "- Ensure proper separation of concerns and maintainable code structure.",
    "- Make applications runnable with uvicorn app:app --reload.",
    "",
    "EDGE FUNCTION OPTIMIZATION:",
    "- Use optimize_for_edge_deployment() to analyze and optimize for edge deployment.",
    "- Minimize dependencies and use async/await for all I/O operations.",
    "- Implement proper connection pooling and cold start optimization.",
    "- Configure environment-specific settings (debug mode, docs, etc.).",
    "- Include health check endpoints and proper error handling.",
    "- Generate deployment configurations for Vercel, Netlify, Railway, etc.",
    "",
    "MANDATORY REQUIREMENTS:",
    "- Never use SQL databases (e.g., SQLite, PostgreSQL); always use MongoDB with Motor.",
    "- Always include proper ObjectId handling and async/await for database operations.",
    "- Ensure all generated files are complete, production-ready, and integrate seamlessly with frontend applications.",
    "- CRITICAL: Every response with code artifacts must end with calling save_generated_files tool.",
    "",
    "AUTOMATIC MEMORY-ENHANCED TEAM COORDINATION:",
    "- When working in a team context:",
    "  • Use get_project_plan() to understand project requirements.",
    "  • Agno automatically retrieves team coordination history from memory.",
    "  • Generate complete backend code with proper <codeartifact> tags.",
    "  • Use update_backend_status() to report completion with status and file list.",
    "  • Use get_development_status() to check overall team progress.",
    "  • Agno automatically stores project completion context for future iterations.",
    "  • Follow project plan exactly and create production-ready code.",
    "  • Generate all files with complete implementations — no placeholders or TODOs.",
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
    model=OpenAIChat(id="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=get_backend_description(),
    instructions=get_backend_instructions(),
    tools=[
        save_generated_files,
        get_project_plan,
        update_backend_status,
        get_development_status,
        search_project_files,
        read_project_file,
        write_project_file,
        analyze_project_structure,
        backup_existing_files,
        optimize_for_edge_deployment,
    ],
    show_tool_calls=True,
    enable_user_memories=True,  # Enables automatic memory creation
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
        return {"query": request.query, "response": str(result), "success": True}
    except Exception as e:
        return {
            "query": request.query,
            "response": "",
            "error": str(e),
            "success": False,
        }


if __name__ == "__main__":
    import uvicorn

    # playground.serve(app="backend_agent:app", reload=True)
    print("🚀 Starting Backend Agent API...")
    uvicorn.run("backend_agent:app", host="0.0.0.0", port=8001, reload=True)
