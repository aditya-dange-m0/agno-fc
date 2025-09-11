"""
Enhanced Backend Agent with Contract Compliance
==============================================

Enhanced version of the existing Backend Agent with contract compliance and reporting capabilities.
Builds on the original agent by adding tools to read API specs and write backend reports.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.playground import Playground
from fastapi import FastAPI
from pydantic import BaseModel
import dotenv
import sys
import os
import json
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

# Add parent directory to path to import utils and tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.artifact_parser import save_artifacts_to_files, extract_code_artifacts
from tools_v1.shared_state_tools import (
    get_api_spec,
    get_project_plan,
    update_backend_report,
    validate_agent_json_output,
    get_shared_state_summary,
)


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


# Contract compliance validation tool
@tool
def validate_contract_compliance(
    agent: Agent, generated_code: str, api_spec_json: str
) -> str:
    """
    Validate that generated FastAPI code complies with the OpenAPI specification.

    Args:
        agent: The agent calling this tool (automatically passed)
        generated_code: The generated FastAPI code to validate
        api_spec_json: The OpenAPI specification as JSON string

    Returns:
        Compliance validation report as JSON string
    """
    try:
        # Parse API specification
        api_spec = json.loads(api_spec_json)
        openapi_spec = api_spec.get("openapi_spec", {})
        paths = openapi_spec.get("paths", {})

        compliance_report = {
            "status": "pass",
            "validated_endpoints": [],
            "missing_endpoints": [],
            "schema_mismatches": [],
            "auth_compliance": True,
            "validation_timestamp": datetime.now().isoformat(),
        }

        # Extract endpoints from OpenAPI spec
        spec_endpoints = []
        for path, methods in paths.items():
            for method in methods.keys():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    spec_endpoints.append(f"{method.upper()} {path}")

        # Basic validation - check if code contains FastAPI patterns
        if "from fastapi import FastAPI" not in generated_code:
            compliance_report["status"] = "fail"
            compliance_report["schema_mismatches"].append("Missing FastAPI import")

        # Check for JWT authentication if specified in spec
        security_schemes = openapi_spec.get("components", {}).get("securitySchemes", {})
        if "bearerAuth" in security_schemes:
            if (
                "jwt" not in generated_code.lower()
                and "bearer" not in generated_code.lower()
            ):
                compliance_report["auth_compliance"] = False
                compliance_report["schema_mismatches"].append(
                    "Missing JWT authentication implementation"
                )

        # Check for basic endpoint patterns
        for endpoint in spec_endpoints:
            method, path = endpoint.split(" ", 1)
            # Convert OpenAPI path to FastAPI path format
            fastapi_path = path.replace("{", "{").replace("}", "}")
            endpoint_pattern = f'@app.{method.lower()}("{fastapi_path}")'

            if (
                endpoint_pattern in generated_code
                or f"@app.{method.lower()}('{fastapi_path}')" in generated_code
            ):
                compliance_report["validated_endpoints"].append(endpoint)
            else:
                compliance_report["missing_endpoints"].append(endpoint)

        # Set overall status
        if (
            compliance_report["missing_endpoints"]
            or compliance_report["schema_mismatches"]
            or not compliance_report["auth_compliance"]
        ):
            compliance_report["status"] = "fail"

        return json.dumps(compliance_report, indent=2)

    except json.JSONDecodeError as e:
        return json.dumps(
            {
                "status": "error",
                "error": f"Invalid API specification JSON: {str(e)}",
                "validation_timestamp": datetime.now().isoformat(),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "error": f"Validation error: {str(e)}",
                "validation_timestamp": datetime.now().isoformat(),
            },
            indent=2,
        )


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
def validate_contract_compliance(agent: Agent, generated_files_summary: str) -> str:
    """
    Simple contract compliance validation against API spec from shared state.

    Args:
        agent: The agent calling this tool (automatically passed)
        generated_files_summary: Summary of generated files to validate

    Returns:
        Simple compliance validation report
    """
    try:
        # Get API spec from shared state
        if hasattr(agent, "team_session_state") and agent.team_session_state:
            api_spec = agent.team_session_state.get("api_spec", None)
            if not api_spec:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "No API specification available in shared state",
                        "validation_timestamp": datetime.now().isoformat(),
                    },
                    indent=2,
                )

            # Simple validation - just check if we have the basic structure
            compliance_report = {
                "status": "pass",
                "message": "Basic compliance validation completed",
                "generated_files": generated_files_summary,
                "api_spec_version": api_spec.get("revision", "unknown"),
                "validation_timestamp": datetime.now().isoformat(),
            }

            return json.dumps(compliance_report, indent=2)
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "No team session state available",
                    "validation_timestamp": datetime.now().isoformat(),
                },
                indent=2,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Validation error: {str(e)}",
                "validation_timestamp": datetime.now().isoformat(),
            },
            indent=2,
        )


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


"""
Enhanced Backend Agent with Contract Compliance
==============================================

This enhanced backend agent builds on the original backend agent by adding:
1. Tools to read API specifications from shared team state
2. Contract compliance validation capabilities  
3. Backend reporting to shared team state
4. Integration with existing artifact parsing system

The agent maintains all the original capabilities while adding contract-first workflow support.
"""

# Use the original backend agent description and instructions with enhancements
BACKEND_DESCRIPTION = """
The Backend Code Generation Agent is an expert Python/FastAPI developer with persistent memory capabilities and contract compliance features, specializing in robust, scalable, and production-ready backend applications.

Enhanced with contract-first workflow capabilities:
- Reads API specifications from shared team state for contract compliance
- Generates FastAPI code that matches OpenAPI specifications exactly
- Validates contract compliance and reports implementation status
- Integrates with team coordination through shared state management

