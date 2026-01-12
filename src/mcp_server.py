import json
from mcp.server.fastmcp import FastMCP
from src.services.issue_service import IssueService

# Initialize FastMCP server
mcp = FastMCP("Feishu Agent")


@mcp.tool()
async def get_active_tasks(project_key: str) -> str:
    """
    Get active tasks (status='in_progress') for a given project key.

    Args:
        project_key: The unique key of the Feishu Project.

    Returns:
        A JSON string representation of the active tasks (id, name, type).
    """
    # 暂时占位，IssueService 尚未实现 filter
    return "Not implemented yet. Please check IssueService."


@mcp.tool()
async def create_task(
    project_key: str,
    name: str,
    type_key: str = "task",
    extra_fields: str = "{}",
) -> str:
    """
    Create a new task in the specified project.

    Args:
        project_key: The unique key of the Feishu Project.
        name: The title/name of the task.
        type_key: The type of work item (default: "task"). Options: "task", "bug", "story".
        extra_fields: A JSON string of additional fields (e.g. '{"Priority": "High"}').
                      Human-readable names will be automatically translated.

    Returns:
        The ID of the created task.
    """
    try:
        fields_dict = json.loads(extra_fields)
        if not isinstance(fields_dict, dict):
            return "Error: extra_fields must be a JSON object (dictionary)."
    except Exception:
        return "Error: extra_fields must be a valid JSON string."

    # 使用 Service 层，直接传入 project_key
    service = IssueService(project_key=project_key)
    
    try:
        # Map extra_fields to arguments
        priority = str(fields_dict.get("Priority") or fields_dict.get("priority") or "")
        description = str(fields_dict.get("Description") or fields_dict.get("description") or "")
        assignee = str(fields_dict.get("Assignee") or fields_dict.get("assignee") or "")
        
        if not priority: priority = "P2" # Default
        
        # Service 层的接口更加业务化
        result = await service.create_issue(
            title=name,
            priority=priority,
            description=description,
            assignee=assignee if assignee else None
        )
        return result
    except Exception as e:
        return f"Error creating task: {str(e)}"
