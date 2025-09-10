from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
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

@tool
def search_project_files(query: str, file_types: str = "js,jsx,ts,tsx,css,json,md,py") -> str:
    """
    Search across all generated project files (frontend + backend) for specific content.
    
    Args:
        query: Search term or pattern to look for
        file_types: Comma-separated file extensions to search (default: js,jsx,ts,tsx,css,json,md,py)
    
    Returns:
        Search results with file paths and matching lines
    """
    import os
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
        ("generated/frontend/package.json", "Frontend dependencies"),
        ("generated/backend/requirements.txt", "Backend dependencies"),
        ("generated/frontend/index.jsx", "Frontend entry point"),
        ("generated/frontend/App.jsx", "Main React component"),
        ("generated/backend/app.py", "FastAPI main application"),
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
def optimize_for_modern_frontend() -> str:
    """
    Analyze and optimize the current frontend project for modern React/Next.js best practices.
    
    Returns:
        Comprehensive optimization report and recommendations
    """
    import os
    import json
    
    optimizations = []
    optimizations.append("🚀 Modern Frontend Optimization Analysis:")
    optimizations.append("=" * 50)
    
    # Check package.json for optimization opportunities
    package_json_path = "generated/frontend/package.json"
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            optimizations.append("\n📦 Dependencies Analysis:")
            
            # Check for modern React patterns
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            # React version check
            react_version = dependencies.get("react", "Not found")
            optimizations.append(f"  React Version: {react_version}")
            
            # Modern tooling recommendations
            modern_tools = {
                "vite": "Fast build tool and dev server",
                "@vitejs/plugin-react": "Vite React plugin",
                "tailwindcss": "Utility-first CSS framework",
                "@tanstack/react-query": "Data fetching and caching",
                "zustand": "Lightweight state management",
                "react-hook-form": "Performant forms library"
            }
            
            optimizations.append("\n🛠️ Modern Tooling Recommendations:")
            for tool, description in modern_tools.items():
                if tool in dependencies or tool in dev_dependencies:
                    optimizations.append(f"  ✅ {tool} - {description}")
                else:
                    optimizations.append(f"  💡 Consider adding {tool} - {description}")
            
        except Exception as e:
            optimizations.append(f"❌ Error reading package.json: {str(e)}")
    
    # Performance optimization recommendations
    optimizations.append("\n⚡ Performance Optimizations:")
    optimizations.append("```jsx")
    optimizations.append("// 1. Code Splitting with React.lazy()")
    optimizations.append("const LazyComponent = React.lazy(() => import('./Component'));")
    optimizations.append("")
    optimizations.append("// 2. Memoization for expensive calculations")
    optimizations.append("const memoizedValue = useMemo(() => expensiveCalculation(data), [data]);")
    optimizations.append("")
    optimizations.append("// 3. Component memoization")
    optimizations.append("const MemoizedComponent = React.memo(Component);")
    optimizations.append("")
    optimizations.append("// 4. Virtual scrolling for large lists")
    optimizations.append("import { FixedSizeList as List } from 'react-window';")
    optimizations.append("```")
    
    # Accessibility recommendations
    optimizations.append("\n♿ Accessibility Enhancements:")
    optimizations.append("```jsx")
    optimizations.append("// 1. Semantic HTML and ARIA labels")
    optimizations.append("<button aria-label='Close dialog' onClick={handleClose}>")
    optimizations.append("  <CloseIcon aria-hidden='true' />")
    optimizations.append("</button>")
    optimizations.append("")
    optimizations.append("// 2. Focus management")
    optimizations.append("const focusRef = useRef();")
    optimizations.append("useEffect(() => focusRef.current?.focus(), []);")
    optimizations.append("")
    optimizations.append("// 3. Color contrast and responsive design")
    optimizations.append("<div className='bg-blue-600 text-white p-4 md:p-6 lg:p-8'>")
    optimizations.append("```")
    
    # SEO and Meta optimization
    optimizations.append("\n🔍 SEO Optimization (Next.js):")
    optimizations.append("```jsx")
    optimizations.append("import Head from 'next/head';")
    optimizations.append("")
    optimizations.append("export default function Page() {")
    optimizations.append("  return (")
    optimizations.append("    <>")
    optimizations.append("      <Head>")
    optimizations.append("        <title>Page Title</title>")
    optimizations.append("        <meta name='description' content='Page description' />")
    optimizations.append("        <meta property='og:title' content='Page Title' />")
    optimizations.append("        <meta property='og:description' content='Page description' />")
    optimizations.append("      </Head>")
    optimizations.append("      {/* Page content */}")
    optimizations.append("    </>")
    optimizations.append("  );")
    optimizations.append("}")
    optimizations.append("```")
    
    # Bundle optimization
    optimizations.append("\n📦 Bundle Optimization:")
    optimizations.append("```javascript")
    optimizations.append("// vite.config.js")
    optimizations.append("export default {")
    optimizations.append("  build: {")
    optimizations.append("    rollupOptions: {")
    optimizations.append("      output: {")
    optimizations.append("        manualChunks: {")
    optimizations.append("          vendor: ['react', 'react-dom'],")
    optimizations.append("          ui: ['@headlessui/react', '@heroicons/react']")
    optimizations.append("        }")
    optimizations.append("      }")
    optimizations.append("    }")
    optimizations.append("  }")
    optimizations.append("};")
    optimizations.append("```")
    
    return "\n".join(optimizations)

