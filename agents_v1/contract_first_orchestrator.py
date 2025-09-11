"""
Contract-First Orchestrator - Multi-Agent System Coordinator
==========================================================

This orchestrator manages the contract-first workflow using the agno Team class pattern.
It coordinates agent handoffs, manages shared state, and implements the workflow state machine:
Planning → Spec Generation → Backend Generation → Frontend Generation → Completed

Key Features:
- Workflow state machine with proper transitions
- Shared state integrity validation and error recovery
- Revision management for api_spec updates
- Team coordination tools for agent handoff management
- Contract compliance validation across all phases
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.playground import Playground

# Import agents
from agents_v1.planner_agent import planner_agent
from agents_v1.api_spec_generator_agent import api_spec_generator_agent
from agents_v1.backend_agent import backend_agent
from agents_v1.frontend_agent import frontend_agent

# Import shared state tools
from tools_v1.shared_state_tools import (
    get_project_plan,
    get_api_spec,
    get_backend_report,
    get_frontend_report,
    get_shared_state_summary,
    JSONValidator,
    RevisionManager,
)

import dotenv

dotenv.load_dotenv()


class WorkflowPhase(Enum):
    """Workflow phases for the contract-first system"""

    PLANNING = "planning"
    SPEC_GENERATION = "spec_generation"
    BACKEND_GENERATION = "backend_generation"
    FRONTEND_GENERATION = "frontend_generation"
    VALIDATION = "validation"
    COMPLETED = "completed"
    ERROR = "error"


class WorkflowStatus(Enum):
    """Workflow status indicators"""

    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"


# Workflow State Machine Tools
@tool
def get_workflow_status(team: Team) -> str:
    """
    Get current workflow status and phase information.

    Args:
        team: The team calling this tool (automatically passed)

    Returns:
        Formatted workflow status report
    """
    shared_state = team.team_session_state
    current_phase = shared_state.get("current_phase", WorkflowPhase.PLANNING.value)
    workflow_status = shared_state.get(
        "workflow_status", WorkflowStatus.INITIALIZED.value
    )

    # Get completion status for each phase
    phases_status = {
        WorkflowPhase.PLANNING.value: (
            "✅ Complete" if shared_state.get("project_plan") else "❌ Pending"
        ),
        WorkflowPhase.SPEC_GENERATION.value: (
            "✅ Complete" if shared_state.get("api_spec") else "❌ Pending"
        ),
        WorkflowPhase.BACKEND_GENERATION.value: (
            "✅ Complete" if shared_state.get("backend_report") else "❌ Pending"
        ),
        WorkflowPhase.FRONTEND_GENERATION.value: (
            "✅ Complete" if shared_state.get("frontend_report") else "❌ Pending"
        ),
    }

    status_report = f"""🔄 Contract-First Workflow Status:
Current Phase: {current_phase.upper()}
Workflow Status: {workflow_status.upper()}

📋 Phase Completion:
  Planning: {phases_status[WorkflowPhase.PLANNING.value]}
  Spec Generation: {phases_status[WorkflowPhase.SPEC_GENERATION.value]}
  Backend Generation: {phases_status[WorkflowPhase.BACKEND_GENERATION.value]}
  Frontend Generation: {phases_status[WorkflowPhase.FRONTEND_GENERATION.value]}

