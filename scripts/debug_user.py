import asyncio
import os
from src.core.client import LarkProjectClient
from src.providers.lark_project.managers.metadata_manager import MetadataManager


async def main():
    client = LarkProjectClient()
    meta = MetadataManager(client)
    try:
        user_key = await meta.get_user_key("梁彦泽")
        print(f"User Key for 梁彦泽: {user_key}")

        # Also check projects
        projects = await client.project.list_project()
        for p in projects:
            print(f"Project: {p.get('name')} ({p.get('project_key')})")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
