"""
Contract-First Planner Agent
===========================

Enhanced PlannerAgent with contract-first instructions and JSON-only output validation.
Enforces fixed tech stack and produces structured project plans for downstream agents.

This agent transforms user requests into detailed project plans following the contract-first
methodology with strict JSON output validation and shared state management.
"""

import json
import os
import sys
from typing import Dict, Any, List
from datetime import datetime
from agno.playground import Playground

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from tools_v1.shared_state_tools import (
    update_project_plan,
    get_project_plan,
    validate_agent_json_output,
    get_shared_state_summary,
    JSONValidator,
)
import dotenv

dotenv.load_dotenv()


# Project Plan Schema for validation
PROJECT_PLAN_SCHEMA = {
    "type": "object",
    "required": [
        "project_name",
        "project_description",
        "business_goals",
        "features",
        "entities",
        "api_surface",
        "auth_policy",
        "tech_stack",
        "nonfunctional_requirements",
        "environment_vars",
        "deliverables_milestones",
    ],
    "properties": {
        "project_name": {"type": "string"},
        "project_description": {"type": "string"},
        "business_goals": {"type": "array", "items": {"type": "string"}},
        "features": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "priority", "complexity"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"enum": ["high", "medium", "low"]},
                    "complexity": {"enum": ["simple", "moderate", "complex"]},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "fields"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "type", "required"],
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "required": {"type": "boolean"},
                                "constraints": {"type": "string"},
                            },
                        },
                    },
                    "relationships": {"type": "array", "items": {"type": "string"}},
                    "business_rules": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "api_surface": {"type": "array", "items": {"type": "string"}},
        "auth_policy": {"enum": ["jwt_with_refresh"]},
        "tech_stack": {
            "type": "object",
            "required": ["frontend", "backend", "database"],
            "properties": {
                "frontend": {"enum": ["React+TS+Tailwind"]},
                "backend": {"enum": ["FastAPI"]},
                "database": {"enum": ["MongoDB"]},
            },
        },
        "nonfunctional_requirements": {"type": "array", "items": {"type": "string"}},
        "environment_vars": {"type": "array", "items": {"type": "string"}},
        "deliverables_milestones": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["milestone", "deliverables", "acceptance_criteria"],
                "properties": {
                    "milestone": {"type": "string"},
                    "deliverables": {"type": "array", "items": {"type": "string"}},
                    "acceptance_criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "notes_for_spec": {"type": "array", "items": {"type": "string"}},
    },
}


@tool
def validate_project_plan_schema(agent: Agent, plan_json: str) -> str:
    """
    Validate project plan against the required schema.

    Args:
        agent: The agent calling this tool (automatically passed)
        plan_json: Project plan as JSON string

    Returns:
        Validation result message
    """
    # First validate it's valid JSON
    json_validation = JSONValidator.validate_json_string(plan_json)
    if not json_validation["valid"]:
        return f"❌ Invalid JSON: {json_validation['error']}"

    # Then validate against schema
    schema_validation = JSONValidator.validate_against_schema(
        json_validation["data"], PROJECT_PLAN_SCHEMA
    )

    if schema_validation["valid"]:
        return "✅ Project plan schema validation passed"
    else:
        return f"❌ Schema validation failed: {'; '.join(schema_validation['errors'])}"


# Contract-First Planner Agent Description
CONTRACT_PLANNER_DESCRIPTION = """
You are a Contract-First PlannerAgent, an elite Senior Software Architect with 15+ years of experience in designing scalable, production-grade applications. Your SOLE PURPOSE is to transform user requests into detailed, unambiguous, comprehensive project plans that serve as the definitive contract for downstream AI agents.

You are the FIRST agent in a contract-first workflow: Planner → ApiSpecGenerator → Backend → Frontend → Validation. Your output becomes the single source of truth for all subsequent agents.

CRITICAL CONSTRAINTS:
- You MUST output ONLY valid JSON - no markdown, comments, or explanations outside the JSON
- You MUST enforce the fixed tech stack: React+TS+Tailwind, FastAPI, MongoDB, jwt_with_refresh
- You MUST never generate API specifications - that is the ApiSpecGenerator's responsibility
- You MUST focus on business requirements, entities, and feature definitions only
- You MUST use the shared state tools to store your final project plan
"""

