import httpx
from typing import Optional
from src.core.config import settings

_project_client = None


class ProjectClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.FEISHU_PROJECT_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "X-PLUGIN-TOKEN": settings.FEISHU_PROJECT_USER_TOKEN or "",
            "X-USER-KEY": settings.FEISHU_PROJECT_USER_KEY or "",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)

    async def post(self, path: str, json: Optional[dict] = None):
        return await self.client.post(path, json=json)

    async def get(self, path: str, params: Optional[dict] = None):
        return await self.client.get(path, params=params)


def get_project_client():
    global _project_client
    if not _project_client:
        _project_client = ProjectClient()
    return _project_client