🕒 Last Updated: {shared_state.get('last_phase_update', 'Never')}
"""

    return status_report


@tool
def transition_workflow_phase(
    team: Team, target_phase: str, validation_required: bool = True
) -> str:
    """
    Transition workflow to the next phase with validation.

    Args:
        team: The team calling this tool (automatically passed)
        target_phase: Target phase to transition to
        validation_required: Whether to validate prerequisites

    Returns:
        Status message indicating success or failure
    """
    shared_state = team.team_session_state
    current_phase = shared_state.get("current_phase", WorkflowPhase.PLANNING.value)

    # Validate phase transition
    valid_transitions = {
        WorkflowPhase.PLANNING.value: [WorkflowPhase.SPEC_GENERATION.value],
        WorkflowPhase.SPEC_GENERATION.value: [
            WorkflowPhase.BACKEND_GENERATION.value,
            WorkflowPhase.FRONTEND_GENERATION.value,
        ],
        WorkflowPhase.BACKEND_GENERATION.value: [
            WorkflowPhase.FRONTEND_GENERATION.value,
            WorkflowPhase.VALIDATION.value,
        ],
        WorkflowPhase.FRONTEND_GENERATION.value: [
            WorkflowPhase.VALIDATION.value,
            WorkflowPhase.COMPLETED.value,
        ],
        WorkflowPhase.VALIDATION.value: [
            WorkflowPhase.COMPLETED.value,
            WorkflowPhase.PLANNING.value,
        ],  # Can loop back for regeneration
        WorkflowPhase.COMPLETED.value: [WorkflowPhase.PLANNING.value],  # Can restart
        WorkflowPhase.ERROR.value: [
            WorkflowPhase.PLANNING.value,
            WorkflowPhase.SPEC_GENERATION.value,
        ],
    }

    if validation_required and target_phase not in valid_transitions.get(
        current_phase, []
    ):
        return f"❌ Invalid phase transition from {current_phase} to {target_phase}"

    # Validate prerequisites for target phase
    if validation_required:
        if (
            target_phase == WorkflowPhase.SPEC_GENERATION.value
            and not shared_state.get("project_plan")
        ):
            return "❌ Cannot transition to spec generation: project plan required"
        elif (
            target_phase == WorkflowPhase.BACKEND_GENERATION.value
            and not shared_state.get("api_spec")
        ):
            return (
                "❌ Cannot transition to backend generation: API specification required"
            )
        elif (
            target_phase == WorkflowPhase.FRONTEND_GENERATION.value
            and not shared_state.get("api_spec")
        ):
            return "❌ Cannot transition to frontend generation: API specification required"

    # Update workflow state
    shared_state["current_phase"] = target_phase
    shared_state["workflow_status"] = WorkflowStatus.IN_PROGRESS.value
    shared_state["last_phase_update"] = datetime.now().isoformat()
    shared_state["phase_history"] = shared_state.get("phase_history", []) + [
        {
            "from_phase": current_phase,
            "to_phase": target_phase,
            "timestamp": datetime.now().isoformat(),
            "transition_type": "automatic" if not validation_required else "validated",
        }
    ]

    return f"✅ Workflow transitioned from {current_phase} to {target_phase}"


@tool
def validate_shared_state_integrity(team: Team) -> str:
    """
    Validate the integrity of shared state across all workflow phases.

    Args:
        team: The team calling this tool (automatically passed)

    Returns:
        Validation report with any integrity issues
    """
    shared_state = team.team_session_state
    issues = []

    # Validate project plan
    project_plan = shared_state.get("project_plan")
    if project_plan:
        if not isinstance(project_plan, dict):
            issues.append("Project plan is not a valid dictionary")
        else:
            required_fields = ["project_name", "entities", "tech_stack", "auth_policy"]
            for field in required_fields:
                if field not in project_plan:
                    issues.append(f"Project plan missing required field: {field}")

    # Validate API specification
    api_spec = shared_state.get("api_spec")
    if api_spec:
        if not isinstance(api_spec, dict):
            issues.append("API specification is not a valid dictionary")
        else:
            required_fields = ["openapi_spec", "revision", "validation_report"]
            for field in required_fields:
                if field not in api_spec:
                    issues.append(f"API specification missing required field: {field}")

            # Validate OpenAPI spec structure
            openapi_spec = api_spec.get("openapi_spec", {})
            if not openapi_spec.get("openapi", "").startswith("3.1"):
                issues.append("OpenAPI specification version is not 3.1.x")

    # Validate backend report
    backend_report = shared_state.get("backend_report")
    if backend_report:
        if not isinstance(backend_report, dict):
            issues.append("Backend report is not a valid dictionary")
        else:
            required_fields = ["implemented_endpoints", "compliance_status"]
            for field in required_fields:
                if field not in backend_report:
                    issues.append(f"Backend report missing required field: {field}")

    # Validate frontend report
    frontend_report = shared_state.get("frontend_report")
    if frontend_report:
        if not isinstance(frontend_report, dict):
            issues.append("Frontend report is not a valid dictionary")
        else:
            required_fields = ["implemented_components", "compliance_status"]
            for field in required_fields:
                if field not in frontend_report:
                    issues.append(f"Frontend report missing required field: {field}")

    # Generate report
    if issues:
        report = "❌ Shared State Integrity Issues Found:\n"
        for i, issue in enumerate(issues, 1):
            report += f"  {i}. {issue}\n"
        return report
    else:
        return "✅ Shared state integrity validation passed - no issues found"


@tool
def handle_workflow_error(
    team: Team, error_type: str, error_message: str, recovery_action: str = "retry"
) -> str:
    """
    Handle workflow errors and coordinate recovery actions.

    Args:
        team: The team calling this tool (automatically passed)
        error_type: Type of error (validation_failure, agent_error, state_corruption)
        error_message: Detailed error message
        recovery_action: Recovery action to take (retry, regenerate, rollback)

    Returns:
        Recovery action status and next steps
    """
    shared_state = team.team_session_state
    current_phase = shared_state.get("current_phase", WorkflowPhase.PLANNING.value)

    # Log error
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": current_phase,
        "error_type": error_type,
        "error_message": error_message,
        "recovery_action": recovery_action,
    }

    error_history = shared_state.get("error_history", [])
    error_history.append(error_entry)
    shared_state["error_history"] = error_history

    # Set error state
    shared_state["workflow_status"] = WorkflowStatus.FAILED.value
    shared_state["last_error"] = error_entry

    # Determine recovery strategy
    recovery_message = f"❌ Workflow Error in {current_phase}:\n"
    recovery_message += f"Error Type: {error_type}\n"
    recovery_message += f"Message: {error_message}\n\n"

    if recovery_action == "retry":
        recovery_message += "🔄 Recovery Action: Retry current phase\n"
        recovery_message += "Next Step: Re-execute current phase agent with same inputs"

    elif recovery_action == "regenerate":
        if error_type == "validation_failure":
            # Go back to spec generation for contract issues
            shared_state["current_phase"] = WorkflowPhase.SPEC_GENERATION.value
            recovery_message += "🔄 Recovery Action: Regenerate API specification\n"
            recovery_message += (
                "Next Step: ApiSpecGenerator will create new specification"
            )
        else:
            # Go back to planning for major issues
            shared_state["current_phase"] = WorkflowPhase.PLANNING.value
            recovery_message += "🔄 Recovery Action: Regenerate from planning phase\n"
            recovery_message += "Next Step: Planner will create updated project plan"

    elif recovery_action == "rollback":
        # Find last successful phase
        phase_history = shared_state.get("phase_history", [])
        if phase_history:
            last_successful = (
                phase_history[-2] if len(phase_history) > 1 else phase_history[-1]
            )
            shared_state["current_phase"] = last_successful["from_phase"]
            recovery_message += (
                f"🔄 Recovery Action: Rollback to {last_successful['from_phase']}\n"
            )
            recovery_message += "Next Step: Resume from last successful phase"
        else:
            shared_state["current_phase"] = WorkflowPhase.PLANNING.value
            recovery_message += "🔄 Recovery Action: Rollback to planning phase\n"
            recovery_message += "Next Step: Start workflow from beginning"

    return recovery_message


@tool
def coordinate_agent_handoff(
    team: Team, from_agent: str, to_agent: str, handoff_data: str = None
) -> str:
    """
    Coordinate handoff between agents with data validation.

    Args:
        team: The team calling this tool (automatically passed)
        from_agent: Name of agent completing their task
        to_agent: Name of agent to receive handoff
        handoff_data: Optional data to pass between agents

    Returns:
        Handoff coordination status
    """
    shared_state = team.team_session_state

    # Log handoff
    handoff_entry = {
        "timestamp": datetime.now().isoformat(),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "phase": shared_state.get("current_phase", "unknown"),
        "data_included": handoff_data is not None,
    }

    handoff_history = shared_state.get("handoff_history", [])
    handoff_history.append(handoff_entry)
    shared_state["handoff_history"] = handoff_history

    # Validate handoff data if provided
    if handoff_data:
        validation_result = JSONValidator.validate_json_string(handoff_data)
        if not validation_result["valid"]:
            return f"❌ Handoff failed: Invalid JSON data from {from_agent}"

    # Update workflow status
    shared_state["last_handoff"] = handoff_entry
    shared_state["workflow_status"] = WorkflowStatus.IN_PROGRESS.value

    return f"✅ Agent handoff completed: {from_agent} → {to_agent}"


@tool
def manage_api_spec_revision(team: Team, change_type: str, description: str) -> str:
    """
    Manage API specification revision updates with team coordination.

    Args:
        team: The team calling this tool (automatically passed)
        change_type: Type of change (major, minor, patch, planner_regen, spec_regen)
        description: Description of the change

    Returns:
        Revision management status
    """
    shared_state = team.team_session_state
    api_spec = shared_state.get("api_spec")

    if not api_spec:
        return "❌ Cannot manage revision: No API specification in shared state"

    current_revision = api_spec.get("revision", "1.0.0")
    new_revision = RevisionManager.increment_version(current_revision, change_type)

    # Update API spec with new revision
    api_spec["revision"] = new_revision
    api_spec["updated_at"] = datetime.now().isoformat()
    api_spec["change_description"] = description

    # Create revision metadata
    revision_metadata = RevisionManager.create_revision_metadata(
        "ContractFirstOrchestrator", change_type, description
    )

    # Update shared state
    shared_state["api_spec"] = api_spec
    shared_state["api_spec_revision"] = new_revision

    # Add to revision history
    revision_history = shared_state.get("api_spec_history", [])
    revision_history.append(revision_metadata)
    shared_state["api_spec_history"] = revision_history

    # Trigger regeneration if needed
    if change_type in ["major", "planner_regen"]:
        shared_state["current_phase"] = WorkflowPhase.PLANNING.value
        regeneration_msg = (
            "🔄 Major revision triggered - workflow reset to planning phase"
        )
    elif change_type in ["minor", "spec_regen"]:
        shared_state["current_phase"] = WorkflowPhase.SPEC_GENERATION.value
        regeneration_msg = (
            "🔄 Minor revision triggered - workflow reset to spec generation phase"
        )
    else:
        regeneration_msg = "📝 Patch revision - no workflow reset required"

    return (
        f"✅ API specification updated to revision {new_revision}\n{regeneration_msg}"
    )


def create_contract_first_orchestrator() -> Team:
    """
    Create the contract-first orchestrator team with all agents and workflow management.

    Returns:
        Configured Team instance with contract-first workflow capabilities
    """

    # Create memory with SQLite database for persistent conversational history
    memory_db = SqliteMemoryDb(
        table_name="contract_first_memory", db_file="contract_first_memory.db"
    )
    memory = Memory(db=memory_db)

    # Create the contract-first development team
    contract_first_team = Team(
        name="Contract-First Development Team",
        team_id="contract_first_team",
        model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
        # Team members in workflow order
        members=[
            planner_agent,
            api_spec_generator_agent,
            backend_agent,
            frontend_agent,
        ],
        # Memory configuration for persistent conversational history
        memory=memory,
        add_history_to_messages=True,
        num_history_runs=5,
        enable_user_memories=True,
        enable_session_summaries=True,
        enable_agentic_memory=True,
        # Enhanced shared team state for contract-first workflow
        team_session_state={
            # Core contract data
            "project_plan": {},
            "api_spec": {},
            "backend_report": {},
            "frontend_report": {},
            # Workflow management
            "current_phase": WorkflowPhase.PLANNING.value,
            "workflow_status": WorkflowStatus.INITIALIZED.value,
            "last_phase_update": datetime.now().isoformat(),
            # Revision management
            "api_spec_revision": "1.0.0",
            "api_spec_history": [],
            # Error handling and recovery
            "error_history": [],
            "last_error": None,
            # Agent coordination
            "handoff_history": [],
            "last_handoff": None,
            "phase_history": [],
            # Validation tracking
            "validation_reports": [],
            "contract_compliance_status": "pending",
        },
        # Contract-first workflow coordination tools
        tools=[
            get_workflow_status,
            transition_workflow_phase,
            validate_shared_state_integrity,
            handle_workflow_error,
            coordinate_agent_handoff,
            manage_api_spec_revision,
            get_shared_state_summary,
        ],
        # Team coordination mode
        mode="coordinate",
        # Contract-first orchestrator instructions
        instructions=[
            "You are the Contract-First Orchestrator, managing a lean multi-agent system with strict workflow control.",
            "",
            "WORKFLOW STATE MACHINE (STRICT ORDER):",
            "1. PLANNING → Planner Agent creates project_plan",
            "2. SPEC_GENERATION → ApiSpecGenerator creates api_spec from project_plan",
            "3. BACKEND_GENERATION → Backend Agent creates backend code from api_spec",
            "4. FRONTEND_GENERATION → Frontend Agent creates frontend code from api_spec",
            "5. VALIDATION → Validate contract compliance (future iteration)",
            "6. COMPLETED → Workflow finished successfully",
            "",
            "ORCHESTRATION RESPONSIBILITIES:",
            "- Use get_workflow_status() to check current phase and completion status",
            "- Use transition_workflow_phase() to move between phases with validation",
            "- Use coordinate_agent_handoff() when agents complete their tasks",
            "- Use validate_shared_state_integrity() to ensure data consistency",
            "- Use handle_workflow_error() for error recovery and regeneration",
            "",
            "AGENT COORDINATION RULES:",
            "- Each agent ONLY accesses their designated input/output keys",
            "- Planner: Input=user_request, Output=project_plan",
            "- ApiSpecGenerator: Input=project_plan, Output=api_spec",
            "- Backend: Input=api_spec, Output=backend_report + code artifacts",
            "- Frontend: Input=api_spec, Output=frontend_report + code artifacts",
            "",
            "CONTRACT COMPLIANCE ENFORCEMENT:",
            "- ALL agents must output valid JSON only (no markdown, comments)",
            "- API specification is the single source of truth for Backend/Frontend",
            "- Use manage_api_spec_revision() for specification updates",
            "- Trigger regeneration when contract drift is detected",
            "",
            "ERROR RECOVERY STRATEGIES:",
            "- Validation failures → Regenerate API specification",
            "- Agent errors → Retry current phase",
            "- State corruption → Rollback to last successful phase",
            "- Contract drift → Major revision and workflow reset",
            "",
            "SHARED STATE MANAGEMENT:",
            "- Validate shared state integrity before each phase transition",
            "- Maintain revision history for all API specification changes",
            "- Log all agent handoffs and phase transitions",
            "- Ensure proper cleanup and state consistency",
            "",
            "WORKFLOW EXECUTION:",
            "- Always start with get_workflow_status() to understand current state",
            "- Coordinate one agent at a time in strict phase order",
            "- Validate prerequisites before each phase transition",
            "- Handle errors gracefully with appropriate recovery actions",
            "- Provide clear status updates and next steps to users",
        ],
        show_tool_calls=True,
        show_members_responses=True,
    )

    return contract_first_team


# Orchestrator execution functions
def execute_contract_first_workflow(user_request: str) -> Team:
    """
    Execute the complete contract-first workflow from user request to generated code.

    Args:
        user_request: User's requirements for the application

    Returns:
        Team instance with completed workflow state
    """
    print("🚀 Starting Contract-First Development Workflow")
    print("=" * 60)

    # Create the orchestrator team
    team = create_contract_first_orchestrator()

    # Store user request in shared state
    team.team_session_state["user_request"] = user_request
    team.team_session_state["workflow_started"] = datetime.now().isoformat()

    print(f"📋 User Request: {user_request}")
    print()

    # Execute workflow phases
    workflow_prompt = f"""
    Execute the contract-first workflow for the following user request:
    "{user_request}"
    
    Follow the strict workflow phases:
    1. Check current workflow status
    2. Execute Planning phase (Planner Agent)
    3. Execute Spec Generation phase (ApiSpecGenerator Agent)
    4. Execute Backend Generation phase (Backend Agent)
    5. Execute Frontend Generation phase (Frontend Agent)
    6. Complete workflow with final validation
    
    Use the workflow management tools to coordinate each phase transition
    and ensure proper agent handoffs with shared state validation.
    """

    team.print_response(workflow_prompt, stream=True)

    print(f"\n🎉 Contract-First Workflow Complete!")
    return team


def interactive_contract_first_mode():
    """
    Run the contract-first orchestrator in interactive mode.
    """
    print("🤖 Contract-First Development Team - Interactive Mode")
    print("=" * 60)
    print("Available commands:")
    print("  /status - Check workflow status and phase")
    print("  /plan <requirements> - Start planning phase")
    print("  /spec - Generate API specification")
    print("  /backend - Generate backend code")
    print("  /frontend - Generate frontend code")
    print("  /validate - Validate shared state integrity")
    print("  /reset - Reset workflow to planning phase")
    print("  /workflow <requirements> - Run complete workflow")
    print("  /quit - Exit")
    print()

    team = create_contract_first_orchestrator()

    while True:
        try:
            user_input = input("\n💬 Enter command or message: ").strip()

            if user_input == "/quit":
                print("👋 Goodbye!")
                break
            elif user_input == "/status":
                team.print_response(
                    "Use get_workflow_status() to show current workflow state",
                    stream=True,
                )
            elif user_input.startswith("/plan "):
                requirements = user_input[6:]
                team.team_session_state["user_request"] = requirements
                team.print_response(
                    f"Execute planning phase for: {requirements}", stream=True
                )
            elif user_input == "/spec":
                team.print_response(
                    "Execute API specification generation phase", stream=True
                )
            elif user_input == "/backend":
                team.print_response(
                    "Execute backend code generation phase", stream=True
                )
            elif user_input == "/frontend":
                team.print_response(
                    "Execute frontend code generation phase", stream=True
                )
            elif user_input == "/validate":
                team.print_response(
                    "Use validate_shared_state_integrity() to check state consistency",
                    stream=True,
                )
            elif user_input == "/reset":
                team.print_response(
                    "Use transition_workflow_phase() to reset to planning phase",
                    stream=True,
                )
            elif user_input.startswith("/workflow "):
                requirements = user_input[10:]
                return execute_contract_first_workflow(requirements)
            else:
                # Natural language processing with workflow awareness
                enhanced_prompt = f"""
                Process this request in the context of the contract-first workflow:
                "{user_input}"
                
                1. Use get_workflow_status() to understand current phase
                2. Determine appropriate action based on current workflow state
                3. Coordinate with appropriate team members if needed
                4. Use workflow management tools for phase transitions
                """
                team.print_response(enhanced_prompt, stream=True)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


# Create the orchestrator instance for export
contract_first_orchestrator = create_contract_first_orchestrator()


def create_contract_first_playground():
    """Create playground with individual agents and the contract-first development team."""

    print("🔧 Creating contract-first development team...")
    dev_team = create_contract_first_orchestrator()

    print("✅ Setting up playground with agents and team...")

    # Create playground with both individual agents and team
    playground = Playground(
        agents=[planner_agent, api_spec_generator_agent, backend_agent, frontend_agent],
        teams=[dev_team],
        name="Contract-First Development Playground",
        description="""Interactive playground for testing contract-first workflow:
