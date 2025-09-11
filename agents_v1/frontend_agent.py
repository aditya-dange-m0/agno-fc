"""
Contract-First Frontend Agent
============================

Enhanced Frontend Agent with contract compliance and reporting capabilities.
Integrates with shared state management and ensures strict OpenAPI specification adherence.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.tools import tool
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Add parent directory to path to import utils and tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.frontend_artifact_parser import save_frontend_artifacts_to_files, extract_frontend_code_artifacts
from tools_v1.shared_state_tools import (
    get_api_spec, get_project_plan, update_frontend_report,
    validate_agent_json_output, get_shared_state_summary
)


@tool
def save_generated_frontend_files(response_text: str, base_path: str = "generated/frontend") -> str:
    """
    Extract frontend code artifacts from response text and save them to files
    
    Args:
        response_text: The response text containing <codeartifact> tags
        base_path: Base directory to save files (default: "generated/frontend")
    
    Returns:
        String summary of saved files
    """
    # Extract artifacts using the frontend utility function
    artifacts = extract_frontend_code_artifacts(response_text)
    
    if not artifacts:
        return "No frontend code artifacts found in response text"
    
    # Save to files using the frontend utility function
    created_files = save_frontend_artifacts_to_files(artifacts, base_path)
    
    # Create summary
    file_summaries = []
    for i, artifact in enumerate(artifacts):
        if i < len(created_files):
            file_summaries.append(f"{artifact.filename} ({artifact.purpose}) - {artifact.framework}/{artifact.type}")
    
    summary = f"Successfully saved {len(created_files)} frontend files:\n" + "\n".join([f"- {file}" for file in file_summaries])
    return summary


@tool
def search_project_files(query: str, file_types: str = "js,jsx,ts,tsx,css,json,md") -> str:
    """
    Search across all generated project files (frontend + backend) for specific content.
    
    Args:
        query: Search term or pattern to look for
        file_types: Comma-separated file extensions to search (default: js,jsx,ts,tsx,css,json,md)
    
    Returns:
        Search results with file paths and matching lines
    """
    import re
    from pathlib import Path
    
    results = []
    search_dirs = ["generated/frontend", "generated/backend"]
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
    import shutil
    
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
        ("generated/frontend/package.json", "Frontend dependencies"),
        ("generated/backend/requirements.txt", "Backend dependencies"),
        ("generated/frontend/src/App.tsx", "Main React component"),
        ("generated/backend/app.py", "FastAPI main application"),
    ]
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            structure.append(f"  ✅ {description}: {file_path}")
        else:
            structure.append(f"  ❌ Missing {description}: {file_path}")
    
    return "\n".join(structure)


@tool
def validate_contract_compliance(agent: Agent, generated_code: str, api_spec_json: str) -> str:
    """
    Validate that generated React+TS+Tailwind code complies with the OpenAPI specification.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        generated_code: The generated React code to validate
        api_spec_json: The OpenAPI specification as JSON string
        
    Returns:
        Compliance validation report
    """
    try:
        # Parse API specification
        api_spec = json.loads(api_spec_json)
        openapi_spec = api_spec.get("openapi_spec", {})
        paths = openapi_spec.get("paths", {})
        
        compliance_report = {
            "status": "pass",
            "validated_api_calls": [],
            "missing_api_calls": [],
            "schema_mismatches": [],
            "auth_compliance": True,
            "component_compliance": True,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Extract endpoints from OpenAPI spec
        spec_endpoints = []
        for path, methods in paths.items():
            for method in methods.keys():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    spec_endpoints.append(f"{method.upper()} {path}")
        
        # Basic validation - check if code contains React patterns
        if "import React" not in generated_code and "from 'react'" not in generated_code:
            compliance_report["status"] = "fail"
            compliance_report["schema_mismatches"].append("Missing React imports")
        
        # Check for Tailwind CSS usage
        if "className=" not in generated_code:
            compliance_report["schema_mismatches"].append("Missing Tailwind CSS classes")
        
        # Check for JWT authentication if specified in spec
        security_schemes = openapi_spec.get("components", {}).get("securitySchemes", {})
        if "bearerAuth" in security_schemes:
            if "authorization" not in generated_code.lower() and "bearer" not in generated_code.lower():
                compliance_report["auth_compliance"] = False
                compliance_report["schema_mismatches"].append("Missing JWT authentication implementation")
        
        # Check for API call patterns
        for endpoint in spec_endpoints:
            method, path = endpoint.split(" ", 1)
            api_call_patterns = [
                f"fetch('{path}'", f'fetch("{path}"',
                f"axios.{method.lower()}('{path}'", f'axios.{method.lower()}("{path}"'
            ]
            
            if any(pattern in generated_code for pattern in api_call_patterns):
                compliance_report["validated_api_calls"].append(endpoint)
            else:
                compliance_report["missing_api_calls"].append(endpoint)
        
        # Set overall status
        if (compliance_report["missing_api_calls"] or 
            compliance_report["schema_mismatches"] or 
            not compliance_report["auth_compliance"]):
            compliance_report["status"] = "fail"
        
        return json.dumps(compliance_report, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "status": "error",
            "error": f"Invalid API specification JSON: {str(e)}",
            "validation_timestamp": datetime.now().isoformat()
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error", 
            "error": f"Validation error: {str(e)}",
            "validation_timestamp": datetime.now().isoformat()
        }, indent=2)





# Agent Description
FRONTEND_AGENT_DESCRIPTION = """
Contract-First Frontend Agent specializing in React+TypeScript+Tailwind applications that conform to OpenAPI specifications.

