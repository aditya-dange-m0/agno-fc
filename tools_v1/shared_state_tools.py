"""
Contract-First Shared State Management Tools
==========================================

This module provides tools for managing shared state in the contract-first multi-agent system.
It includes JSON validation utilities, revision management, and state management for all agents.

Following the existing pattern from planner_agent.py but enhanced for contract-first workflow.
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from agno.agent import Agent
from agno.tools import tool


# JSON Validation Utilities
class JSONValidator:
    """Utility class for validating agent JSON outputs"""
    
    @staticmethod
    def validate_json_string(json_string: str) -> Dict[str, Any]:
        """
        Validate that a string is valid JSON and return parsed object.
        
        Args:
            json_string: String to validate as JSON
            
        Returns:
            Dict containing validation result and parsed data
        """
        try:
            parsed_data = json.loads(json_string)
            return {
                "valid": True,
                "data": parsed_data,
                "error": None
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "data": None,
                "error": f"Invalid JSON: {str(e)}"
            }
    
    @staticmethod
    def validate_against_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema to validate against
            
        Returns:
            Dict containing validation result
        """
        try:
            jsonschema.validate(data, schema)
            return {
                "valid": True,
                "errors": []
            }
        except jsonschema.ValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }
        except jsonschema.SchemaError as e:
            return {
                "valid": False,
                "errors": [f"Schema error: {str(e)}"]
            }
    
    @staticmethod
    def has_markdown_or_comments(text: str) -> bool:
        """
        Check if text contains markdown formatting or comments.
        
        Args:
            text: Text to check
            
        Returns:
            True if markdown or comments found, False otherwise
        """
        markdown_indicators = [
            "```", "##", "**", "*", "_", "[", "]", "<!--", "//", "#"
        ]
        
        # Check for markdown indicators
        for indicator in markdown_indicators:
            if indicator in text:
                return True
        
        # Check if it starts with non-JSON content
        stripped = text.strip()
        if not (stripped.startswith("{") or stripped.startswith("[")):
            return True
            
        return False


# Revision Management Utilities
class RevisionManager:
    """Utility class for managing API specification versioning"""
    
    @staticmethod
    def parse_version(version: str) -> Dict[str, int]:
        """
        Parse semantic version string into components.
        
        Args:
            version: Version string (e.g., "1.2.3")
            
        Returns:
            Dict with major, minor, patch components
        """
        try:
            parts = version.split(".")
            return {
                "major": int(parts[0]),
                "minor": int(parts[1]) if len(parts) > 1 else 0,
                "patch": int(parts[2]) if len(parts) > 2 else 0
            }
        except (ValueError, IndexError):
            return {"major": 1, "minor": 0, "patch": 0}
    
    @staticmethod
    def increment_version(current_version: str, change_type: str) -> str:
        """
        Increment version based on change type.
        
        Args:
            current_version: Current version string
            change_type: Type of change (major, minor, patch)
            
        Returns:
            New version string
        """
        version_parts = RevisionManager.parse_version(current_version)
        
        if change_type == "major" or change_type == "planner_regen":
            version_parts["major"] += 1
            version_parts["minor"] = 0
            version_parts["patch"] = 0
        elif change_type == "minor" or change_type == "spec_regen":
            version_parts["minor"] += 1
            version_parts["patch"] = 0
        else:  # patch or bug_fix
            version_parts["patch"] += 1
        
        return f"{version_parts['major']}.{version_parts['minor']}.{version_parts['patch']}"
    
    @staticmethod
    def create_revision_metadata(agent_name: str, change_type: str, description: str) -> Dict[str, Any]:
        """
        Create revision metadata for tracking changes.
        
        Args:
            agent_name: Name of agent making the change
            change_type: Type of change being made
            description: Description of the change
            
        Returns:
            Revision metadata dict
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "change_type": change_type,
            "description": description,
            "revision_id": f"{agent_name}_{int(datetime.now().timestamp())}"
        }


# Project Plan Management Tools
def _update_project_plan_core(agent: Agent, plan_data: str) -> str:
    """
    Update the project_plan in shared team state with JSON validation.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        plan_data: The project plan data as JSON string
        
    Returns:
        Status message indicating success or failure
    """
    # Validate JSON format
    validation_result = JSONValidator.validate_json_string(plan_data)
    
    if not validation_result["valid"]:
        return f"❌ Invalid JSON in project plan: {validation_result['error']}"
    
    # Check for markdown or comments
    if JSONValidator.has_markdown_or_comments(plan_data):
        return "❌ Project plan contains markdown or comments. JSON only required."
    
    # Store in shared state
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        agent.team_session_state["project_plan"] = validation_result["data"]
        agent.team_session_state["project_plan_updated"] = datetime.now().isoformat()
        agent.team_session_state["project_plan_agent"] = agent.name
        return "✅ Project plan updated successfully in shared team state"
    else:
        return f"📋 Project plan validated: {str(validation_result['data'])[:100]}..."


def _get_project_plan_core(agent: Agent) -> str:
    """
    Get the current project_plan from shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        
    Returns:
        Current project plan as JSON string or error message
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        plan = agent.team_session_state.get("project_plan", None)
        if plan:
            return json.dumps(plan, indent=2)
        else:
            return "❌ No project plan available in shared state"
    else:
        return "❌ No team session state available"