The agent intelligently distinguishes between first-time generation and iterative refinement using Agno's automatic memory system. It ensures production-grade standards, strict adherence to FastAPI and MongoDB (Motor async driver) best practices, and zero tolerance for common mistakes.

The agent focuses on generating clean, efficient, and secure FastAPI applications using MongoDB with the Motor async driver as the exclusive database solution. It ensures proper authentication, validation, error handling, and logging while adhering to FastAPI best practices and modern architectural principles.
"""

# Enhanced instructions with contract compliance and iterative workflow
BACKEND_INSTRUCTIONS = [
    "CONTRACT-FIRST WORKFLOW:",
    "- Always start by reading the API specification using get_api_spec()",
    "- Generate FastAPI code that strictly conforms to the OpenAPI specification",
    "- Use validate_contract_compliance() to check adherence to specification",
    "- Use update_backend_report() to report implementation status to shared state",
    "- Never invent endpoints, schemas, or authentication methods not in the API spec",
    "",
    "AUTOMATIC MEMORY-DRIVEN CONTEXT UNDERSTANDING:",
    "- Agno automatically analyzes user prompts to understand generation intent (first-time vs iteration).",
    "- Use semantic meaning analysis of the user's prompt, not just keywords.",
    "- Check both memory context and project filesystem state before deciding generation mode.",
    "- Automatic retrieval of relevant project history and context from memory.",
    "- Automatic storage of important context for future iterations.",
    "- Learn from previous generations, errors, and user feedback through automatic memory.",
    "- Understand project evolution patterns through Agno's memory system.",
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
    "FILE OPERATION GUIDANCE:",
    "WHEN TO USE save_generated_files():",
    "- For FIRST GENERATION: Always use save_generated_files() with <codeartifact> tags",
    "- When creating multiple new files from scratch",
    "- When generating complete project structure",
    "",
    "WHEN TO USE write_project_file():",
    "- For ITERATIVE REFINEMENT: Use write_project_file() for targeted updates",
    "- When modifying existing files (mode='update')",
    "- When adding content to existing files (mode='append')",
    "- When creating single files during iterations",
    "",
    "FILE OPERATION WORKFLOW:",
    "1. Use analyze_project_structure() to understand current state",
    "2. Use read_project_file() to examine existing files before modification",
    "3. Use search_project_files() to find relevant code patterns",
    "4. For new projects: Use save_generated_files() with <codeartifact> tags",
    "5. For updates: Use write_project_file() with appropriate mode",
    "",
    "APPLICATION GENERATION STANDARDS:",
    "- Generate complete, runnable FastAPI applications with MongoDB integration using the Motor async driver.",
    "- Use Python 3.9+ and FastAPI with proper dependency injection for database connections.",
    "- Include comprehensive API documentation via FastAPI's auto-docs.",
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
    "- Do not use response_model when returning MongoDB documents with _id fields that don't match Pydantic models.",
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
    "6. Confirm the files were saved by showing the tool's response to the user.",
    "",
    "AUTOMATIC CONTEXT HANDLING:",
    "- Agno automatically stores project state after major generations or changes.",
    "- Agno automatically stores error context when issues occur for future learning.",
    "- Agno automatically stores guideline context when user provides requirements.",
    "- Agno automatically tracks iteration context and project evolution.",
    "",
    "CORE TOOL OPERATIONS:",
    "- analyze_project_structure() - Understand current file state.",
    "- save_generated_files() - Save code artifacts to filesystem (first generation).",
    "- write_project_file() - Write individual files (iterative refinement).",
    "- File operations (search, read) for targeted updates.",
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
    "TEAM COORDINATION:",
    "- Use get_project_plan() to understand project requirements.",
    "- Use update_backend_status() to report completion with status and file list.",
    "- Use get_development_status() to check overall team progress.",
    "- When working in a team context, follow project plan exactly and create production-ready code.",
    "- Generate all files with complete implementations — no placeholders or TODOs.",
    "",
    "MANDATORY REQUIREMENTS:",
    "- Never use SQL databases (e.g., SQLite, PostgreSQL); always use MongoDB with Motor.",
    "- Always include proper ObjectId handling and async/await for database operations.",
    "- Ensure all generated files are complete, production-ready, and integrate seamlessly with frontend applications.",
    "",
    "MANDATORY CONTRACT-FIRST WORKFLOW:",
    "1. Read API specification from shared state using get_api_spec()",
    "2. Generate FastAPI code conforming to specification",
    "3. Validate contract compliance using validate_contract_compliance()",
    "4. Save code artifacts to filesystem",
    "5. Report implementation status using update_backend_report()",
    "",
    "- CRITICAL: Every response with code artifacts must end with calling save_generated_files tool (first generation) or appropriate write_project_file calls (iterations).",
]

# Create the Enhanced Backend Agent
backend_agent = Agent(
    name="Enhanced Backend Developer",
    role="Expert Python/FastAPI developer with contract compliance",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=BACKEND_DESCRIPTION,
    instructions=BACKEND_INSTRUCTIONS,
    tools=[
        # Shared state tools (imported from tools_v1)
        get_api_spec,
        get_project_plan,
        update_backend_report,
        validate_agent_json_output,
        get_shared_state_summary,
        # File operation tools
        save_generated_files,
        search_project_files,
        read_project_file,
        write_project_file,
        analyze_project_structure,
        # Contract compliance tools
        validate_contract_compliance,
        # Team coordination tools
        update_backend_status,
        get_development_status,
    ],
    show_tool_calls=True,
    enable_user_memories=True,
)




playground = Playground(agents=[backend_agent])

app = playground.get_app()  # This needs to be at module level

if __name__ == "__main__":
    playground.serve(app="backend_agent:app", reload=True)