This agent operates in a contract-first workflow where it:
1. Reads API specifications from shared team state
2. Generates React+TS+Tailwind code using <codeartifact> tags
3. Validates contract compliance against the OpenAPI spec
4. Reports implementation status to shared team state

The agent supports both first-time generation and iterative refinement of existing projects.
"""

# Agent Instructions
FRONTEND_AGENT_INSTRUCTIONS = [
    "CONTRACT-FIRST WORKFLOW:",
    "- Always start by reading the API specification from shared team state using get_api_spec()",
    "- Generate code that conforms to the OpenAPI specification",
    "- Use get_project_plan() if additional business context is needed",
    "",
    "GENERATION MODE DETECTION:",
    "1. Use analyze_project_structure() to understand current file state.",
    "2. For first generation: Create complete project using <codeartifact> tags + save_generated_frontend_files()",
    "3. For iterations: Use targeted tools (search_project_files, read_project_file, write_project_file)",
    "",
    "WHEN TO USE save_generated_frontend_files():",
    "- For FIRST GENERATION: Use save_generated_frontend_files() after generating <codeartifact> tags",
    "- When creating complete new project structure",
    "- When generating multiple related files at once",
    "",
    "WHEN TO USE write_project_file():",
    "- For ITERATIVE REFINEMENT: Use write_project_file() for targeted updates",
    "- When modifying existing files (mode='update')",
    "- When adding content to existing files (mode='append')",
    "",
    "FILE OPERATION WORKFLOW:",
    "1. Use analyze_project_structure() to understand current state",
    "2. Use read_project_file() to examine existing files before modification",
    "3. Use search_project_files() to find relevant code patterns",
    "4. For new projects: Use save_generated_frontend_files() with <codeartifact> tags",
    "5. For updates: Use write_project_file() with appropriate mode",
    "",
    "REACT+TS+TAILWIND REQUIREMENTS:",
    "- Use functional components with hooks exclusively",
    "- Implement TypeScript interfaces that match OpenAPI schemas",
    "- Use Tailwind CSS for responsive, mobile-first design",
    "- Include proper loading states and error handling",
    "- Implement authentication state management if required by API spec",
    "",
    "CONTRACT COMPLIANCE:",
    "- Use validate_contract_compliance() to check adherence to OpenAPI specification",
    "- Ensure API endpoints match specification exactly",
    "- Verify authentication implementation matches security schemes",
    "",
    "ARTIFACT GENERATION:",
    "- Wrap generated code in <codeartifact> tags with proper attributes",
    "- Include type, filename, purpose, framework, complexity attributes",
    "- Generate package.json with necessary dependencies",
    "",
    "REPORTING:",
    "- Use update_frontend_report() to report implementation status to shared state",
    "- Track implemented components and API integrations",
    "- Report compliance status and generated files",
    "",
    "MANDATORY TOOLS:",
    "- analyze_project_structure() - Understand current file state",
    "- save_generated_frontend_files() - Save code artifacts to filesystem (first generation)",
    "- write_project_file() - Write individual files (iterative refinement)",
    "- File operations (search, read) for targeted updates",
    "",
    "CRITICAL SUCCESS CRITERIA:",
    "- All components render and function as specified",
    "- Responsive design across mobile, tablet, and desktop",
    "- Proper error handling and user feedback",
    "- Integration with backend APIs as per OpenAPI specification",
    "- CRITICAL: Every response with code artifacts must end with calling save_generated_frontend_files tool (first generation) or appropriate write_project_file calls (iterations)"
]

# Create the Contract-First Frontend Agent
frontend_agent = Agent(
    name="Contract-First Frontend Agent",
    role="React+TS+Tailwind Contract Compliance Developer",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=FRONTEND_AGENT_DESCRIPTION,
    instructions=FRONTEND_AGENT_INSTRUCTIONS,
    tools=[
        # Shared state tools (imported from tools_v1)
        get_api_spec,
        get_project_plan,
        update_frontend_report,
        validate_agent_json_output,
        get_shared_state_summary,
        # File operation tools
        save_generated_frontend_files,
        search_project_files,
        read_project_file,
        write_project_file,
        analyze_project_structure,
        # Contract compliance tools
        validate_contract_compliance
    ],
    show_tool_calls=True,
    enable_user_memories=True
)

playground = Playground(agents=[frontend_agent])
app = playground.get_app()

if __name__ == "__main__":
    playground.serve(app="frontend_agent:app", reload=True)