@tool
def update_project_plan(agent: Agent, plan_data: str) -> str:
    """
    Update the project_plan in shared team state with JSON validation.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        plan_data: The project plan data as JSON string
        
    Returns:
        Status message indicating success or failure
    """
    return _update_project_plan_core(agent, plan_data)


@tool
def get_project_plan(agent: Agent) -> str:
    """
    Get the current project_plan from shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        
    Returns:
        Current project plan as JSON string or error message
    """
    return _get_project_plan_core(agent)


# API Specification Management Tools
@tool
def update_api_spec(agent: Agent, spec_data: str, revision_type: str = "minor") -> str:
    """
    Update the api_spec in shared team state with validation and revision management.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        spec_data: The API specification data as JSON string
        revision_type: Type of revision (major, minor, patch)
        
    Returns:
        Status message indicating success or failure
    """
    # Validate JSON format
    validation_result = JSONValidator.validate_json_string(spec_data)
    
    if not validation_result["valid"]:
        return f"❌ Invalid JSON in API specification: {validation_result['error']}"
    
    # Check for markdown or comments
    if JSONValidator.has_markdown_or_comments(spec_data):
        return "❌ API specification contains markdown or comments. JSON only required."
    
    spec_dict = validation_result["data"]
    
    # Handle revision management
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        current_spec = agent.team_session_state.get("api_spec", {})
        current_revision = current_spec.get("revision", "1.0.0")
        
        # Increment revision
        new_revision = RevisionManager.increment_version(current_revision, revision_type)
        
        # Add revision metadata
        spec_dict["revision"] = new_revision
        spec_dict["generated_by"] = agent.name
        spec_dict["updated_at"] = datetime.now().isoformat()
        
        # Create revision history entry
        revision_metadata = RevisionManager.create_revision_metadata(
            agent.name, revision_type, f"API specification updated to v{new_revision}"
        )
        
        # Store in shared state
        agent.team_session_state["api_spec"] = spec_dict
        agent.team_session_state["api_spec_revision"] = new_revision
        agent.team_session_state["api_spec_history"] = agent.team_session_state.get("api_spec_history", []) + [revision_metadata]
        
        return f"✅ API specification updated to revision {new_revision} in shared team state"
    else:
        return f"📋 API specification validated: revision {spec_dict.get('revision', 'unknown')}"
    
    if team_state:
        current_spec = team_state.get("api_spec", {})
        current_revision = current_spec.get("revision", "1.0.0")
        
        # Increment revision
        new_revision = RevisionManager.increment_version(current_revision, revision_type)
        
        # Add revision metadata
        spec_dict["revision"] = new_revision
        spec_dict["generated_by"] = agent_name
        spec_dict["updated_at"] = datetime.now().isoformat()
        
        # Create revision history entry
        revision_metadata = RevisionManager.create_revision_metadata(
            agent_name, revision_type, f"API specification updated to v{new_revision}"
        )
        
        # Store in shared state
        team_state["api_spec"] = spec_dict
        team_state["api_spec_revision"] = new_revision
        team_state["api_spec_history"] = team_state.get("api_spec_history", []) + [revision_metadata]
        
        return f"✅ API specification updated to revision {new_revision} in shared team state"
    else:
        return f"📋 API specification validated: revision {spec_dict.get('revision', 'unknown')}"


