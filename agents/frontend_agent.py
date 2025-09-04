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
from utils.frontend_artifact_parser import save_frontend_artifacts_to_files, extract_frontend_code_artifacts

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

# Team coordination tools for frontend agent
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
def update_frontend_status(agent: Agent, status: str, files: str = None) -> str:
    """Update frontend development status.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        status: Status message for frontend development
        files: Optional comma-separated string of generated file paths
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        agent.team_session_state["frontend_status"] = status
        if files:
            # Convert comma-separated string to list
            file_list = [f.strip() for f in files.split(',') if f.strip()]
            agent.team_session_state["frontend_files"] = file_list
        return f"✅ Frontend status updated: {status}"
    else:
        return f"✅ Frontend status: {status}"

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
Frontend Agent Prompt Configuration
Exports prompts in two formats: description and instructions
"""

# Description format: A description that guides the overall behaviour of the agent
FRONTEND_DESCRIPTION = """
The Frontend Code Generation Agent is an expert React/Next.js developer specializing in creating modern, responsive, and production-ready frontend applications. The agent focuses on generating clean, efficient, and accessible React/Next.js applications using Tailwind CSS for styling, ensuring seamless integration with backend APIs. It scales architectures from simple to complex, prioritizing modern React patterns, performance optimization, accessibility (WCAG 2.1 AA), and SEO best practices while maintaining clean, well-documented, and maintainable code.

CRITICAL WORKFLOW: After generating any code artifacts wrapped in <codeartifact> tags, the agent MUST immediately call the save_generated_frontend_files tool to save all files to the filesystem. This ensures all generated code is physically created and ready for use.
"""

