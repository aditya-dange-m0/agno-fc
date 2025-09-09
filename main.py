"""
Team Orchestrator for Code Generation Agents
============================================

This module creates a team of agents that work together to plan and generate
complete full-stack applications. The team consists of:

1. Planner Agent - Creates structured project plans
2. Backend Agent - Generates FastAPI backend code
3. Frontend Agent - Generates React/Next.js frontend code

The team uses shared state to coordinate the development process from
planning to implementation.
"""

import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools import tool

# Memory imports for persistent conversational history
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

# Import agent modules - import the actual agent instances
try:
    from agents.planner_agent import planner_agent
    from agents.backend_agent import backend_agent  
    from agents.frontend_agent import frontend_agent
except ImportError as e:
    print(f"Error importing agents: {e}")
    print("Make sure all agent files exist and are properly configured")
    exit(1)

# Import utilities
from utils.artifact_parser import extract_code_artifacts, save_artifacts_to_files
from utils.frontend_artifact_parser import extract_frontend_code_artifacts, save_frontend_artifacts_to_files

# Load environment variables
load_dotenv()

# Team-level coordination tools
@tool 
def get_development_status(team: Team) -> str:
    """Get overall development status of the project for team leader.
    
    Args:
        team: The team calling this tool (automatically passed)
    """
    shared_state = team.team_session_state
    backend_status = shared_state.get("backend_status", "Not started")
    frontend_status = shared_state.get("frontend_status", "Not started")
    backend_completed = shared_state.get("backend_completed", False)
    frontend_completed = shared_state.get("frontend_completed", False)
    
    status = f"""📊 Development Status:
- Backend: {backend_status} ({'✅ Completed' if backend_completed else '🔄 In Progress'})
- Frontend: {frontend_status} ({'✅ Completed' if frontend_completed else '🔄 In Progress'})
- Files saved to: ./generated/ directory
"""
    return status

@tool
def detect_project_mode(team: Team, user_query: str) -> str:
    """
    Detect whether this is a first generation or iterative refinement request.
    
    Args:
        team: The team calling this tool (automatically passed)
        user_query: The user's request to analyze
    
    Returns:
        Analysis of project mode and recommendations for the team
    """
    import os
    
    # Check existing project state
    has_backend = os.path.exists("generated/backend") and len(os.listdir("generated/backend")) > 0
    has_frontend = os.path.exists("generated/frontend") and len(os.listdir("generated/frontend")) > 0
    
    # Keywords analysis
    first_gen_keywords = [
        "create", "build", "generate", "scaffold", "new project", 
        "from scratch", "start", "initialize", "setup", "new"
    ]
    
    iterative_keywords = [
        "update", "modify", "change", "add", "extend", "improve", 
        "fix", "refactor", "enhance", "adjust", "edit", "optimize"
    ]
    
    query_lower = user_query.lower()
    first_gen_score = sum(1 for keyword in first_gen_keywords if keyword in query_lower)
    iterative_score = sum(1 for keyword in iterative_keywords if keyword in query_lower)
    
    # Determine mode and update team state
    if has_backend or has_frontend:
        if iterative_score > first_gen_score:
            mode = "iterative_refinement"
            team.team_session_state["current_mode"] = "iterative"
            recommendation = "🔄 Iterative Refinement - Update existing project"
        else:
            mode = "first_generation"
            team.team_session_state["current_mode"] = "first_generation"
            recommendation = "⚠️ First Generation - Will overwrite existing files"
    else:
        mode = "first_generation"
        team.team_session_state["current_mode"] = "first_generation"
        recommendation = "🆕 First Generation - Create new project"
    
    analysis = f"""🎯 Team Project Mode Analysis:
- Mode: {mode}
- Existing Backend: {'✅ Yes' if has_backend else '❌ No'}
- Existing Frontend: {'✅ Yes' if has_frontend else '❌ No'}
- Recommendation: {recommendation}

📋 Query: "{user_query[:100]}{'...' if len(user_query) > 100 else ''}"
"""
    
    return analysis

