from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.tools import tool
from rich.pretty import pprint
from agno.playground import Playground
import dotenv
import sys
import os
import json

dotenv.load_dotenv()

# JSON validation tool for planner agent
@tool
def validate_project_plan_json(plan_json: str) -> str:
    """Validate that the project plan follows the correct JSON schema format.
    
    Args:
        plan_json: JSON string of the project plan
    
    Returns:
        Validation result with any errors found
    """
    try:
        plan = json.loads(plan_json)
        
        required_sections = [
            "project_name", "description", "features", "tech_stack", 
            "database_models", "architecture", "environment", 
            "deliverables", "acceptance_criteria"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in plan:
                missing_sections.append(section)
        
        if missing_sections:
            return f"❌ Missing required sections: {', '.join(missing_sections)}"
        
        # Validate features structure
        if not isinstance(plan["features"], list):
            return "❌ features must be a list"
        
        for i, feature in enumerate(plan["features"]):
            required_fields = ["name", "description", "priority", "complexity", "dependencies", "acceptance_criteria"]
            for field in required_fields:
                if field not in feature:
                    return f"❌ Feature {i+1} missing required field: {field}"
            
            # Validate priority values
            if feature["priority"] not in ["High", "Medium", "Low"]:
                return f"❌ Feature '{feature['name']}' has invalid priority. Must be High, Medium, or Low"
            
            # Validate complexity values
            if feature["complexity"] not in ["Simple", "Moderate", "Complex"]:
                return f"❌ Feature '{feature['name']}' has invalid complexity. Must be Simple, Moderate, or Complex"
        
        # Validate database_models structure
        if not isinstance(plan["database_models"], list):
            return "❌ database_models must be a list"
        
        for i, model in enumerate(plan["database_models"]):
            required_fields = ["name", "collection", "description", "relationships", "business_rules"]
            for field in required_fields:
                if field not in model:
                    return f"❌ Database model {i+1} missing required field: {field}"
        
        return "✅ Project plan JSON format is valid"
        
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON format: {str(e)}"
    except Exception as e:
        return f"❌ Validation error: {str(e)}"

@tool
def generate_comprehensive_features(project_type: str, core_entities: str) -> str:
    """Generate a comprehensive feature list based on project type and entities.
    
    Args:
        project_type: Type of project (e.g., 'task management', 'e-commerce', 'social media')
        core_entities: Main entities in the system (e.g., 'users, tasks, projects')
    
    Returns:
        JSON string with comprehensive feature list
    """
    
    # Base features that every application needs
    base_features = [
        {
            "name": "User Authentication",
            "description": "Complete user registration, login, logout, password reset, and email verification system with JWT tokens",
            "priority": "High",
            "complexity": "Moderate",
            "dependencies": [],
            "acceptance_criteria": [
                "Users can register with email and password",
                "Users can login and receive JWT access/refresh tokens",
                "Users can reset password via email",
                "Email verification required for account activation",
                "Secure logout invalidates tokens"
            ]
        },
        {
            "name": "User Profile Management",
            "description": "User profile creation, editing, avatar upload, and account settings management",
            "priority": "High",
            "complexity": "Simple",
            "dependencies": ["User Authentication"],
            "acceptance_criteria": [
                "Users can view and edit their profile information",
                "Users can upload and change profile avatars",
                "Users can update account settings and preferences",
                "Profile data is validated and sanitized"
            ]
        },
        {
            "name": "Role-Based Access Control",
            "description": "Multi-level user roles and permissions system for enterprise security",
            "priority": "High",
            "complexity": "Complex",
            "dependencies": ["User Authentication"],
            "acceptance_criteria": [
                "Admin, Manager, and User roles with different permissions",
                "Role-based access to features and data",
                "Permission inheritance and override capabilities",
                "Audit trail for role changes"
            ]
        }
    ]
    
    # Project-specific features based on type
    project_specific = []
    
    if "task" in project_type.lower() or "project" in project_type.lower():
        project_specific.extend([
            {
                "name": "Task Management",
                "description": "Complete CRUD operations for tasks with status tracking, assignments, and due dates",
                "priority": "High",
                "complexity": "Moderate",
                "dependencies": ["User Authentication", "User Profile Management"],
                "acceptance_criteria": [
                    "Users can create, read, update, and delete tasks",
                    "Tasks have title, description, status, priority, and due date",
                    "Tasks can be assigned to users",
                    "Task status workflow (Todo, In Progress, Done)"
                ]
            },
            {
                "name": "Project Organization",
                "description": "Project creation and management with team collaboration features",
                "priority": "High",
                "complexity": "Complex",
                "dependencies": ["Task Management", "Role-Based Access Control"],
                "acceptance_criteria": [
                    "Users can create and manage projects",
                    "Projects contain multiple tasks",
                    "Team members can be added to projects",
                    "Project-level permissions and visibility"
                ]
            },
            {
                "name": "Time Tracking",
                "description": "Time logging and tracking for tasks and projects with reporting",
                "priority": "Medium",
                "complexity": "Moderate",
                "dependencies": ["Task Management"],
                "acceptance_criteria": [
                    "Users can start/stop time tracking on tasks",
                    "Manual time entry with validation",
                    "Time reports by user, project, and date range",
                    "Export time data to CSV/PDF"
                ]
            }
        ])
    
    # Enterprise features
    enterprise_features = [
        {
            "name": "Audit Logging",
            "description": "Comprehensive audit trail for all user actions and system changes",
            "priority": "Medium",
            "complexity": "Moderate",
            "dependencies": ["User Authentication"],
            "acceptance_criteria": [
                "All user actions are logged with timestamps",
                "Audit logs include user, action, and affected resources",
                "Audit logs are searchable and filterable",
                "Audit data retention and archival policies"
            ]
        },
        {
            "name": "API Rate Limiting",
            "description": "Rate limiting and throttling to prevent API abuse",
            "priority": "Medium",
            "complexity": "Simple",
            "dependencies": [],
            "acceptance_criteria": [
                "Rate limits per user and IP address",
                "Configurable rate limit thresholds",
                "Rate limit headers in API responses",
                "Graceful handling of rate limit exceeded"
            ]
        },
        {
            "name": "Data Export/Import",
            "description": "Bulk data export and import capabilities with multiple formats",
            "priority": "Low",
            "complexity": "Moderate",
            "dependencies": ["User Authentication"],
            "acceptance_criteria": [
                "Export user data in JSON, CSV, and PDF formats",
                "Import data with validation and error handling",
                "Bulk operations with progress tracking",
                "Data backup and restore functionality"
            ]
        }
    ]
    
    # Combine all features
    all_features = base_features + project_specific + enterprise_features
    
    return json.dumps({"comprehensive_features": all_features}, indent=2)

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
PlannerAgent is an elite Senior Software Architect with over 15 years of experience in designing scalable, production-grade, full-stack applications. Its sole purpose is to transform user requests into high-level project plans that define the 'what' of the system - requirements, architecture, features, and technology stack. The agent focuses exclusively on strategic planning and delegates all API contract design to the ApiSpecGenerator agent. It produces structured project plans that serve as the foundation for other specialized agents to build upon.
"""

# Instructions format: A list of precise, task-specific instructions
PLANNER_INSTRUCTIONS = [
    "STRICT JSON OUTPUT REQUIREMENT: Always output a single, valid JSON object. Never output arrays, free text, or markdown. Start with { and end with }.",
    "JSON VALIDATION: Use validate_project_plan_json() to validate your JSON before finalizing the response.",
    "COMPREHENSIVE FEATURE GENERATION: Use generate_comprehensive_features() to ensure complete feature coverage including authentication, CRUD, workflows, enterprise features, and integrations.",
    
    "ANALYSIS PHASE:",
    "Analyze User Request: Thoroughly dissect the user's prompt to identify all explicit and implicit requirements.",
    "Determine the primary business goal, core entities (e.g., users, tasks, products), and requested features/user actions.",
    "Identify project type (task management, e-commerce, social media, etc.) to generate appropriate features.",
    
    "TECHNOLOGY STACK ENFORCEMENT:",
    "Frontend: React.js 18+ with TypeScript, Next.js 14+ App Router, Tailwind CSS, React Hook Form, Zustand for state management.",
    "Backend: FastAPI with Python 3.9+, structured with modular folders (/routes, /services, /models, /auth, /utils).",
    "Database: MongoDB exclusively with Motor async driver and Pydantic models.",
    "Authentication: JWT with refresh tokens, bcrypt for password hashing, role-based access control.",
    "Deployment: Docker containers, environment-based configuration, health checks, logging.",
    
    "FEATURE SPECIFICATION REQUIREMENTS:",
    "Generate complete feature list covering: Authentication system (registration, login, password reset, email verification), User management (profiles, roles, permissions), Core business logic (CRUD operations for main entities), Workflow management (status tracking, assignments, notifications), Time tracking and reporting (if applicable), Data visualization and analytics, Enterprise features (audit logging, rate limiting, data export/import), Integration capabilities (APIs, webhooks, third-party services).",
    "For each feature, include: name (clear, descriptive feature name), description (detailed purpose and functionality, minimum 20 words), priority (High/Medium/Low based on business value and user needs), complexity (Simple/Moderate/Complex based on technical implementation), dependencies (list of other features this depends on), acceptance_criteria (list of 3-5 testable, measurable criteria).",
    "Ensure feature dependencies are properly linked (e.g., Task Management depends on User Authentication).",
    "Map priority to complexity realistically (High priority doesn't always mean Complex).",
    
    "DATABASE MODEL DESIGN:",
    "Define MongoDB models for every feature with: name (entity name), collection (MongoDB collection name), description (detailed field specifications with types, constraints, and purposes), relationships (entity relationships with cardinality), business_rules (constraints, validation rules, unique fields, indexes).",
    "Include audit fields (created_at, updated_at, created_by, updated_by) for all models.",
    "Design for scalability with proper indexing and relationship strategies.",
    
    "ARCHITECTURE SPECIFICATION:",
    "Backend Architecture: Modular FastAPI structure with Repository pattern for data access, Service layer for business logic, Route handlers for API endpoints, Middleware for authentication, logging, and CORS, Background tasks for async operations.",
    "Frontend Architecture: Next.js App Router with TypeScript, Client components for interactivity, Server components for data fetching, API routes for backend communication, Custom hooks for data management, Utility functions and type definitions.",
    "DO NOT generate API endpoints or schemas - delegate all API contract design to the ApiSpecGenerator agent.",
    
    "ENVIRONMENT CONFIGURATION:",
    "Include comprehensive environment variables: Database (MONGODB_URL, DATABASE_NAME), Authentication (JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS), Email (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD), File Storage (AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY), Monitoring (LOG_LEVEL, SENTRY_DSN), Deployment (ENVIRONMENT, DEBUG_MODE, ALLOWED_ORIGINS).",
    
    "DELIVERABLES AND ACCEPTANCE CRITERIA:",
    "Map deliverables directly to features with 1:1 traceability.",
    "Include concrete deliverables: Database models and schemas, Authentication system with JWT, API endpoints (delegated to ApiSpecGenerator), Frontend components and pages, User interface with responsive design, Testing suite with unit and integration tests, Documentation and deployment guides.",
    "Define measurable acceptance criteria that can be tested and verified.",
    
    "VALIDATION AND QUALITY ASSURANCE:",
    "Use validate_project_plan_json() to ensure JSON schema compliance before finalizing.",
    "Verify all required sections are present and properly structured.",
    "Ensure feature dependencies are logical and complete.",
    "Check that complexity matches the described functionality.",
    "Validate that acceptance criteria are specific and testable.",
    
    "CRITICAL REQUIREMENTS:",
    "Always output valid JSON - no markdown, no explanations outside the JSON object.",
    "Include all required sections: project_name, description, features, tech_stack, database_models, architecture, environment, deliverables, acceptance_criteria.",
    "Generate comprehensive feature lists appropriate for production applications.",
    "Ensure enterprise-grade considerations (security, scalability, monitoring, compliance).",
    "Do not deviate from the specified technology stack under any circumstances.",
    "IMPORTANT: Do NOT generate API endpoints or schemas. Focus only on high-level planning and delegate API contract design to the ApiSpecGenerator agent.",
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
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
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
        "- Delegate all API contract design to the ApiSpecGenerator agent",
    ],
    tools=[update_project_plan, get_project_plan, get_development_status, validate_project_plan_json, generate_comprehensive_features],
    show_tool_calls=True,
)

# Import API spec agent for playground integration
try:
    from api_spec_agent import api_spec_agent
    playground = Playground(agents=[planner_agent, api_spec_agent])
except ImportError:
    playground = Playground(agents=[planner_agent])

app = playground.get_app()


# # Example usage - Create a project plan
if __name__ == "__main__":
    playground.serve(app="planner_agent:app", reload=True)