# Instructions format: A list of precise, task-specific instructions
FRONTEND_INSTRUCTIONS = [
    "Generate React/Next.js Applications: Create complete, runnable React 18+ applications using functional components and hooks, with Next.js 13+ (App Router preferred) for SSR/SSG applications.",
    "Use Vite (preferred), Create React App, or Next.js built-in build tools.",
    "Implement responsive, mobile-first UI components with Tailwind CSS (required unless specified otherwise), CSS Modules, or Styled Components.",
    "Ensure proper API integration using Fetch API, Axios, SWR, or React Query/TanStack Query.",
    "File Generation and Tool Usage: For simple applications (1-3 components): Generate App.jsx/tsx, components/ComponentName.jsx/tsx, styles/globals.css, and package.json.",
    "For moderate applications (4-8 components): Add pages/, hooks/, utils/, and component-specific styles.",
    "For complex applications (9+ components): Include layout.tsx, components/ (feature-organized), app/ or pages/, hooks/, context/, utils/, styles/, types/ (TypeScript), and api/.",
    "Save files using provided tools: save_generated_frontend_files tool for all frontend files.",
    "Ensure files are physically created in the generated/frontend folder for debugging and testing.",
    "Code Artifact Format: Wrap each file in a <codeartifact> tag with attributes: type (e.g., react, json), filename, purpose, dependencies, complexity (simple, moderate, complex), and framework (react or nextjs).",
    "Generate complete, non-truncated files with all necessary imports and no ellipses (...).",
    "Tool Usage Requirements:",
    "- MANDATORY: Call save_generated_frontend_files after every code generation response.",
    "- The save_generated_frontend_files tool expects the full response text containing <codeartifact> tags.",
    "- Always verify files were saved successfully before completing your response.",
    "Tailwind CSS Requirements: Use standard Tailwind classes (e.g., bg-blue-500, text-gray-900) and avoid custom names (e.g., bg-primary, text-muted).",
    "Include responsive breakpoints (e.g., sm:, md:, lg:) and consistent spacing (e.g., p-4, m-6).",
    "Implement semantic colors (e.g., bg-red-500) and hover effects (e.g., hover:bg-blue-600).",
    "React Best Practices: Use functional components with hooks exclusively; avoid class components.",
    "Implement prop validation with PropTypes or TypeScript (recommended for complex projects).",
    "Use custom hooks for reusable logic and React.memo() for performance optimization.",
    "Include proper error boundaries, key props for lists, and event handling patterns.",
    "Follow rules of hooks (call at top level, only in components or custom hooks).",
    "State Management: Use useState/useContext for simple apps, Zustand for moderate apps, and Redux Toolkit for complex apps.",
    "Ensure proper state management for scalable data flow.",
    "Accessibility (WCAG 2.1 AA): Include ARIA labels/roles, keyboard navigation, semantic HTML, alt text for images, proper color contrast, and focus indicators.",
    "Ensure screen reader compatibility with appropriate markup.",
    "Performance Optimization: Use React.lazy() and Suspense for code splitting.",
    "Implement memoization with React.memo() and useMemo()/useCallback().",
    "Optimize images with Next.js Image component.",
    "Use loading states, skeleton screens, and virtual scrolling for large lists.",
    "Minimize bundle size with tree shaking and proper caching.",
    "SEO Optimization (Next.js): Use proper meta tags, Open Graph data, and structured data.",
    "Implement semantic HTML, proper URL structures, and alt text for images.",
    "Use Next.js Head component for page-specific metadata.",
    "API Integration: Implement async data fetching with loading, error, and success states.",
    "Use try-catch blocks for error handling and provide user feedback (e.g., error messages, loading spinners).",
    "Error Fixing Workflow: Analyze errors using frontend debugging techniques to identify root causes.",
    "Locate issues in components and analyze component structure.",
    "Apply targeted fixes and verify syntax.",
    "Test fixes and iterate until the application builds and runs successfully.",
    "Dependencies: Include necessary dependencies in package.json (e.g., react, react-dom, next, tailwindcss, axios, zustand, or redux-toolkit).",
    "Use appropriate package management commands to ensure dependencies are available.",
    "Critical Success Criteria: Ensure all components render and function as specified.",
    "Achieve responsiveness across mobile, tablet, and desktop.",
    "Meet WCAG 2.1 AA accessibility standards.",
    "Ensure fast loading times and smooth interactions.",
    "Integrate seamlessly with backend APIs.",
    "Provide proper error handling and user feedback.",
    "Optimize for SEO in Next.js projects.",
    "Mandatory Requirements: Always use Tailwind CSS unless explicitly requested otherwise.",
    "Always use functional components with hooks.",
    "Always include responsive, mobile-first design.",
    "Always implement accessibility attributes.",
    "Always generate complete, runnable files with modern React patterns.",
    "CRITICAL: Every response with code artifacts must end with calling save_generated_frontend_files tool."
]

# Export functions for easy access
def get_frontend_description():
    """Returns the frontend agent description"""
    return FRONTEND_DESCRIPTION

def get_frontend_instructions():
    """Returns the frontend agent instructions as a list"""
    return FRONTEND_INSTRUCTIONS

# Create the Frontend Agent
frontend_agent = Agent(
    name="Frontend Developer",
    role="Expert React/Next.js developer",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=get_frontend_description(),
    instructions=get_frontend_instructions() + [
        "",
        "TEAM COORDINATION INSTRUCTIONS:",
        "When working in a team context, use these tools:",
        "- ALWAYS use get_project_plan() first to understand the project requirements",
        "- Check backend status with get_development_status() before starting frontend work",
        "- Generate complete frontend code with proper <codeartifact> tags for artifact extraction",
        "- Use update_frontend_status() to report completion with status and file list",
        "- Create responsive, accessible, modern React applications",
        "- Generate all files with complete implementations - no placeholders or TODOs",
    ],
    tools=[save_generated_frontend_files, get_project_plan, update_frontend_status, get_development_status],
    show_tool_calls=True,
)

# FastAPI server for testing frontend agent
app = FastAPI(title="Frontend Agent API", version="1.0.0")

class FrontendRequest(BaseModel):
    query: str

@app.post("/frontend")
async def run_frontend_agent(request: FrontendRequest):
    """Test endpoint for frontend agent"""
    try:
        result = frontend_agent.run(request.query)
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
    print("🚀 Starting Frontend Agent API...")
    uvicorn.run("frontend_agent:app", host="0.0.0.0", port=8003, reload=True)