• Individual agents (Planner, ApiSpecGenerator, Backend, Frontend)
• Contract-First Development Team orchestrator
• Workflow state machine with phase transitions
• Shared state management and contract compliance
• Team coordination and artifact generation""",
    )

    return playground


def main():
    """Main function to start the contract-first playground server."""

    print("🚀 Starting Contract-First Development Playground")
    print("=" * 60)
    print("📋 Features:")
    print("  • Test individual agents separately")
    print("  • Test contract-first team orchestrator coordination")
    print("  • Workflow state machine (Planning → Spec → Backend → Frontend)")
    print("  • Generate and save code artifacts with contract compliance")
    print("  • Memory persistence across sessions")
    print("  • Shared state management and validation")
    print("=" * 60)

    try:
        # Create the playground
        playground = create_contract_first_playground()

        # Get the FastAPI app
        app = playground.get_app()

        print("✅ Contract-first playground created successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser to: http://localhost:7777")
        print("💡 Try commands like:")
        print("   - 'Create a todo app with user authentication'")
        print("   - '/workflow Build a blog website with comments'")
        print("   - '/status - Check workflow status'")
        print("   - '/plan <requirements> - Start planning phase'")
        print("=" * 60)

        # Start the server
        playground.serve(
            app="contract_first_orchestrator:app",
            host="0.0.0.0",
            port=7777,
            reload=True,
        )

    except Exception as e:
        print(f"❌ Error starting contract-first playground: {e}")
        raise


# Create the app instance for uvicorn
contract_first_playground_instance = create_contract_first_playground()
app = contract_first_playground_instance.get_app()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--playground":
            # Run playground mode
            main()
        else:
            # Run with requirements from command line
            requirements = " ".join(sys.argv[1:])
            execute_contract_first_workflow(requirements)
    else:
        # Default to playground mode
        main()
