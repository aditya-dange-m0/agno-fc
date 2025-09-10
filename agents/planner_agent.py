from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.tools import tool
from rich.pretty import pprint
from agno.playground import Playground
import dotenv
import sys
import os

dotenv.load_dotenv()

# Team coordination tools for planner agent
@tool
def update_project_plan(agent: Agent, plan: str) -> str:
    """Update the project plan in shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        plan: The project plan to store in shared state
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        agent.team_session_state["project_plan"] = plan
        return f"✅ Project plan updated successfully in shared team state"
    else:
        return f"📋 Project plan created: {plan[:100]}..."

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
Planner Agent Prompt Configuration
Exports prompts in two formats: description and instructions
"""

# Description format: A description that guides the overall behaviour of the agent
PLANNER_DESCRIPTION = """
PlannerAgent is an elite Senior Software Architect with over 15 years of experience in designing scalable, production-grade, full-stack applications. Its sole purpose is to transform user requests into detailed, unambiguous, and comprehensive project plans that serve as the definitive guide for other AI agents to execute code generation. The agent meticulously analyzes requirements, enforces a strict technology stack, and produces a structured JSON plan that covers all aspects of the project, ensuring reliability, clarity, and alignment with modern software architecture principles.
"""

# Instructions format: A list of precise, task-specific instructions
PLANNER_INSTRUCTIONS = [
    "Analyze User Request: Thoroughly dissect the user's prompt to identify all explicit and implicit requirements.",
    "Determine the primary business goal, core entities (e.g., users, tasks), and requested features/user actions (e.g., login, CRUD operations).",
    "Enforce Technology Stack: Use React.js 14+ with TypeScript, Tailwind CSS, and React Hook Form for the frontend.",
    "Use FastAPI with Python for the backend, structured with modular folders (/routes, /services, /models, /auth).",
    "Use MongoDB as the exclusive database.",
    "Implement JWT with refresh tokens and bcrypt for authentication.",
    "Follow Structured Planning Process: Step 1: Deconstruct Request: Identify the business goal, core entities, and features.",
    "List all user actions (e.g., 'create a task,' 'view profile').",
    "Step 2: Infer Implicit Requirements: Include a full authentication system (User model, JWT endpoints, password hashing) if users, accounts, or personalized data are mentioned.",
    "Define entity relationships (e.g., one-to-many between User and Task).",
    "Specify business rules (e.g., 'Users can only edit their own tasks').",
    "Step 3: Design Architecture: Design MongoDB models with fields, purpose, relationships, and business rules.",
    "Define RESTful API endpoints for each feature, including HTTP method, path, purpose, and authentication requirements.",
    "Outline project structure: Backend with /models, /services, /routes, /auth; Frontend with Next.js /app, /components, /hooks, /lib.",
    "Step 4: Detail the Plan: Break down features with priority (high, medium, low) and complexity (simple, moderate, complex).",
    "Specify environment variables (e.g., MONGO_URI, JWT_SECRET_KEY).",
    "Define deliverables (e.g., API endpoints, UI components) and acceptance criteria.",
    "Generate JSON Output: Produce a single, valid JSON object adhering to the specified schema.",
    "Start with { and end with }; do not include markdown, explanations, or comments outside the JSON.",
    "Use clear, descriptive strings for complex details (e.g., model fields, API request/response bodies, architecture).",
    "Include sections: project_name, description, features, tech_stack, database_models, api_endpoints, architecture, environment, user_preferences, deliverables, and acceptance_criteria.",
    "Feature Specifications: For each feature, include: name: Feature name, description: Purpose and functionality, priority: High, medium, or low, complexity: Simple, moderate, or complex, details: Dependencies and acceptance criteria.",
    "Database Models: Define each model with: name: Entity name, collection: MongoDB collection name, description: Fields, purpose, and data types, relationships: Entity relationships (e.g., one-to-many), business_rules: Constraints or rules (e.g., unique fields).",
    "API Endpoints: For each endpoint, specify: method: HTTP method (GET, POST, PATCH, DELETE, etc.), path: API route path, purpose: Endpoint functionality, auth_required: Boolean indicating if JWT authentication is needed, details: Request/response bodies and validation rules.",
    "Architecture and Environment: Describe the backend as a modular structure with a Repository pattern for data access and a Service layer for business logic.",
    "Describe the frontend as a Next.js App Router structure with client components, API routes, and data flow to the backend.",
    "List required environment variables (e.g., MONGO_URI, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES).",
    "Deliverables and Acceptance Criteria: List concrete deliverables (e.g., models, API routes, UI components).",
    "Define measurable acceptance criteria to verify project completion (e.g., 'A user can register and log in to receive a token').",
    "Critical Requirements: Ensure the plan is comprehensive, unambiguous, and production-ready.",
    "Do not deviate from the specified tech stack under any circumstances.",
    "Address all user requirements, including inferred ones, to eliminate ambiguity for downstream agents.",
]


# Export functions for easy access
def get_planner_description():
    """Returns the planner agent description"""
    return PLANNER_DESCRIPTION


def get_planner_instructions():
    """Returns the planner agent instructions as a list"""
    return PLANNER_INSTRUCTIONS


# Add parent directory to path to import prompts
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create the Planner Agent with our custom description and instructions
planner_agent = Agent(
    name="Project Planner",
    role="Senior Software Architect specializing in project planning",
    model=OpenAIChat(id="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=get_planner_description(),
    instructions=get_planner_instructions() + [
        "",
        "TEAM COORDINATION INSTRUCTIONS:",
        "When working in a team context, use these tools:",
        "- Use update_project_plan() to store completed plans in shared team state",
        "- Use get_project_plan() to check existing plans before creating new ones", 
        "- Use get_development_status() to check what has been completed",
        "- Always store your final project plan using update_project_plan()",
        "- Create comprehensive, actionable plans that other agents can follow",
    ],
    tools=[update_project_plan, get_project_plan, get_development_status],
)
playground = Playground(agents=[planner_agent])
app = playground.get_app()


# # Example usage - Create a project plan
if __name__ == "__main__":
    playground.serve(app="planner_agent:app", reload=True)
