"""
Bounded AI Agent — LLM06: Excessive Agency

An AI agent with strict permission boundaries, human-in-the-loop approval,
and comprehensive audit logging.
"""

import os
import sys
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class PermissionLevel(Enum):
    """Permission levels for agent actions."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ActionCategory(Enum):
    """Categories of actions the agent can perform."""
    SEARCH = "search"
    SUMMARIZE = "summarize"
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    SEND_EMAIL = "send_email"
    CALL_API = "call_api"
    DELETE_DATA = "delete_data"
    CONFIGURE = "configure"


# Map actions to required permission levels
ACTION_PERMISSIONS = {
    ActionCategory.SEARCH: PermissionLevel.READ,
    ActionCategory.SUMMARIZE: PermissionLevel.READ,
    ActionCategory.CREATE_FILE: PermissionLevel.WRITE,
    ActionCategory.MODIFY_FILE: PermissionLevel.WRITE,
    ActionCategory.DELETE_FILE: PermissionLevel.ADMIN,
    ActionCategory.SEND_EMAIL: PermissionLevel.WRITE,
    ActionCategory.CALL_API: PermissionLevel.ADMIN,
    ActionCategory.DELETE_DATA: PermissionLevel.ADMIN,
    ActionCategory.CONFIGURE: PermissionLevel.ADMIN,
}

# Actions that require human approval
REQUIRES_APPROVAL = {
    ActionCategory.DELETE_FILE,
    ActionCategory.SEND_EMAIL,
    ActionCategory.CALL_API,
    ActionCategory.DELETE_DATA,
    ActionCategory.CONFIGURE,
}


@dataclass
class AuditEntry:
    """A single audit log entry."""
    timestamp: str
    action: str
    requested_by: str
    permission_required: str
    approved: bool
    result: str = ""


@dataclass
class AgentAction:
    """Represents an agent action request."""
    category: ActionCategory
    description: str
    parameters: dict = field(default_factory=dict)


class AuditLogger:
    """Logs all agent actions for accountability."""

    def __init__(self):
        self.entries: list[AuditEntry] = []

    def log(self, action: str, requested_by: str, permission_required: str,
            approved: bool, result: str = ""):
        """Add an audit log entry."""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            requested_by=requested_by,
            permission_required=permission_required,
            approved=approved,
            result=result,
        )
        self.entries.append(entry)

    def print_log(self):
        """Print the audit log."""
        print("\n" + "=" * 70)
        print("AUDIT LOG")
        print("=" * 70)
        for entry in self.entries:
            status = "✓ APPROVED" if entry.approved else "✗ DENIED"
            print(f"  [{entry.timestamp}] {status} — {entry.action}")
            print(f"    Requested by: {entry.requested_by}")
            print(f"    Permission: {entry.permission_required}")
            if entry.result:
                print(f"    Result: {entry.result}")
        print("=" * 70)


class BoundedAgent:
    """
    An AI agent with bounded permissions and human-in-the-loop approval.

    Usage:
        agent = BoundedAgent(permission_level=PermissionLevel.WRITE)
        result = agent.execute("Send an email to the team")
    """

    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ,
                 auto_approve: bool = False):
        """
        Args:
            permission_level: Maximum permission level for this agent.
            auto_approve: If True, skip human approval (for testing).
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("Set OPENAI_API_KEY in your .env file.")
        self.client = OpenAI(api_key=api_key)
        self.permission_level = permission_level
        self.auto_approve = auto_approve
        self.audit_logger = AuditLogger()

    def _parse_intent(self, user_request: str) -> AgentAction | None:
        """
        Parse user request to determine the intended action.
        Uses simple keyword matching for demonstration.
        """
        request_lower = user_request.lower()

        if any(w in request_lower for w in ["delete", "remove", "destroy"]):
            if "file" in request_lower:
                return AgentAction(ActionCategory.DELETE_FILE, f"Delete file: {user_request}")
            elif "data" in request_lower or "record" in request_lower:
                return AgentAction(ActionCategory.DELETE_DATA, f"Delete data: {user_request}")
            else:
                return AgentAction(ActionCategory.DELETE_FILE, f"Delete: {user_request}")

        if "email" in request_lower or "send" in request_lower:
            return AgentAction(ActionCategory.SEND_EMAIL, f"Send email: {user_request}")

        if "api" in request_lower or "call" in request_lower or "request" in request_lower:
            return AgentAction(ActionCategory.CALL_API, f"Call API: {user_request}")

        if "configure" in request_lower or "setting" in request_lower:
            return AgentAction(ActionCategory.CONFIGURE, f"Configure: {user_request}")

        if "create" in request_lower or "write" in request_lower or "new" in request_lower:
            return AgentAction(ActionCategory.CREATE_FILE, f"Create: {user_request}")

        if "modify" in request_lower or "edit" in request_lower or "update" in request_lower:
            return AgentAction(ActionCategory.MODIFY_FILE, f"Modify: {user_request}")

        if "search" in request_lower or "find" in request_lower or "look" in request_lower:
            return AgentAction(ActionCategory.SEARCH, f"Search: {user_request}")

        if "summarize" in request_lower or "summary" in request_lower:
            return AgentAction(ActionCategory.SUMMARIZE, f"Summarize: {user_request}")

        # Default to search/read
        return AgentAction(ActionCategory.SEARCH, f"Search/query: {user_request}")

    def _check_permission(self, action: AgentAction) -> tuple[bool, str]:
        """Check if the agent has permission for the action."""
        required = ACTION_PERMISSIONS.get(action.category, PermissionLevel.ADMIN)

        level_order = {
            PermissionLevel.READ: 1,
            PermissionLevel.WRITE: 2,
            PermissionLevel.ADMIN: 3,
        }

        if level_order[self.permission_level] < level_order[required]:
            return False, (
                f"Insufficient permission. Required: {required.value}, "
                f"Have: {self.permission_level.value}"
            )
        return True, "Permission granted"

    def _get_approval(self, action: AgentAction) -> bool:
        """Get human approval for sensitive actions."""
        if self.auto_approve:
            return True

        print(f"\n⚠ ACTION REQUIRES APPROVAL:")
        print(f"  Action: {action.category.value}")
        print(f"  Description: {action.description}")
        print(f"  Parameters: {action.parameters}")
        print(f"\nApprove this action? (yes/no): ", end="")
        response = input().strip().lower()
        return response in ("yes", "y")

    def execute(self, user_request: str) -> dict:
        """
        Execute a user request with permission checks and approval gates.

        Args:
            user_request: The user's natural language request.

        Returns:
            Dict with action result and audit info.
        """
        # Parse intent
        action = self._parse_intent(user_request)
        if not action:
            return {"error": "Could not understand the request."}

        # Check permission
        permitted, perm_message = self._check_permission(action)
        if not permitted:
            self.audit_logger.log(
                action=action.description,
                requested_by="user",
                permission_required=ACTION_PERMISSIONS[action.category].value,
                approved=False,
                result=f"DENIED: {perm_message}",
            )
            return {
                "action": action.category.value,
                "status": "denied",
                "reason": perm_message,
            }

        # Check if approval is needed
        if action.category in REQUIRES_APPROVAL:
            approved = self._get_approval(action)
            if not approved:
                self.audit_logger.log(
                    action=action.description,
                    requested_by="user",
                    permission_required=ACTION_PERMISSIONS[action.category].value,
                    approved=False,
                    result="Denied by human operator",
                )
                return {
                    "action": action.category.value,
                    "status": "denied",
                    "reason": "Human operator denied the action",
                }

        # Execute the action (simulated)
        result = self._perform_action(action)

        self.audit_logger.log(
            action=action.description,
            requested_by="user",
            permission_required=ACTION_PERMISSIONS[action.category].value,
            approved=True,
            result=result,
        )

        return {
            "action": action.category.value,
            "status": "completed",
            "result": result,
        }

    def _perform_action(self, action: AgentAction) -> str:
        """Simulate performing an action."""
        # In a real system, this would call actual tools/APIs
        action_descriptions = {
            ActionCategory.SEARCH: f"Search completed for: {action.description}",
            ActionCategory.SUMMARIZE: f"Summary generated for: {action.description}",
            ActionCategory.CREATE_FILE: f"File created: {action.description}",
            ActionCategory.MODIFY_FILE: f"File modified: {action.description}",
            ActionCategory.DELETE_FILE: f"File deleted: {action.description}",
            ActionCategory.SEND_EMAIL: f"Email sent: {action.description}",
            ActionCategory.CALL_API: f"API called: {action.description}",
            ActionCategory.DELETE_DATA: f"Data deleted: {action.description}",
            ActionCategory.CONFIGURE: f"Configuration updated: {action.description}",
        }
        return action_descriptions.get(action.category, "Action completed")