"""
Enhanced Frontend Agent with Advanced Tools
==========================================

This frontend agent now supports:

1. 🔍 SEARCH & ANALYSIS TOOLS:
   - search_project_files() - Search across all generated files
   - read_project_file() - Safely read any project file
   - analyze_project_structure() - Get complete project overview

2. 📝 SAFE FILE OPERATIONS:
   - write_project_file() - Write files with backup support
   - backup_existing_files() - Create timestamped backups

3. 🎯 DUAL GENERATION MODES:
   - detect_generation_mode() - Auto-detect first gen vs iterative
   - First Generation: Complete React/Next.js project scaffolding
   - Iterative Refinement: Targeted updates without breaking existing code

4. 🚀 MODERN FRONTEND OPTIMIZATION:
   - optimize_for_modern_frontend() - React/Next.js best practices analysis
   - Performance optimization, accessibility, SEO recommendations
   - Modern tooling suggestions and bundle optimization

WORKFLOW:
1. detect_generation_mode() → Understand the request type
2. analyze_project_structure() → Check current state
3. For iterative: search_project_files() + read_project_file()
4. backup_existing_files() → Safety first for updates
5. Generate/modify code appropriately
6. optimize_for_modern_frontend() → Modern React practices

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
    "GENERATION MODE DETECTION: Always start by using detect_generation_mode() to understand if this is first generation or iterative refinement.",
    "FIRST GENERATION MODE (New Projects):",
    "- Use analyze_project_structure() to confirm no existing frontend files",
    "- Generate complete, runnable React 18+ applications using functional components and hooks",
    "- Create full project structure based on complexity (simple/moderate/complex)",
    "- Use save_generated_frontend_files() to create all files at once",
    "ITERATIVE REFINEMENT MODE (Existing Projects):",
    "- Use analyze_project_structure() to understand current project state",
    "- Use search_project_files() to find relevant existing code",
    "- Use read_project_file() to examine specific files before making changes",
    "- Use backup_existing_files() before making significant changes",
    "- Use write_project_file() with 'update' mode to modify existing files",
    "- Only modify/extend specific parts without breaking existing functionality",
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
    "WORKFLOW FOR ALL REQUESTS:",
    "1. Call detect_generation_mode() to determine first generation vs iterative refinement",
    "2. Call analyze_project_structure() to understand current state",
    "3. For iterative refinement: Use search_project_files() and read_project_file() as needed",
    "4. For significant changes: Call backup_existing_files() first",
    "5. Generate or modify code using appropriate method:",
    "   - First generation: Use <codeartifact> tags + save_generated_frontend_files()",
    "   - Iterative refinement: Use write_project_file() for targeted updates",
    "6. Always verify files were saved successfully before completing response",
    "MANDATORY TOOL CALLS:",
    "- detect_generation_mode() - ALWAYS call first",
    "- analyze_project_structure() - ALWAYS call to understand current state",
    "- save_generated_frontend_files() - Call after generating <codeartifact> tags (first generation)",
    "- write_project_file() - Use for targeted updates (iterative refinement)",
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
    "MODERN FRONTEND OPTIMIZATION:",
    "- Use optimize_for_modern_frontend() to analyze and optimize for modern React/Next.js practices",
    "- Implement code splitting, memoization, and performance optimizations",
    "- Use modern tooling like Vite, TanStack Query, Zustand for better DX",
    "- Ensure accessibility compliance and responsive design",
    "- Optimize bundle size and implement proper caching strategies",
    "- Follow React 18+ patterns and Next.js 13+ App Router when applicable",
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
    tools=[
        save_generated_frontend_files, 
        get_project_plan, 
        update_frontend_status, 
        get_development_status,
        search_project_files,
        read_project_file,
        write_project_file,
        analyze_project_structure,
        detect_generation_mode,
        backup_existing_files,
        optimize_for_modern_frontend
    ],
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