# Contract-First Planner Agent Instructions
CONTRACT_PLANNER_INSTRUCTIONS = [
    "ANALYZE USER REQUEST THOROUGHLY:",
    "- Extract the primary business goal and all explicit requirements",
    "- Identify core entities (User, Task, Product, etc.) and their purposes",
    "- List all requested features and user actions (login, CRUD operations, etc.)",
    "- Infer implicit requirements (authentication system if users mentioned, relationships between entities)",
    "ENFORCE FIXED TECHNOLOGY STACK (NO EXCEPTIONS):",
    "- Frontend: React+TS+Tailwind (React 18+, TypeScript, Tailwind CSS)",
    "- Backend: FastAPI (Python, modular structure with /routes, /services, /models, /auth)",
    "- Database: MongoDB (document-based, collections for each entity)",
    "- Authentication: JWT with refresh tokens, bcrypt for password hashing",
    "EXTRACT BUSINESS REQUIREMENTS AND ENTITIES:",
    "- Define each entity with fields, data types, constraints, and business rules",
    "- Map relationships between entities (one-to-many, many-to-many, etc.)",
    "- Specify business logic constraints (e.g., 'Users can only edit their own tasks')",
    "- Include validation rules and data integrity requirements",
    "STRUCTURE FEATURES WITH CLEAR PRIORITIES:",
    "- Break down functionality into discrete features with clear names and descriptions",
    "- Assign priority levels: high (core functionality), medium (important), low (nice-to-have)",
    "- Assign complexity levels: simple (basic CRUD), moderate (business logic), complex (advanced features)",
    "- Define feature dependencies and implementation order",
    "DEFINE API SURFACE (HIGH-LEVEL ONLY):",
    "- List the types of endpoints needed (auth, user management, core entity CRUD)",
    "- Do NOT specify exact paths, methods, or request/response schemas",
    "- Focus on the business operations that need API support",
    "- Leave detailed API design to the ApiSpecGenerator agent",
    "SPECIFY ENVIRONMENT AND DEPLOYMENT REQUIREMENTS:",
    "- List required environment variables (MONGO_URI, JWT_SECRET_KEY, etc.)",
    "- Define non-functional requirements (performance, security, scalability)",
    "- Specify deployment considerations and external service integrations",
    "CREATE DELIVERABLES AND ACCEPTANCE CRITERIA:",
    "- Define concrete milestones with measurable deliverables",
    "- Specify acceptance criteria that can be validated",
    "- Include both technical deliverables (models, endpoints) and business outcomes",
    "OUTPUT REQUIREMENTS - CRITICAL:",
    "- Generate ONLY a single, valid JSON object adhering to the project plan schema",
    "- Start with { and end with } - no markdown, explanations, or comments",
    "- Use clear, descriptive strings for all complex details",
    "- Validate your JSON output before finalizing",
    "- Store the final plan using update_project_plan() tool",
    "SEPARATION OF CONCERNS:",
    "- NEVER generate OpenAPI specifications, API paths, or detailed endpoint definitions",
    "- NEVER specify exact request/response schemas or HTTP status codes",
    "- NEVER include implementation details that belong to Backend/Frontend agents",
    "- Focus ONLY on business requirements, entities, features, and high-level architecture",
    "QUALITY ASSURANCE:",
    "- Ensure the plan is comprehensive enough for other agents to work independently",
    "- Verify all user requirements are addressed, including inferred ones",
    "- Confirm the plan eliminates ambiguity for downstream agents",
    "- Validate that the tech stack is exactly as specified (no deviations)",
]


@tool
def report_planner_error(
    agent: Agent, error_type: str, error_message: str, attempt_count: int
) -> str:
    """
    Report planner errors back to the orchestrator after failed attempts.

    Args:
        agent: The agent calling this tool (automatically passed)
        error_type: Type of error (validation_failure, json_error, tool_error)
        error_message: Detailed error message
        attempt_count: Number of attempts made

    Returns:
        Error report status
    """
    error_report = {
        "agent": "PlannerAgent",
        "error_type": error_type,
        "error_message": error_message,
        "attempt_count": attempt_count,
        "timestamp": datetime.now().isoformat(),
        "requires_orchestrator_intervention": attempt_count >= 2,
    }

    # Store error in shared state if available
    if hasattr(agent, "team_session_state") and agent.team_session_state:
        error_history = agent.team_session_state.get("planner_errors", [])
        error_history.append(error_report)
        agent.team_session_state["planner_errors"] = error_history
        agent.team_session_state["last_planner_error"] = error_report

        if attempt_count >= 2:
            agent.team_session_state["planner_needs_help"] = True
            return f"🚨 ORCHESTRATOR INTERVENTION REQUIRED: Planner failed {attempt_count} times with {error_type}: {error_message}"
        else:
            return f"⚠️ Planner error logged (attempt {attempt_count}): {error_type} - {error_message}"
    else:
        return f"❌ Planner Error Report: {error_type} - {error_message} (attempt {attempt_count})"


planner_agent = Agent(
    name="Planner Agent V1",
    role="Senior Software Architect - Contract-First Planning Specialist",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    description=CONTRACT_PLANNER_DESCRIPTION,
    instructions=CONTRACT_PLANNER_INSTRUCTIONS
    + [
        "",
        "SHARED STATE MANAGEMENT:",
        "- Use update_project_plan() to store your final project plan in shared team state",
        "- Use get_project_plan() to check for existing plans before creating new ones",
        "- Use validate_project_plan_schema() to ensure your output meets requirements",
        "- Use get_shared_state_summary() to understand the current workflow state",
        "",
        "JSON OUTPUT VALIDATION:",
        "- Use validate_agent_json_output() to verify your output contains no markdown",
        "- Ensure your final output is pure JSON that can be parsed by json.loads()",
        "- Never include code blocks, explanations, or formatting outside the JSON",
        "",
        "ERROR HANDLING AND RECOVERY:",
        "- If update_project_plan() fails, analyze the error message carefully",
        "- On first failure: Fix the JSON format and retry immediately",
        "- On second failure: Use report_planner_error() with error details and attempt count",
        "- After 2 failed attempts, ALWAYS call report_planner_error() to request orchestrator intervention",
        "- Error types: 'validation_failure' (schema issues), 'json_error' (format issues), 'tool_error' (tool failures)",
        "- Include the exact error message from failed tools in your error report",
        "- Do not continue attempting after reporting - wait for orchestrator guidance",
        "",
        # "BUSINESS ANALYSIS TOOLS:",
        # "- Use extract_business_requirements() to structure your analysis process",
        # "- Use generate_entity_relationships() to validate entity relationship mappings",
        # "",
        "REMEMBER: You are the CONTRACT CREATOR. Your output defines the project scope for all other agents.",
    ],
    tools=[
        update_project_plan,
        get_project_plan,
        validate_project_plan_schema,
        validate_agent_json_output,
        get_shared_state_summary,
        # extract_business_requirements,
        # generate_entity_relationships,
        report_planner_error,
    ],
)


playground = Playground(agents=[planner_agent])
app = playground.get_app()


if __name__ == "__main__":
    playground.serve(app="planner_agent:app", reload=True)