@tool
def get_api_spec(agent: Agent) -> str:
    """
    Get the current api_spec from shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        
    Returns:
        Current API specification as JSON string or error message
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        spec = agent.team_session_state.get("api_spec", None)
        if spec:
            return json.dumps(spec, indent=2)
        else:
            return "❌ No API specification available in shared state"
    else:
        return "❌ No team session state available"


@tool
def get_api_spec_revision_history(agent: Agent) -> str:
    """
    Get the revision history for the API specification.
    
    Args:
        Agent: The agent or team calling this tool (automatically passed)
        
    Returns:
        Revision history as formatted string
    """
    team_state = None
    
    if hasattr(Agent, 'team_session_state') and Agent.team_session_state:
        team_state = Agent.team_session_state
    
    if team_state:
        history = team_state.get("api_spec_history", [])
        if history:
            formatted_history = "📋 API Specification Revision History:\n"
            for entry in history[-5:]:  # Show last 5 revisions
                formatted_history += f"  - {entry['timestamp']}: {entry['description']} (by {entry['agent']})\n"
            return formatted_history
        else:
            return "📋 No revision history available"
    else:
        return "❌ No team session state available"


# Backend Report Management Tools
@tool
def update_backend_report(agent: Agent, report_data: str) -> str:
    """
    Update the backend_report in shared team state with JSON validation.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        report_data: The backend report data as JSON string
        
    Returns:
        Status message indicating success or failure
    """
    # Validate JSON format
    validation_result = JSONValidator.validate_json_string(report_data)
    
    if not validation_result["valid"]:
        return f"❌ Invalid JSON in backend report: {validation_result['error']}"
    
    # Check for markdown or comments
    if JSONValidator.has_markdown_or_comments(report_data):
        return "❌ Backend report contains markdown or comments. JSON only required."
    
    # Store in shared state
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        report_dict = validation_result["data"]
        report_dict["updated_at"] = datetime.now().isoformat()
        report_dict["updated_by"] = agent.name
        
        agent.team_session_state["backend_report"] = report_dict
        return "✅ Backend report updated successfully in shared team state"
    else:
        return f"📋 Backend report validated: {str(validation_result['data'])[:100]}..."


@tool
def get_backend_report(agent: Agent) -> str:
    """
    Get the current backend_report from shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        
    Returns:
        Current backend report as JSON string or error message
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        report = agent.team_session_state.get("backend_report", None)
        if report:
            return json.dumps(report, indent=2)
        else:
            return "❌ No backend report available in shared state"
    else:
        return "❌ No team session state available"