@tool
def analyze_team_project_structure(team: Team) -> str:
    """
    Analyze the current project structure for the entire team.
    
    Args:
        team: The team calling this tool (automatically passed)
    
    Returns:
        Comprehensive project structure analysis
    """
    import os
    
    structure = []
    structure.append("📁 Team Project Structure Analysis:")
    structure.append("=" * 50)
    
    # Check generated directories
    if os.path.exists("generated"):
        structure.append("\n🏗️ Generated Files:")
        
        for root, dirs, files in os.walk("generated"):
            level = root.replace("generated", "").count(os.sep)
            indent = "  " * level
            folder_name = os.path.basename(root) if root != "generated" else "generated"
            structure.append(f"{indent}📂 {folder_name}/")
            
            subindent = "  " * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    structure.append(f"{subindent}📄 {file} ({size} bytes)")
                except:
                    structure.append(f"{subindent}📄 {file}")
    else:
        structure.append("\n❌ No generated directory found")
    
    # Project status summary
    structure.append(f"\n📊 Project Status:")
    shared_state = team.team_session_state
    structure.append(f"  Current Mode: {shared_state.get('current_mode', 'Not set')}")
    structure.append(f"  Backend Status: {shared_state.get('backend_status', 'Not started')}")
    structure.append(f"  Frontend Status: {shared_state.get('frontend_status', 'Not started')}")
    structure.append(f"  Project Plan: {'✅ Available' if shared_state.get('project_plan') else '❌ Missing'}")
    
    return "\n".join(structure)

@tool
def backup_team_project(team: Team) -> str:
    """
    Create a backup of the entire project before making changes.
    
    Args:
        team: The team calling this tool (automatically passed)
    
    Returns:
        Backup status and information
    """
    import os
    import shutil
    from datetime import datetime
    
    if not os.path.exists("generated"):
        return "📁 No generated files to backup"
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"team_backup_{timestamp}"
    
    try:
        shutil.copytree("generated", backup_dir)
        
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(backup_dir):
            file_count += len(files)
        
        # Update team state
        team.team_session_state["last_backup"] = backup_dir
        team.team_session_state["backup_timestamp"] = timestamp
        
        return f"✅ Team backup created: {backup_dir} ({file_count} files backed up)"
        
    except Exception as e:
        return f"❌ Team backup failed: {str(e)}"
@tool
def coordinate_development(team: Team, phase: str) -> str:
    """Coordinate the development process across team members.
    
    Args:
        team: The team calling this tool (automatically passed)
        phase: Development phase to coordinate (planning, backend, frontend, integration)
    """
    shared_state = team.team_session_state
    
    if phase == "planning":
        return "🎯 Planning phase initiated. Planner agent should create project structure."
    elif phase == "backend":
        plan = shared_state.get("project_plan", "")
        if not plan:
            return "❌ Cannot start backend development without a project plan."
        return f"🔧 Backend development phase initiated. Using plan: {plan[:100]}..."
    elif phase == "frontend":
        backend_completed = shared_state.get("backend_completed", False)
        if not backend_completed:
            return "⚠️ Frontend development should wait for backend completion."
        return "🎨 Frontend development phase initiated."
    elif phase == "integration":
        backend_completed = shared_state.get("backend_completed", False)
        frontend_completed = shared_state.get("frontend_completed", False)
        if not backend_completed or not frontend_completed:
            return "❌ Integration requires both backend and frontend to be completed."
        return "🔗 Integration phase: Both backend and frontend completed and files saved to ./generated/ directory."
    
    return f"❓ Unknown phase: {phase}"

@tool
def save_team_artifacts(team: Team, agent_type: str, response_text: str) -> str:
    """Save code artifacts generated by team members to local file system only.
    
    Args:
        team: The team calling this tool (automatically passed)
        agent_type: Type of agent that generated the code (backend or frontend)
        response_text: The response containing code artifacts
    """
    try:
        if agent_type == "backend":
            artifacts = extract_code_artifacts(response_text)
            if artifacts:
                created_files = save_artifacts_to_files(artifacts, "generated/backend")
                # Update only status in team state, not file lists
                team.team_session_state["backend_status"] = f"Completed - {len(created_files)} files generated"
                team.team_session_state["backend_completed"] = True
                return f"✅ Backend artifacts saved: {len(created_files)} files created in generated/backend/"
            else:
                return "⚠️ No backend artifacts found in response"
                
        elif agent_type == "frontend":
            artifacts = extract_frontend_code_artifacts(response_text)
            if artifacts:
                created_files = save_frontend_artifacts_to_files(artifacts, "generated/frontend")
                # Update only status in team state, not file lists
                team.team_session_state["frontend_status"] = f"Completed - {len(created_files)} files generated"
                team.team_session_state["frontend_completed"] = True
                return f"✅ Frontend artifacts saved: {len(created_files)} files created in generated/frontend/"
            else:
                return "⚠️ No frontend artifacts found in response"
        
        return f"❓ Unknown agent type: {agent_type}"
        
    except Exception as e:
        return f"❌ Error saving artifacts: {str(e)}"