def demo_bounded_agent():
    """Demonstrate the bounded agent with various permission levels."""
    print("=" * 70)
    print("LLM06: Bounded AI Agent Demo")
    print("=" * 70)

    # Test with READ permission
    print("\n" + "─" * 50)
    print("Agent with READ permission (auto-approve mode)")
    print("─" * 50)

    read_agent = BoundedAgent(
        permission_level=PermissionLevel.READ,
        auto_approve=True,
    )

    read_tests = [
        "Search for customer records",
        "Summarize the latest report",
        "Delete all user data",
        "Send an email to the CEO",
        "Create a new file",
    ]

    for test in read_tests:
        result = read_agent.execute(test)
        status = "✓" if result["status"] == "completed" else "✗"
        print(f"  {status} '{test}' → {result['status']}: {result.get('reason', result.get('result', ''))}")

    # Test with ADMIN permission
    print("\n" + "─" * 50)
    print("Agent with ADMIN permission (auto-approve mode)")
    print("─" * 50)

    admin_agent = BoundedAgent(
        permission_level=PermissionLevel.ADMIN,
        auto_approve=True,
    )

    for test in read_tests:
        result = admin_agent.execute(test)
        status = "✓" if result["status"] == "completed" else "✗"
        print(f"  {status} '{test}' → {result['status']}: {result.get('reason', result.get('result', ''))}")

    # Print audit logs
    read_agent.audit_logger.print_log()
    admin_agent.audit_logger.print_log()


def main():
    """Run the bounded agent demo."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("Error: Set OPENAI_API_KEY in your .env file.")
        sys.exit(1)

    demo_bounded_agent()


if __name__ == "__main__":
    main()