# Frontend Report Management Tools
@tool
def update_frontend_report(agent: Agent, report_data: str) -> str:
    """
    Update the frontend_report in shared team state with JSON validation.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        report_data: The frontend report data as JSON string
        
    Returns:
        Status message indicating success or failure
    """
    # Validate JSON format
    validation_result = JSONValidator.validate_json_string(report_data)
    
    if not validation_result["valid"]:
        return f"❌ Invalid JSON in frontend report: {validation_result['error']}"
    
    # Check for markdown or comments
    if JSONValidator.has_markdown_or_comments(report_data):
        return "❌ Frontend report contains markdown or comments. JSON only required."
    
    # Store in shared state
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        report_dict = validation_result["data"]
        report_dict["updated_at"] = datetime.now().isoformat()
        report_dict["updated_by"] = agent.name
        
        agent.team_session_state["frontend_report"] = report_dict
        return "✅ Frontend report updated successfully in shared team state"
    else:
        return f"📋 Frontend report validated: {str(validation_result['data'])[:100]}..."


@tool
def get_frontend_report(agent: Agent) -> str:
    """
    Get the current frontend_report from shared team state.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        
    Returns:
        Current frontend report as JSON string or error message
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        report = agent.team_session_state.get("frontend_report", None)
        if report:
            return json.dumps(report, indent=2)
        else:
            return "❌ No frontend report available in shared state"
    else:
        return "❌ No team session state available"


# Validation Utilities
@tool
def validate_agent_json_output(agent: Agent, output_text: str, expected_schema: str = None) -> str:
    """
    Validate that agent output is valid JSON without markdown or comments.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        output_text: The output text to validate
        expected_schema: Optional JSON schema to validate against
        
    Returns:
        Validation result message
    """
    # Check for markdown or comments first
    if JSONValidator.has_markdown_or_comments(output_text):
        return "❌ Output contains markdown or comments. JSON only required."
    
    # Validate JSON format
    validation_result = JSONValidator.validate_json_string(output_text)
    
    if not validation_result["valid"]:
        return f"❌ Invalid JSON output: {validation_result['error']}"
    
    # Validate against schema if provided
    if expected_schema:
        try:
            schema_dict = json.loads(expected_schema)
            schema_validation = JSONValidator.validate_against_schema(
                validation_result["data"], schema_dict
            )
            if not schema_validation["valid"]:
                return f"❌ Schema validation failed: {'; '.join(schema_validation['errors'])}"
        except json.JSONDecodeError:
            return "❌ Invalid schema provided for validation"
    
    return "✅ Valid JSON output - no markdown or comments detected"


# Shared State Integrity Tools
@tool
def get_shared_state_summary(agent: Agent) -> str:
    """
    Get a summary of all shared state keys and their status.
    
    Args:
        agent: The agent calling this tool (automatically passed)
        
    Returns:
        Summary of shared state
    """
    if hasattr(agent, 'team_session_state') and agent.team_session_state:
        state = agent.team_session_state
        
        summary = "📊 Shared State Summary:\n"
        summary += "=" * 30 + "\n"
        
        # Project Plan
        plan_status = "✅ Available" if state.get("project_plan") else "❌ Missing"
        summary += f"Project Plan: {plan_status}\n"
        
        # API Specification
        spec_status = "✅ Available" if state.get("api_spec") else "❌ Missing"
        spec_revision = state.get("api_spec_revision", "Unknown")
        summary += f"API Specification: {spec_status} (v{spec_revision})\n"
        
        # Backend Report
        backend_status = "✅ Available" if state.get("backend_report") else "❌ Missing"
        summary += f"Backend Report: {backend_status}\n"
        
        # Frontend Report
        frontend_status = "✅ Available" if state.get("frontend_report") else "❌ Missing"
        summary += f"Frontend Report: {frontend_status}\n"
        
        # Revision History
        history_count = len(state.get("api_spec_history", []))
        summary += f"Revision History: {history_count} entries\n"
        
        return summary
    else:
        return "❌ No team session state available"


# Export all tools for easy import
CONTRACT_FIRST_TOOLS = [
    update_project_plan,
    get_project_plan,
    update_api_spec,
    get_api_spec,
    get_api_spec_revision_history,
    update_backend_report,
    get_backend_report,
    update_frontend_report,
    get_frontend_report,
    validate_agent_json_output,
    get_shared_state_summary
]