# Create the Development Team
def create_development_team():
    """Create a team of development agents with shared state and persistent memory."""
    
    try:
        # Use the existing agents from their respective files
        print(f"✅ Using planner agent: {planner_agent.name}")
        print(f"✅ Using backend agent: {backend_agent.name}")
        print(f"✅ Using frontend agent: {frontend_agent.name}")
        
        # Create memory with SQLite database for persistent conversational history
        memory_db = SqliteMemoryDb(
            table_name="dev_team_memory", 
            db_file="dev_team_memory.db"
        )
        memory = Memory(db=memory_db)
        print(f"✅ Created persistent memory database: dev_team_memory.db")
        
        # Create the development team with memory
        dev_team = Team(
            name="Full-Stack Development Team",
            team_id="dev_team",
            model=OpenAIChat(id="gpt-4o-mini",api_key=os.getenv("OPENAI_API_KEY")),
            members=[planner_agent, backend_agent, frontend_agent],
            
            # Memory configuration for persistent conversational history
            memory=memory,
            add_history_to_messages=True,      # Add chat history to messages
            num_history_runs=10,               # Number of previous runs to include
            enable_user_memories=True,         # Store user preferences/facts
            enable_session_summaries=True,     # Create session summaries
            enable_agentic_memory=True,        # Let team manage memories
            
            # Shared team state - accessible by all members
            team_session_state={
                "project_plan": "",
                "project_plan_completed": False,
                "backend_status": "Not started",
                "frontend_status": "Not started", 
                "backend_completed": False,
                "frontend_completed": False,
                "current_phase": "planning",
                "current_mode": "first_generation",  # Track generation mode
                "requirements": "",
                "last_backup": "",  # Track last backup location
                "backup_timestamp": "",  # Track backup time
            },
            
            # Team coordination tools
            tools=[
                coordinate_development, 
                save_team_artifacts, 
                get_development_status,
                detect_project_mode,
                analyze_team_project_structure,
                backup_team_project
            ],
            
            # Team configuration
            mode="coordinate",  # Team leader coordinates member responses
            
            instructions=[
                "You are the Team Leader for a full-stack development team with enhanced iteration capabilities.",
                "",
                "ENHANCED WORKFLOW - ALWAYS START WITH:",
                "1. Use detect_project_mode() to understand if this is first generation or iterative refinement",
                "2. Use analyze_team_project_structure() to assess current project state",
                "3. For iterative work: Use backup_team_project() before making changes",
                "",
                "COORDINATION PROCESS:",
                "- First Generation: Planning → Backend → Frontend → Integration",
                "- Iterative Refinement: Analysis → Targeted Updates → Validation",
                "- Always check project plan before assigning development tasks",
                "- Use team tools to track progress and save generated code artifacts",
                "- Ensure each phase is completed before moving to the next",
                "",
                "TEAM MEMBER COORDINATION:",
                "- Backend Agent: Enhanced tools for search, analysis, safe file operations, and edge optimization",
                "- Frontend Agent: Enhanced tools for search, analysis, safe file operations, and modern React optimization",
                "- Planner Agent: Project planning and requirements analysis",
                "- All agents: Support both first generation and iterative refinement modes",
                "",
                "SAFETY & QUALITY:",
                "- Always create backups before significant changes (backup_team_project)",
                "- Use save_team_artifacts to persist generated work",
                "- Provide clear status updates and coordinate handoffs between members",
                "- Validate that changes don't break existing functionality",
            ],
            
            show_tool_calls=True,
            show_members_responses=True,
        )
        
        print(f"✅ Created development team with persistent memory: {dev_team.name}")
        return dev_team
        
    except Exception as e:
        print(f"❌ Error creating development team: {e}")
        raise

