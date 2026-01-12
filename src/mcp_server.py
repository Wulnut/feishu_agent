import json
from mcp.server.fastmcp import FastMCP
from src.providers.project.manager import ProjectManager

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
    manager = ProjectManager(project_key)
    tasks = await manager.get_active_tasks()
    return str(tasks)


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

    manager = ProjectManager(project_key)
    try:
        task_id = await manager.create_task(name, type_key, extra_fields=fields_dict)
        return f"Successfully created task. ID: {task_id}"
    except Exception as e:
        return f"Error creating task: {str(e)}"