# Orchestrator functions
def run_development_workflow(requirements: str):
    """Run the enhanced development workflow supporting both first generation and iterative refinement."""
    
    print("🚀 Starting Enhanced Full-Stack Development Workflow")
    print("=" * 60)
    
    # Create the development team
    team = create_development_team()
    
    # Store requirements in shared state
    team.team_session_state["requirements"] = requirements
    
    print(f"📋 Requirements: {requirements}")
    print()
    
    # Phase 0: Mode Detection and Analysis
    print("🎯 Phase 0: Project Analysis & Mode Detection")
    print("-" * 50)
    
    analysis_prompt = f"""
    Before starting development, analyze the current project state:
    
    1. Use detect_project_mode to understand if this is first generation or iterative refinement
    2. Use analyze_team_project_structure to assess the current project state
    3. Based on the analysis, determine the appropriate workflow
    
    Requirements to analyze: {requirements}
    """
    
    team.print_response(analysis_prompt, stream=True)
    print("\n" + "="*60)
    
    # Phase 1: Planning (or Plan Update for iterative)
    current_mode = team.team_session_state.get("current_mode", "first_generation")
    
    if current_mode == "first_generation":
        print("🎯 Phase 1: Project Planning (First Generation)")
        print("-" * 50)
        
        planning_prompt = f"""
        Create a comprehensive project plan for the following requirements:
        {requirements}
        
        The Planner Agent should create a detailed plan including:
        - Project structure
        - Technology stack
        - API endpoints
        - Database schema
        - Frontend components
        - Implementation timeline
        
        Save the plan to shared team state using update_project_plan.
        """
    else:
        print("🎯 Phase 1: Plan Analysis & Updates (Iterative Refinement)")
        print("-" * 50)
        
        planning_prompt = f"""
        Analyze the existing project plan and update it for the new requirements:
        {requirements}
        
        The Planner Agent should:
        - Review the current project plan
        - Identify what needs to be added or modified
        - Update the plan with new requirements
        - Ensure compatibility with existing structure
        
        Use update_project_plan to save the updated plan.
        """
    
    team.print_response(planning_prompt, stream=True)
    print("\n" + "="*60)
    
    # Phase 2: Backend Development
    current_mode = team.team_session_state.get("current_mode", "first_generation")
    
    if current_mode == "first_generation":
        print("🔧 Phase 2: Backend Development (First Generation)")
        print("-" * 50)
        
        backend_prompt = f"""
        Using the project plan from shared team state, the Backend Agent should:
        
        1. Use detect_generation_mode() to confirm first generation mode
        2. Use analyze_project_structure() to understand current state
        3. Get the project plan using get_project_plan
        4. Generate complete FastAPI backend code with:
           - Database models
           - API endpoints
           - Authentication (if needed)
           - Configuration files
        5. Use proper <codeartifact> tags for all generated code
        6. Call save_generated_files() to create all files
        7. Use optimize_for_edge_deployment() for production readiness
        8. Update backend status when complete
        
        The Team Leader should save the generated artifacts using save_team_artifacts.
        """
    else:
        print("🔧 Phase 2: Backend Updates (Iterative Refinement)")
        print("-" * 50)
        
        backend_prompt = f"""
        The Backend Agent should update the existing backend for new requirements:
        
        1. Use detect_generation_mode() to confirm iterative mode
        2. Use analyze_project_structure() to understand current backend
        3. Use search_project_files() to find relevant existing code
        4. Use backup_existing_files() to create safety backup
        5. Get the updated project plan using get_project_plan
        6. For each required change:
           - Use read_project_file() to examine existing code
           - Use write_project_file() to make targeted updates
           - Preserve existing functionality
        7. Use optimize_for_edge_deployment() to validate changes
        8. Update backend status when complete
        
        Focus on extending existing code without breaking current functionality.
        """
    
    team.print_response(backend_prompt, stream=True)
    print("\n" + "="*60)
    
    # Phase 3: Frontend Development
    current_mode = team.team_session_state.get("current_mode", "first_generation")
    
    if current_mode == "first_generation":
        print("🎨 Phase 3: Frontend Development (First Generation)")
        print("-" * 50)
        
        frontend_prompt = f"""
        Using the project plan and backend status, the Frontend Agent should:
        
        1. Get the project plan using get_project_plan
        2. Check backend development status
        3. Generate complete React/Next.js frontend code with:
           - Components
           - Pages
           - API integration
           - Styling with Tailwind CSS
           - Configuration files
        4. Use proper <codeartifact> tags for all generated code
        5. Update frontend status when complete
        
        The Team Leader should save the generated artifacts using save_team_artifacts.
        """
    else:
        print("🎨 Phase 3: Frontend Updates (Iterative Refinement)")
        print("-" * 50)
        
        frontend_prompt = f"""
        The Frontend Agent should update the existing frontend for new requirements:
        
        1. Analyze existing frontend structure
        2. Get the updated project plan using get_project_plan
        3. Check backend changes and new API endpoints
        4. Create backup of existing frontend files if needed
        5. For each required change:
           - Examine existing components and pages
           - Add new components or update existing ones
           - Update API integration for new endpoints
           - Maintain existing styling and functionality
        6. Use proper <codeartifact> tags for new/updated code
        7. Update frontend status when complete
        
        Focus on extending existing frontend without breaking current features.
        """
    
    team.print_response(frontend_prompt, stream=True)
    print("\n" + "="*60)
    
    # Phase 4: Integration Summary
    current_mode = team.team_session_state.get("current_mode", "first_generation")
    
    print("🔗 Phase 4: Integration Summary & Validation")
    print("-" * 50)
    
    if current_mode == "first_generation":
        summary_prompt = """
        Provide a comprehensive summary of the completed development:
        
        1. Use get_development_status to check overall progress
        2. Use analyze_team_project_structure to show final project structure
        3. List all generated files and their purposes
        4. Provide setup instructions for both backend and frontend
        5. Include API documentation and integration points
        6. Suggest next steps for deployment
        7. Provide edge deployment optimization recommendations
        
        This completes the full-stack development workflow.
        """
    else:
        summary_prompt = """
        Provide a comprehensive summary of the iterative updates:
        
        1. Use get_development_status to check overall progress
        2. Use analyze_team_project_structure to show updated project structure
        3. List all modified/added files and their purposes
        4. Highlight what was changed vs what was preserved
        5. Provide updated setup instructions if needed
        6. Include new API documentation and integration points
        7. Validate that existing functionality is preserved
        8. Suggest testing steps for the new features
        
        This completes the iterative refinement workflow.
        """
    
    team.print_response(summary_prompt, stream=True)
    
    mode_emoji = "🆕" if current_mode == "first_generation" else "🔄"
    mode_text = "First Generation" if current_mode == "first_generation" else "Iterative Refinement"
    print(f"\n{mode_emoji} {mode_text} Development Workflow Complete!")
    
    return team

def interactive_mode():
    """Run the orchestrator in enhanced interactive mode with iteration support."""
    print("🤖 Enhanced Full-Stack Development Team - Interactive Mode")
    print("=" * 60)
    print("Available commands:")
    print("  /analyze - Analyze current project structure and mode")
    print("  /plan <requirements> - Start with project planning")
    print("  /backend - Generate/update backend code")
    print("  /frontend - Generate/update frontend code")
    print("  /status - Check development status")
    print("  /backup - Create backup of current project")
    print("  /workflow <requirements> - Run complete workflow (auto-detects mode)")
    print("  /optimize - Optimize current backend for edge deployment")
    print("  /search <query> - Search across project files")
    print("  /quit - Exit")
    print()
    
    team = create_development_team()
    
    while True:
        try:
            user_input = input("\n💬 Enter command or message: ").strip()
            
            if user_input == "/quit":
                print("👋 Goodbye!")
                break
            elif user_input == "/analyze":
                team.print_response("Use detect_project_mode and analyze_team_project_structure to analyze the current project", stream=True)
            elif user_input.startswith("/plan "):
                requirements = user_input[6:]
                team.team_session_state["requirements"] = requirements
                team.print_response(f"Analyze the project mode and create/update a project plan for: {requirements}", stream=True)
            elif user_input == "/backend":
                team.print_response("Analyze the current project and generate/update backend code based on the project plan", stream=True)
            elif user_input == "/frontend":
                team.print_response("Analyze the current project and generate/update frontend code based on the project plan and backend", stream=True)
            elif user_input == "/status":
                team.print_response("Use get_development_status and analyze_team_project_structure to show current status", stream=True)
            elif user_input == "/backup":
                team.print_response("Use backup_team_project to create a backup of the current project", stream=True)
            elif user_input == "/optimize":
                team.print_response("Have the Backend Agent use optimize_for_edge_deployment to analyze the current backend", stream=True)
            elif user_input.startswith("/search "):
                query = user_input[8:]
                team.print_response(f"Have the Backend Agent use search_project_files to search for: {query}", stream=True)
            elif user_input.startswith("/workflow "):
                requirements = user_input[10:]
                return run_development_workflow(requirements)
            else:
                # Enhanced natural language processing
                enhanced_prompt = f"""
                Analyze this request and determine the appropriate action:
                "{user_input}"
                
                1. First use detect_project_mode to understand if this is first generation or iterative
                2. Use analyze_team_project_structure to understand current state
                3. Based on the analysis, coordinate the appropriate team members
                4. If making changes, consider using backup_team_project first
                """
                team.print_response(enhanced_prompt, stream=True)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run with requirements from command line
        requirements = " ".join(sys.argv[1:])
        run_development_workflow(requirements)
    else:
        # Run in interactive mode
        interactive_mode()
